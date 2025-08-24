import abc
import pathlib

import frontmatter
import htpy as h
import mistune
from markupsafe import Markup

from server.html.layouts import post_layout
from server.mistune import BlogRenderer
from server.schemas import PostMetadata

LEVEL_HEADINGS_MAP = {1: h.h1, 2: h.h2, 3: h.h3, 4: h.h4, 5: h.h5, 6: h.h6}


class BaseRenderer(abc.ABC):
    def __init__(self):
        self.mistune = mistune.create_markdown(escape=False)

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

        return Markup(page_html), metadata


class BlogPostRenderer(BaseRenderer):
    def __init__(self):
        self.mistune = mistune.create_markdown(escape=False, renderer=BlogRenderer())

    def to_html(self, markdown_content: str, metadata: PostMetadata) -> h.Renderable:
        print(markdown_content)
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
                class_="prose prose-pre:bg-base-200 prose-pre:rounded-none prose-pre:text-black prose-stone h-full w-full mt-8 prose-pre:border prose-pre:border-accent prose-img:border-accent prose-img:border prose-a:hover:font-bold prose-a:duration-100"
            )[
                h.h1[metadata.title],
                *elts,
                Markup(markdown_content),
            ],
        ]
