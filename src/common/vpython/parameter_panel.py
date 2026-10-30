
"""Reusable, validated numeric parameter controls for VPython applications."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from math import isclose, isfinite
from typing import Callable, Optional

from vpython import button, winput, wtext

Number = float | int


@dataclass(frozen=True)
class Parameter:
    """Numeric parameter descriptor with optional bounds and grouping."""

    name: str
    label: str
    value: float
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    step: Optional[float] = None
    integer: bool = False
    group: Optional[str] = None
    default: Optional[float] = None


class ParameterPanel:
    """Display numeric inputs and pass validated values to one callback."""

    def __init__(
        self,
        title: str,
        parameters: list[Parameter],
        on_apply: Callable[[dict[str, Number]], None],
        pos: object | None = None,
    ) -> None:
        if not parameters:
            raise ValueError("At least one parameter is required.")

        names = [p.name for p in parameters]

        if len(names) != len(set(names)) or any(not name for name in names):
            raise ValueError("Parameter names must be unique and nonempty.")

        self._pos_args = {"pos": pos} if pos is not None else {}
        self.title = title
        self.parameters = list(parameters)
        self.on_apply = on_apply
        self.inputs: dict[str, object] = {}
        self.status: object

        # Validate definitions before creating widgets.
        for param in self.parameters:
            self._validate_definition(param)
            self._validate_value(param, param.value)

            if param.default is not None:
                self._validate_value(param, param.default)

        self._wtext(
            text=f'<h3 style="margin:12px 0">{escape(title)}</h3>'
        )

        current_group: Optional[str] = None

        for param in self.parameters:
            if param.group != current_group and param.group is not None:
                current_group = param.group

                self._wtext(
                    text=(
                        '<h4 style="margin:10px 0 4px">'
                        f'{escape(current_group)}'
                        '</h4>'
                    )
                )

            self._wtext(
                text=f'{escape(param.label)}: &nbsp;'
            )

            # VPython requires bind for every winput.
            self.inputs[param.name] = self._winput(
                prompt="",
                text=str(param.value),
                type="numeric",
                width=120,
                bind=self._handle_input_change,
            )

            self._wtext(text="<br>")

        self._wtext(text="<br>")

        self._button(
            text="APLICAR PARÂMETROS",
            bind=self._handle_apply,
        )

        self._wtext(text=" &nbsp; ")

        self._button(
            text="RESTAURAR PADRÕES",
            bind=self._handle_reset,
        )

        self._wtext(text="<br>")

        self.status = self._wtext(
            text="Parâmetros prontos."
        )

        self._wtext(text="<br>")

    def _wtext(self, **kwargs: object) -> object:
        return wtext(**kwargs, **self._pos_args)

    def _button(self, **kwargs: object) -> object:
        return button(**kwargs, **self._pos_args)

    def _winput(self, **kwargs: object) -> object:
        return winput(**kwargs, **self._pos_args)

    @staticmethod
    def _validate_definition(param: Parameter) -> None:
        for label, value in (
            ("minimum", param.minimum),
            ("maximum", param.maximum),
            ("step", param.step),
        ):
            if value is not None and not isfinite(value):
                raise ValueError(
                    f"{param.label}: {label} must be finite."
                )

        if (
            param.minimum is not None
            and param.maximum is not None
            and param.minimum > param.maximum
        ):
            raise ValueError(
                f"{param.label}: minimum cannot exceed maximum."
            )

        if param.step is not None and param.step <= 0:
            raise ValueError(
                f"{param.label}: step must be positive."
            )

    @staticmethod
    def _validate_value(
        param: Parameter,
        value: Number,
    ) -> None:
        if not isfinite(value):
            raise ValueError(
                f"{param.label} deve ser um número finito."
            )

        if param.minimum is not None and value < param.minimum:
            raise ValueError(
                f"{param.label} deve ser >= {param.minimum}."
            )

        if param.maximum is not None and value > param.maximum:
            raise ValueError(
                f"{param.label} deve ser <= {param.maximum}."
            )

        if param.integer and not float(value).is_integer():
            raise ValueError(
                f"{param.label} deve ser inteiro."
            )

        if param.step is not None:
            origin = (
                param.minimum
                if param.minimum is not None
                else 0.0
            )

            steps = (value - origin) / param.step

            if not isclose(
                steps,
                round(steps),
                rel_tol=1e-10,
                abs_tol=1e-9,
            ):
                raise ValueError(
                    f"{param.label} deve variar em "
                    f"passos de {param.step}."
                )

    def get_values(self) -> dict[str, Number]:
        """Read and validate every input field."""

        result: dict[str, Number] = {}

        for param in self.parameters:
            raw = self.inputs[param.name].text

            try:
                value = float(raw)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Número inválido para {param.label}."
                ) from exc

            self._validate_value(param, value)

            result[param.name] = (
                int(value) if param.integer else value
            )

        return result

    def set_values(
        self,
        values: dict[str, Number],
    ) -> None:
        """Set input fields after validating their values."""

        by_name = {
            param.name: param
            for param in self.parameters
        }

        unknown = values.keys() - by_name.keys()

        if unknown:
            raise ValueError(
                f"Unknown parameters: {', '.join(sorted(unknown))}"
            )

        for name, value in values.items():
            self._validate_value(by_name[name], value)

        for name, value in values.items():
            self.inputs[name].text = str(value)

    def apply(self) -> bool:
        """Apply validated parameters to the simulation."""

        try:
            values = self.get_values()
            self.on_apply(values)

        except (ValueError, TypeError) as exc:
            self.status.text = (
                '<span style="color:#ef5350">Erro: '
                f'{escape(str(exc))}</span>'
            )
            return False

        self.status.text = (
            '<span style="color:#81c784">'
            'Parâmetros aplicados.'
            '</span>'
        )

        return True

    def reset(self) -> bool:
        """Restore default values and apply them."""

        defaults = {
            p.name: (
                p.default
                if p.default is not None
                else p.value
            )
            for p in self.parameters
        }

        self.set_values(defaults)

        return self.apply()

    def _handle_input_change(
        self,
        _event: object,
    ) -> None:
        """Mark edits as pending without applying them."""

        if hasattr(self, "status"):
            self.status.text = (
                "Alterações pendentes. "
                "Clique em APLICAR PARÂMETROS."
            )

    def _handle_apply(
        self,
        _event: object,
    ) -> None:
        self.apply()

    def _handle_reset(
        self,
        _event: object,
    ) -> None:
        self.reset()
