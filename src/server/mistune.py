import re
import shlex
from html import escape

import htpy as h
import mistune
from bs4 import BeautifulSoup
from catppuccin.extras.pygments import LatteStyle
from markupsafe import Markup
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer
from pygments.lexers import get_lexer_by_name

from server.html.svgs import permalink

LEVEL_HEADINGS_MAP = {1: h.h1, 2: h.h2, 3: h.h3, 4: h.h4, 5: h.h5, 6: h.h6}


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]+", "", text)
    return re.sub(r"\s+", "-", text)


class BlogRenderer(mistune.HTMLRenderer):
    def heading(self, text, level, **attrs):
        hid = attrs.get("id") or slugify(text)

        elt = LEVEL_HEADINGS_MAP[level]

        return str(
            elt(id=hid, class_="flex gap-8 items-center")[
                h.span[text],
                h.a(href=f"#{hid}", aria_label="Permalink")[permalink()],
            ]
        )

    def block_code(self, code, info=None):
        # "info" is the fence info string, e.g. "python"
        lang, *opts = shlex.split(info or "")
        if not lang:
            return str(h.pre()[h.code[escape(code)]])
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except Exception:
            lexer = TextLexer(stripall=True)

        # Parse the options
        parsed_opts = {}

        for opt in opts:
            if "=" not in opt:
                continue
            left, right = opt.split("=", 1)
            parsed_opts[left] = right

        if "lint" in parsed_opts:
            parsed_opts["lint"] = [int(ln) for ln in parsed_opts["lint"].split(" ")]

        print(parsed_opts)

        if lang == "custom":
            elt = parsed_opts.pop("elt")
            path = parsed_opts.pop("__path")
            return Markup(f"""
                          <script src="{path}"></script>
                          <{elt}></{elt}>
                """)

        if lang == "mermaid":
            return str(h.center[h.pre(class_="mermaid")[code]])

        if lang == "raw_html":
            return str(Markup(code))

        if lang == "note":
            markdown_parser = mistune.create_markdown(renderer=self, escape=False)
            code_modified = code.replace("```", "````")
            parsed, _ = markdown_parser.parse(code_modified)
            return str(
                h.div(class_="bg-base-200 border-accent border py-2 px-4")[
                    h.p(class_="font-bold")["Note"], Markup(parsed)
                ]
            )

        if lang == "youtube":
            return str(
                h.iframe(
                    class_="w-full",
                    height="400",
                    src=parsed_opts["url"],
                    frameborder="0",
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
                    referrerpolicy="strict-origin-when-cross-origin",
                    allowfullscreen=True,
                )
            )

        if lang == "callout":
            markdown_parser = mistune.create_markdown(renderer=self, escape=False)
            parsed, _ = markdown_parser.parse(code)
            return str(
                h.div(class_="bg-base-200 border-accent border py-2 px-4")[
                    Markup(parsed)
                ]
            )

        highlighted = highlight(
            code,
            lexer,
            HtmlFormatter(wrapcode=True, style=LatteStyle, linespans="line"),
        )

        # Post formatting for lint lines
        if lint_lines := parsed_opts.get("lint"):
            soup = BeautifulSoup(highlighted)
            for ln in lint_lines:
                span = soup.find(id=f"line-{ln}")
                if span:
                    span["class"] = span.get("class", []) + ["lint-error"]  # type: ignore

            return str(soup)

        return highlighted
