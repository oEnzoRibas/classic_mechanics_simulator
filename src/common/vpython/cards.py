r"""Safe, reusable inline information cards for VPython applications.

LaTeX documents may mix text and formulas delimited by \( ... \), \[ ... \],
$ ... $ or $$ ... $$. Text is HTML-escaped; formulas become MathML.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from re import DOTALL, compile as re_compile, fullmatch
from typing import Optional

from vpython import button, wtext


# Capture display and inline expressions without injecting raw HTML text.
_MATH = re_compile(
    r"\\\[(?P<bracket_display>.*?)\\\]"
    r"|\$\$(?P<dollar_display>.*?)\$\$"
    r"|\\\((?P<bracket_inline>.*?)\\\)"
    r"|(?<!\\)\$(?!\$)(?P<dollar_inline>.*?)(?<!\\)\$(?!\$)",
    DOTALL,
)


@dataclass
class Card:
    """A rendered card and its associated widgets."""

    card_id: int
    title: str
    content_widget: object
    close_button: object


class CardCenter:
    """Manage inline VPython information cards (not modal dialogs)."""

    def __init__(self, pos: object | None = None) -> None:
        self._pos = pos
        self._cards: dict[int, Card] = {}
        self._next_id = 1

    @property
    def cards(self) -> dict[int, Card]:
        """Return a copy of the currently open-card registry."""
        return self._cards.copy()

    @staticmethod
    def _plain_html(text: str) -> str:
        return escape(text).replace("\n", "<br>")

    @classmethod
    def _render_content(cls, content: str, latex: bool = False) -> str:
        """Escape ordinary content and optionally convert delimited LaTeX.

        MathML returned by the converter is inserted only where a math token
        appeared; every other segment is escaped before being placed in HTML.
        """
        if not latex:
            return cls._plain_html(content)

        try:
            from latex2mathml.converter import convert
        except ImportError as exc:
            raise RuntimeError(
                "LaTeX rendering requires latex2mathml "
                "(install with: pip install latex2mathml)."
            ) from exc

        output: list[str] = []
        cursor = 0
        for match in _MATH.finditer(content):
            output.append(cls._plain_html(content[cursor:match.start()]))
            expr = next(group for group in match.groups() if group is not None).strip()
            display = (
                match.group("bracket_display") is not None
                or match.group("dollar_display") is not None
            )
            try:
                mathml = convert(expr)
            except Exception as exc:
                raise ValueError(f"Invalid LaTeX expression: {exc}") from exc
            if display:
                mathml = mathml.replace("<math", '<math display="block"', 1)
            output.append(mathml)
            cursor = match.end()
        output.append(cls._plain_html(content[cursor:]))

        # A single undelimited formula is also allowed, for compatibility.
        if cursor == 0 and "\n" not in content and content.lstrip().startswith("\\"):
            try:
                return convert(content)
            except Exception as exc:
                raise ValueError(f"Invalid LaTeX expression: {exc}") from exc
        return "".join(output)

    def open_card(
        self,
        title: str,
        content: str,
        *,
        subtitle: Optional[str] = None,
        latex: bool = False,
        width: str = "420px",
    ) -> int:
        """Render a card. Set ``latex=True`` for safely delimited math."""
        if fullmatch(r"\d+(?:px|%|rem|em|vw)", width) is None:
            raise ValueError("Card width must be a CSS length (e.g. '420px').")

        rendered = self._render_content(content, latex=latex)
        card_id = self._next_id
        self._next_id += 1

        safe_title = escape(title)
        safe_subtitle = (
            '<div style="color:#adb5bd;margin-bottom:10px">'
            f"{escape(subtitle)}</div>"
            if subtitle else ""
        )
        markup = f"""
        <div style="box-sizing:border-box;width:{width};max-width:100%;
            margin:12px 0 6px;padding:16px;border:1px solid #555;
            border-radius:10px;background:#202124;color:#f1f3f4;
            font-family:Arial,sans-serif;overflow-wrap:anywhere">
          <div style="font-size:17px;font-weight:bold;margin-bottom:10px">
            {safe_title}
          </div>
          {safe_subtitle}
          <div style="line-height:1.6">{rendered}</div>
        </div>
        """
        pos_args = {"pos": self._pos} if self._pos is not None else {}
        content_widget = wtext(text=markup, **pos_args)
        close_button = button(
            text=f"Fechar card {card_id}",
            bind=lambda _event, cid=card_id: self.close_card(cid),
            **pos_args,
        )
        wtext(text="<br>", **pos_args)

        self._cards[card_id] = Card(
            card_id=card_id,
            title=title,
            content_widget=content_widget,
            close_button=close_button,
        )
        return card_id

    def close_card(self, card_id: int) -> bool:
        """Hide one card and disable its button. Return False if absent."""
        card = self._cards.pop(card_id, None)
        if card is None:
            return False
        card.content_widget.text = ""
        card.close_button.disabled = True
        return True

    def close_all(self) -> None:
        """Close every currently open card."""
        for card_id in list(self._cards):
            self.close_card(card_id)
