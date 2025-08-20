import htpy as h
from markupsafe import Markup

from server.config import settings
from server.html.utils import link
from server.html.utils import posthog
from server.schemas import PostMetadata


@h.with_children
def root_layout(children: h.Node, *, theme: str, title: str):
    posthog_script = posthog() if settings.BLOG_PROD else None

    return h.html(data_theme=theme, lang="en")[
        h.head[
            h.meta(charset="UTF-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            h.title[title],
            h.link(rel="stylesheet", href="/static/output.css"),
            posthog_script,
            h.script(src="/static/htmx.min.js"),
        ],
        children,
        Markup("""
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11.10.0/+esm'

// Initialize mermaid on page load
mermaid.initialize({ startOnLoad: true });

// Reinitialize mermaid after htmx navigation
document.addEventListener('htmx:afterSwap', function() {
    mermaid.run();
});
</script>
"""),
    ]


@h.with_children
def main_layout(children: h.Node, *, theme: str, title: str):
    return root_layout(theme=theme, title=title)[
        h.body(class_="font-mono bg-stone-50 min-h-screen")[
            h.div(class_="p-8")[children]
        ],
    ]


@h.with_children
def with_topnav(children: h.Node, *, theme: str, title: str) -> h.Renderable:
    return root_layout(theme=theme, title=title)[
        h.body(class_="font-mono bg-stone-50 min-h-screen")[
            h.div(class_="pt-18")[
                h.div(
                    class_="w-full h-12 py-4 flex items-center sm:justify-between justify-center px-8 border-b border-stone-200 bg-stone-100 fixed top-0"
                )[
                    h.a(class_="text-lg sm:block hidden link link-hover", href="/")[
                        "Maxime Filippini"
                    ],
                    h.div(class_="flex gap-6 items-center")[
                        link(name="Home", href="/"),
                        link(name="CV", href="/cv/"),
                        link(name="Blog", href="/posts/"),
                        link(name="Contact me", href="/contact/"),
                    ],
                ],
                h.div(class_="px-8")[children],
            ]
        ]
    ]


@h.with_children
def post_layout(
    children: h.Node, *, theme: str, metadata: PostMetadata
) -> h.Renderable:
    return with_topnav(theme=theme, title=metadata.title)[
        h.div(class_="container max-w-3xl mx-auto mb-8")[children]
    ]
