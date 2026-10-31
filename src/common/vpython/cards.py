
"""Reusable native HTML modals for VPython.

The launcher stays in the canvas caption.
The hidden dialog is mounted separately to avoid layout gaps.
"""

from __future__ import annotations

from html import escape
from html.parser import HTMLParser
from re import DOTALL, compile as re_compile, fullmatch
from uuid import uuid4

from vpython import wtext


_MATH = re_compile(
    r"\\\[(?P<display_bracket>.*?)\\\]"
    r"|\$\$(?P<display_dollar>.*?)\$\$"
    r"|\\\((?P<inline_bracket>.*?)\\\)"
    r"|(?<!\\)\$(?!\$)(?P<inline_dollar>.*?)(?<!\\)\$(?!\$)",
    DOTALL,
)

_ALLOWED_TAGS = {
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "div", "span", "b", "strong",
    "i", "em", "u", "br", "hr",
    "ul", "ol", "li", "blockquote",
    "sub", "sup", "pre", "code",
}

_VOID_TAGS = {"br", "hr"}


def _text_and_math(text: str) -> str:
    """Escape text and convert delimited LaTeX to MathML."""

    from latex2mathml.converter import convert

    parts: list[str] = []
    end = 0

    for match in _MATH.finditer(text):
        parts.append(
            escape(text[end:match.start()]).replace(
                "\n", "<br>"
            )
        )

        expression = next(
            group
            for group in match.groups()
            if group is not None
        )

        try:
            mathml = convert(expression.strip())
        except Exception as exc:
            raise ValueError(
                f"Invalid LaTeX expression: {exc}"
            ) from exc

        is_display = (
            match.group("display_bracket") is not None
            or match.group("display_dollar") is not None
        )

        if is_display:
            mathml = mathml.replace(
                "<math",
                '<math display="block"',
                1,
            )

        parts.append(mathml)
        end = match.end()

    parts.append(
        escape(text[end:]).replace("\n", "<br>")
    )

    return "".join(parts)


class _SafeProblemHTML(HTMLParser):
    """Preserve basic formatting without unsafe HTML attributes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in _ALLOWED_TAGS:
            self.parts.append(f"<{tag}>")

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        if tag in _ALLOWED_TAGS:
            self.parts.append(f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        if tag in _ALLOWED_TAGS and tag not in _VOID_TAGS:
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(_text_and_math(data))


class CardCenter:
    """Manage compact modal launchers and native dialogs."""

    def __init__(
        self,
        pos: object | None = None,
        modal_pos: object | None = None,
    ) -> None:
        self._pos = pos
        self._modal_pos = (
            modal_pos if modal_pos is not None else pos
        )

        self._modal_widgets: list[object] = []

    @staticmethod
    def _render_content(
        content: str,
        latex: bool = False,
    ) -> str:
        if not latex:
            return escape(content).replace("\n", "<br>")

        try:
            parser = _SafeProblemHTML()
            parser.feed(content)
            parser.close()
            return "".join(parser.parts)

        except ImportError as exc:
            raise RuntimeError(
                "Install LaTeX rendering: uv add latex2mathml"
            ) from exc

    def add_modal_launcher(
        self,
        *,
        button_text: str,
        title: str,
        content: str,
        subtitle: str | None = None,
        latex: bool = False,
        width: str = "860px",
        label: str | None = None,
    ) -> object:
        """Create a reusable launcher and its native modal."""

        if not fullmatch(
            r"\d+(?:px|%|rem|em|vw)",
            width,
        ):
            raise ValueError(
                "Width must be a CSS length, e.g. '860px'."
            )

        modal_id = f"vpython-dialog-{uuid4().hex}"
        launcher_id = f"{modal_id}-launcher"

        content_html = self._render_content(
            content,
            latex,
        )

        subtitle_html = (
            '<div class="dialog-subtitle">'
            f'{escape(subtitle)}'
            '</div>'
            if subtitle
            else ""
        )

        label_html = (
            '<span style="'
            'display:inline-block;'
            'box-sizing:border-box;'
            'width:112px;'
            'flex:0 0 112px;'
            'font:600 12px Arial,sans-serif;'
            'color:#475569">'
            f'{escape(label)}'
            '</span>'
            if label
            else ""
        )

        # Only the compact launcher is placed in the
        # right-hand controls. No dialog or CSS here.

        launcher_html = (
            '<span style="'
            'display:inline-flex;'
            'align-items:center;'
            'vertical-align:middle;'
            'margin-left:12px;'
            'white-space:nowrap;'
            'line-height:1;'
            'height:26px">'
            f'{label_html}'
            f'<button id="{launcher_id}" '
            'type="button" '
            f'commandfor="{modal_id}" '
            'command="show-modal">'
            f'{escape(button_text)}'
            '</button>'
            '</span>'
        )

        # The dialog and its styles are mounted separately.

        modal_html = f"""
<style>
#{launcher_id} {{
    all: unset !important;
    box-sizing: border-box !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    vertical-align: middle !important;

    height: 26px !important;
    width: 166px !important;
    min-height: 26px !important;
    min-width: 166px !important;

    margin: 0 !important;
    padding: 0 9px !important;

    border: 1px solid #0f766e !important;
    border-radius: 6px !important;

    background: #0d9488 !important;
    color: #ffffff !important;

    font: 700 11px/1 Arial, sans-serif !important;
    white-space: nowrap !important;

    cursor: pointer !important;
}}

#{launcher_id}:hover {{
    background: #0f766e !important;
}}

#{modal_id}:not([open]) {{
    display: none !important;
}}

#{modal_id} {{
    box-sizing: border-box !important;
    width: {width} !important;
    max-width: calc(100vw - 32px) !important;
    max-height: 86dvh !important;

    margin: auto !important;
    padding: 0 !important;

    border: 1px solid #3a4a61 !important;
    border-radius: 12px !important;

    background: #111827 !important;
    color: #e2e8f0 !important;

    font-family: Arial, sans-serif !important;
    box-shadow: 0 22px 70px rgba(0,0,0,.7) !important;
    overflow: hidden !important;
}}

#{modal_id}::backdrop {{
    background: rgba(5,10,20,.78);
    backdrop-filter: blur(4px);
}}

#{modal_id} .dialog-layout {{
    display: flex;
    flex-direction: column;
    max-height: 86dvh;
    min-width: 0;
}}

#{modal_id} .dialog-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;

    padding: 13px 18px;
    background: #1e293b;
    border-bottom: 1px solid #334155;
}}

#{modal_id} .dialog-title {{
    font: 700 18px/1.3 Arial, sans-serif;
    color: #f8fafc;
}}

#{modal_id} .dialog-subtitle {{
    margin-top: 4px;
    font: 12px/1.4 Arial, sans-serif;
    color: #94a3b8;
}}

#{modal_id} .dialog-body {{
    flex: 1;
    min-height: 0;
    min-width: 0;

    overflow-y: auto;
    overflow-x: hidden;

    padding: 18px 22px;

    white-space: normal;
    overflow-wrap: anywhere;
    font: 15px/1.65 Arial, sans-serif;
}}

#{modal_id} .dialog-body * {{
    box-sizing: border-box;
    max-width: 100%;
    overflow-wrap: anywhere;
}}

#{modal_id} .dialog-body h2,
#{modal_id} .dialog-body h3 {{
    margin: 10px 0 7px !important;
    color: #7dd3fc !important;
    line-height: 1.35 !important;
}}

#{modal_id} .dialog-body pre,
#{modal_id} .dialog-body code {{
    white-space: pre-wrap !important;
}}

#{modal_id} .dialog-footer {{
    display: flex;
    justify-content: flex-end;
    padding: 10px 18px;

    background: #1e293b;
    border-top: 1px solid #334155;
}}

#{modal_id} .dialog-button {{
    all: unset !important;
    box-sizing: border-box !important;

    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;

    background: #334155 !important;
    color: #f8fafc !important;

    border: 1px solid #475569 !important;
    border-radius: 7px !important;

    font: 600 13px/1 Arial, sans-serif !important;
    cursor: pointer !important;
}}

#{modal_id} .dialog-button:hover {{
    background: #475569 !important;
}}

#{modal_id} .dialog-x {{
    width: 30px !important;
    height: 30px !important;
    font-size: 18px !important;
}}

#{modal_id} .dialog-close {{
    height: 32px !important;
    padding: 0 16px !important;
}}
</style>

<dialog
    id="{modal_id}"
    aria-labelledby="{modal_id}-title"
>
    <div class="dialog-layout">

        <header class="dialog-header">

            <div>
                <div
                    id="{modal_id}-title"
                    class="dialog-title"
                >
                    {escape(title)}
                </div>

                {subtitle_html}
            </div>

            <form method="dialog" style="margin:0">
                <button
                    type="submit"
                    class="dialog-button dialog-x"
                    aria-label="Close"
                >
                    &times;
                </button>
            </form>

        </header>

        <section class="dialog-body">
            {content_html}
        </section>

        <footer class="dialog-footer">

            <form method="dialog" style="margin:0">
                <button
                    type="submit"
                    class="dialog-button dialog-close"
                >
                    Close
                </button>
            </form>

        </footer>

    </div>
</dialog>
"""

        modal_args = (
            {"pos": self._modal_pos}
            if self._modal_pos is not None
            else {}
        )

        launcher_args = (
            {"pos": self._pos}
            if self._pos is not None
            else {}
        )

        # Mount modal outside the control column.
        modal_widget = wtext(
            text=modal_html,
            **modal_args,
        )

        # Keep the modal widget registered.
        self._modal_widgets.append(modal_widget)

        # Only this small widget occupies the control row.
        return wtext(
            text=launcher_html,
            **launcher_args,
        )
