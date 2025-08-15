import abc
import pathlib

import frontmatter
import htpy as h
import mistune
from markupsafe import Markup

from server.layouts import post_layout
from server.schemas import PostMetadata


class Renderer(abc.ABC):
    def __init__(self):
        self.mistune = mistune.create_markdown()

    @abc.abstractmethod
    def to_html(
        self, markdown_content: str, metadata: PostMetadata
    ) -> h.HTMLElement: ...

    def render_content(self, path: pathlib.Path):
        # Parse frontmatter and content
        with open(path, encoding="utf-8") as f:
            post = frontmatter.load(f)

        metadata = PostMetadata(**{k: str(v) for k, v in post.metadata.items()})

        content_html = str(self.mistune(post.content))

        page_html = self.to_html(content_html, metadata=metadata)

        return str(page_html)


class TestRenderer(Renderer):
    def to_html(self, markdown_content: str, metadata: PostMetadata) -> h.HTMLElement:
        return post_layout(theme="lofi", metadata=metadata)[
            h.p["TEEEEST"],
            h.button(class_="btn btn-warning")["click me"],
            h.article(class_="prose")[Markup(markdown_content),],
        ]
