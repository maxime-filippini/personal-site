import abc
import pathlib
import re
from html import escape

import frontmatter
import htpy as h
import mistune
from markupsafe import Markup
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer
from pygments.lexers import get_lexer_by_name

from server.html.layouts import post_layout
from server.html.svgs import permalink
from server.schemas import PostMetadata

LEVEL_HEADINGS_MAP = {1: h.h1, 2: h.h2, 3: h.h3, 4: h.h4, 5: h.h5, 6: h.h6}


class Renderer(abc.ABC):
    def __init__(self):
        self.mistune = mistune.create_markdown()

    @abc.abstractmethod
    def to_html(
        self, markdown_content: str, metadata: PostMetadata
    ) -> h.Renderable: ...

    def render_content(self, path: pathlib.Path):
        with open(path, encoding="utf-8") as f:
            post = frontmatter.load(f)

        metadata_dict = dict(post.metadata)
        metadata_dict["slug"] = path.stem

        metadata = PostMetadata(**metadata_dict)  # type: ignore

        content_html = str(self.mistune(post.content))

        page_html = self.to_html(content_html, metadata=metadata)

        return str(page_html)


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
        lang = (info or "").split(None, 1)[0]
        if not lang:
            return str(h.pre()[h.code[escape(code)]])
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except Exception:
            lexer = TextLexer(stripall=True)
        return highlight(code, lexer, HtmlFormatter(wrapcode=True))


class TestRenderer(Renderer):
    def __init__(self):
        self.mistune = mistune.create_markdown(renderer=BlogRenderer())

    def to_html(self, markdown_content: str, metadata: PostMetadata) -> h.Renderable:
        if metadata.last_update == metadata.posted_on:
            class_ = "text-sm border-y border-stone-400 py-4"
            add_update = False
        else:
            class_ = "text-sm border-t border-stone-400 pt-4"
            add_update = True

        elts = [
            h.p(class_=class_)[
                f"Originally posted on: {metadata.posted_on.strftime('%Y-%m-%d')}"
            ],
        ]

        if add_update:
            elts.append(
                h.p(class_="text-sm border-b border-stone-400 pb-4")[
                    f"Last updated on: {metadata.last_update.strftime('%Y-%m-%d')}"
                ]
            )

        return post_layout(theme="lofi", metadata=metadata)[
            h.article(
                class_="prose prose-pre:bg-stone-100 prose-pre:rounded-none prose-pre:text-black prose-stone h-full w-full mt-8 prose-pre:border prose-pre:border-stone-300"
            )[
                h.h1[metadata.title],
                *elts,
                Markup(markdown_content),
            ],
        ]
