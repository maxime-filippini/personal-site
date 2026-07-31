import abc
import pathlib

import frontmatter
import htpy as h
import mistune
from markupsafe import Markup

from personal_site.constants import BLOG_THEME
from personal_site.html.layouts import post_layout
from personal_site.mistune import BlogRenderer
from personal_site.posts import PostMetadata

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
        self.mistune = mistune.create_markdown(
            escape=False, renderer=BlogRenderer(escape=False), plugins=["table"]
        )

    def to_html(self, markdown_content: str, metadata: PostMetadata) -> h.Renderable:
        dates = [
            h.p[f"Published {metadata.posted_on.strftime('%Y-%m-%d')}"],
        ]

        if metadata.last_update != metadata.posted_on:
            dates.extend(
                [
                    h.span["·"],
                    h.p[f"Updated {metadata.last_update.strftime('%Y-%m-%d')}"],
                ]
            )

        html = self.mistune(markdown_content)

        return post_layout(theme=BLOG_THEME, metadata=metadata)[
            h.article[
                h.header(class_="border-b border-base-300")[
                    h.div(class_="max-w-3xl mx-auto px-6 py-10 sm:px-8 sm:py-14")[
                        # h.p(class_="text-sm text-base-content/60 font-semibold mb-4")[
                        #     "Draft" if metadata.draft else "Writing and projects"
                        # ],
                        h.h1(class_="text-3xl sm:text-4xl font-bold leading-tight")[
                            metadata.title
                        ],
                        h.div(
                            class_="flex flex-wrap items-center gap-3 mt-5 text-xs text-base-content/60"
                        )[dates],
                    ]
                ],
                h.div(class_="border-b border-base-300")[
                    h.div(
                        class_="prose prose-stone max-w-3xl mx-auto px-6 py-8 sm:px-8 sm:py-12 prose-pre:bg-base-200 prose-pre:rounded-none prose-pre:text-black prose-pre:border prose-pre:border-accent prose-img:border-accent prose-img:border prose-img:w-full prose-a:hover:font-bold prose-a:duration-100"
                    )[Markup(html)]
                ],
            ]
        ]
