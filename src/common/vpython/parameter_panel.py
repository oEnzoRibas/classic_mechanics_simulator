
"""Reusable, validated parameter controls for VPython applications.

The presentation uses styled wtext sections and native VPython widgets.
Parameter definitions and callbacks remain independent of the simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from math import isclose, isfinite
from typing import Callable, Optional

from vpython import button, color, winput, wtext

Number = float | int


@dataclass(frozen=True)
class Parameter:
    """Define one numeric parameter, its constraints, and its UI group."""

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
    """Display parameter inputs and apply validated values on demand."""

   
    def __init__(
        self,
        title: str,
        parameters: list[Parameter],
        on_apply: Callable[[dict[str, Number]], None],
        pos: object | None = None,
        extra_controls: Callable[[], None] | None = None,
    ) -> None:
        if not parameters:
            raise ValueError("At least one parameter is required.")

        names = [param.name for param in parameters]

        if len(names) != len(set(names)) or not all(names):
            raise ValueError(
                "Parameter names must be unique and non-empty."
            )

        for param in parameters:
            self._validate_definition(param)
            self._validate_value(param, param.value)

            if param.default is not None:
                self._validate_value(param, param.default)

        self._pos_args = {"pos": pos} if pos is not None else {}
        self.title = title
        self.parameters = list(parameters)
        self.on_apply = on_apply
        self.inputs: dict[str, object] = {}

        # Compact panel header

        self._wtext(
            text=(
                '<span style="display:inline-block;'
                'box-sizing:border-box;'
                'width:420px;margin:0 0 2px 12px;'
                'padding:2px 0;'
                'border-bottom:1px solid #cbd5e1;'
                'font:700 14px Arial,sans-serif;'
                'color:#0f172a">'
                f'{escape(title)}'
                '</span><br>'
            )
        )

        current_group: str | None = None

        for param in self.parameters:

            # Section heading

            if param.group != current_group:
                current_group = param.group

                if current_group:
                    self._wtext(
                        text=(
                            '<span style="'
                            'display:inline-block;'
                            'box-sizing:border-box;'
                            'width:420px;'
                            'margin:4px 0 2px 12px;'
                            'padding:3px 8px;'
                            'border-left:3px solid #0d9488;'
                            'background:#eaf3f5;'
                            'color:#115e59;'
                            'font:700 11px Arial,sans-serif">'
                            f'{escape(current_group.upper())}'
                            '</span><br>'
                        )
                    )

            # Parameter label

            self._wtext(
                text=(
                    '<span style="'
                    'display:inline-block;'
                    'box-sizing:border-box;'
                    'width:174px;'
                    'margin-left:12px;'
                    'vertical-align:middle;'
                    'font:500 12px Arial,sans-serif;'
                    'color:#334155">'
                    f'{escape(param.label)}'
                    '</span>'
                )
            )

            # Native numeric input

            self.inputs[param.name] = self._winput(
                prompt="",
                text=str(param.value),
                type="numeric",
                width=106,
                bind=self._handle_input_change,
            )

            # Optional constraints

            hint = self._hint(param)

            if hint:
                self._wtext(
                    text=(
                        '<span style="'
                        'display:inline-block;'
                        'margin-left:8px;'
                        'font:10px Arial,sans-serif;'
                        'color:#64748b">'
                        f'{escape(hint)}'
                        '</span>'
                    )
                )

            self._wtext(text="<br>")

        # Actions

        self._wtext(
            text=(
                '<span style="'
                'display:inline-block;'
                'width:12px">'
                '</span>'
            )
        )

        if extra_controls is not None:
            extra_controls()

        self._button(
            text="APPLY CHANGES",
            bind=self._handle_apply,
            background=color.cyan,
        )

        self._wtext(text="&nbsp;&nbsp;")

        self._button(
            text="RESET DEFAULTS",
            bind=self._handle_reset,
            background=color.gray(0.85),
        )

        self._wtext(text="<br>")

        # Feedback

        self.status = self._wtext(
            text=self._status(
                "Ready — edit the values and click Apply Changes.",
                "#475569",
            )
        )

        self._wtext(text="<br>")

    @staticmethod
    def _status(message: str, accent: str) -> str:
        return (
            '<span style="'
            'display:inline-block;'
            'box-sizing:border-box;'
            'max-width:420px;'
            'margin:5px 0 0 12px;'
            'padding:5px 8px;'
            'background:#f1f5f9;'
            f'border-left:3px solid {accent};'
            'border-radius:4px;'
            'font:11px/1.4 Arial,sans-serif;'
            'color:#334155">'
            f'{escape(message)}'
            '</span>'
        )

    @staticmethod
    def _hint(param: Parameter) -> str:
        """Generate a short description of parameter constraints."""

        hints: list[str] = []

        if param.minimum is not None:
            hints.append(f"Min: {param.minimum:g}")

        if param.maximum is not None:
            hints.append(f"Max: {param.maximum:g}")

        if param.step is not None:
            hints.append(f"Step: {param.step:g}")

        if param.integer:
            hints.append("Integer only")

        return " · ".join(hints)

    def _wtext(self, **kwargs: object) -> object:
        return wtext(**kwargs, **self._pos_args)

    def _button(self, **kwargs: object) -> object:
        return button(**kwargs, **self._pos_args)

    def _winput(self, **kwargs: object) -> object:
        return winput(**kwargs, **self._pos_args)

    # ---------------------------------------------------------
    # UI STYLING
    # ---------------------------------------------------------

    @staticmethod
    def _header_html(title: str) -> str:
        return (
            '<div style="box-sizing:border-box;max-width:740px;'
            'margin:16px 0 14px;padding:16px 18px;'
            'border-radius:12px;border:1px solid #33465f;'
            'background:#17263d;color:#f8fafc;'
            'font-family:Arial,sans-serif">'
            '<div style="font-size:19px;font-weight:700;line-height:1.3">'
            f'&#9881;&nbsp; {escape(title)}</div>'
            '<div style="margin-top:5px;font-size:12px;line-height:1.5;'
            'color:#b9c8da">'
            'Customize the simulation parameters below.'
            '</div></div>'
        )

    @staticmethod
    def _group_html(group: str) -> str:
        return (
            '<div style="box-sizing:border-box;max-width:740px;'
            'margin:16px 0 10px;padding:9px 12px;'
            'border-left:4px solid #0891b2;border-radius:5px;'
            'background:#e8f4fa;color:#164e63;'
            'font:700 13px/1.4 Arial,sans-serif;'
            'letter-spacing:.6px;text-transform:uppercase">'
            f'{escape(group)}</div>'
        )

    @staticmethod
    def _label_html(label: str) -> str:
        return (
            '<span style="display:inline-block;min-width:230px;'
            'padding:7px 12px 7px 3px;vertical-align:middle;'
            'font:600 13px/1.4 Arial,sans-serif;'
            'color:#334155">'
            f'{escape(label)}</span>'
        )

    @staticmethod
    def _hint_html(param: Parameter) -> str:
        hints = []

        if param.minimum is not None:
            hints.append(f"Min: {param.minimum:g}")

        if param.maximum is not None:
            hints.append(f"Max: {param.maximum:g}")

        if param.step is not None:
            hints.append(f"Step: {param.step:g}")

        if param.integer:
            hints.append("Integer")

        if not hints:
            return ""

        return (
            '<span style="display:inline-block;margin-left:12px;'
            'font:11px Arial,sans-serif;color:#64748b">'
            f'{escape(" · ".join(hints))}</span>'
        )

    @staticmethod
    def _status_html(message: str, accent: str) -> str:
        return (
            '<span style="display:inline-block;max-width:740px;'
            'box-sizing:border-box;padding:9px 12px;'
            'border-radius:7px;background:#f1f5f9;'
            'border-left:3px solid '
            f'{accent};color:#334155;'
            'font:12px/1.5 Arial,sans-serif">'
            f'{escape(message)}</span>'
        )

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

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
                f"{param.label} must be a finite number."
            )

        if param.minimum is not None and value < param.minimum:
            raise ValueError(
                f"{param.label} must be at least {param.minimum:g}."
            )

        if param.maximum is not None and value > param.maximum:
            raise ValueError(
                f"{param.label} must be at most {param.maximum:g}."
            )

        if param.integer and not float(value).is_integer():
            raise ValueError(
                f"{param.label} must be an integer."
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
                    f"{param.label} must use increments "
                    f"of {param.step:g}."
                )

    # ---------------------------------------------------------
    # PARAMETER MANAGEMENT
    # ---------------------------------------------------------

    def get_values(self) -> dict[str, Number]:
        """Read and validate all inputs."""

        result: dict[str, Number] = {}

        for param in self.parameters:
            raw = self.inputs[param.name].text

            try:
                value = float(raw)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Enter a valid number for {param.label}."
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
        """Validate all values before updating any input."""

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
        """Apply the validated configuration."""

        try:
            values = self.get_values()
            self.on_apply(values)

        except (ValueError, TypeError) as exc:
            self.status.text = self._status_html(
                f"Error: {exc}",
                "#dc2626",
            )
            return False

        self.status.text = self._status_html(
            "Changes applied successfully.",
            "#16a34a",
        )

        return True

    def reset(self) -> bool:
        """Restore default values and apply them."""

        defaults = {
            param.name: (
                param.default
                if param.default is not None
                else param.value
            )
            for param in self.parameters
        }

        self.set_values(defaults)
        return self.apply()

    # ---------------------------------------------------------
    # EVENT HANDLERS
    # ---------------------------------------------------------

    def _handle_input_change(self, _event: object) -> None:
        if hasattr(self, "status"):
            self.status.text = self._status_html(
                "Unsaved changes. Click Apply Changes "
                "to update the simulation.",
                "#d97706",
            )

    def _handle_apply(self, _event: object) -> None:
        self.apply()

    def _handle_reset(self, _event: object) -> None:
        self.reset()
