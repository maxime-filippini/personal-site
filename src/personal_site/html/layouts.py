from typing import TYPE_CHECKING

import htpy as h
from markupsafe import Markup

from personal_site.html.svgs import moon
from personal_site.html.svgs import sun
from personal_site.html.utils import link
from personal_site.html.utils import posthog
from personal_site.html.utils import static_url
from personal_site.settings import settings

if TYPE_CHECKING:
    from personal_site.posts import PostMetadata


@h.with_children
def root_layout(children: h.Node, *, theme: str, title: str, description: str):
    posthog_script = posthog() if settings.BLOG_PROD else None

    return h.html(data_theme=theme, lang="en")[
        h.head[
            h.meta(charset="UTF-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            h.title[title],
            h.meta(property="og:description", content=description),
            h.link(rel="stylesheet", href=static_url("app.css")),
            h.link(rel="stylesheet", href=static_url("pygments-theme-aware.css")),
            h.link(
                rel="icon",
                href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>👨🏼‍💻</text></svg>",
            ),
            posthog_script,
            h.script(src=static_url("htmx.min.js")),
            h.script(
                src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js",
                defer=True,
            ),
            h.script(src=static_url("js/alpine_stuff.js")),
            h.script(src=static_url("js/theme_init.js")),
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
    return root_layout(theme=theme, title=title, description="")[
        h.body(class_="font-mono min-h-screen bg-base-100")[
            h.div(class_="min-h-screen")[children]
        ],
    ]


@h.with_children
def with_topnav(
    children: h.Node, *, theme: str, title: str, description: str
) -> h.Renderable:
    return root_layout(theme=theme, title=title, description=description)[
        h.body(class_="font-mono min-h-screen bg-base-100")[
            h.div(class_="max-w-6xl mx-auto min-h-screen border-x border-base-300")[
                h.nav(
                    class_="h-16 flex items-center sm:justify-between justify-center px-4 sm:px-8 border-b border-base-300 bg-base-200 sm:sticky sm:top-0 sm:z-[999]"
                )[
                    h.a(class_="text-lg sm:block hidden link link-hover", href="/")[
                        "Maxime Filippini"
                    ],
                    h.div(
                        class_="flex gap-4 sm:gap-6 items-center text-xs sm:text-base"
                    )[
                        link(name="Home", href="/"),
                        link(name="CV", href="/cv/"),
                        link(name="Blog", href="/posts/"),
                        link(name="Contact", href="/contact/"),
                        h.button(
                            class_="rounded-full bg-base-100 border border-base-300 p-1 duration-100 stroke-base-content cursor-pointer stroke-1 hover:bg-black hover:stroke-white",
                            x_data=True,
                            **{
                                "@click": "$store.darkMode.toggle()",
                                "x-show": "!$store.darkMode.on",
                            },
                        )[moon()],
                        h.button(
                            class_="rounded-full bg-base-100 border border-base-300 p-1 duration-100 stroke-base-content cursor-pointer stroke-1 hover:bg-white hover:stroke-black",
                            x_data=True,
                            **{
                                "@click": "$store.darkMode.toggle()",
                                "x-show": "$store.darkMode.on",
                            },
                        )[sun()],
                    ],
                ],
                h.main[children],
            ]
        ]
    ]


@h.with_children
def post_layout(
    children: h.Node, *, theme: str, metadata: PostMetadata
) -> h.Renderable:
    return with_topnav(
        theme=theme, title=metadata.title, description=metadata.abstract
    )[children]
