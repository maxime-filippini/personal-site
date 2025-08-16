import datetime

import htpy as h

from server.config import settings
from server.html.layouts import main_layout
from server.html.layouts import with_topnav
from server.html.utils import fancy_link
from server.schemas import PostMetadata


def cv_page(theme: str):
    return with_topnav(title="My CV", theme=theme)[
        h.div(class_="max-w-4xl mx-auto")[
            h.div(class_="mb-8")[
                h.h1(
                    class_="sm:text-5xl text-3xl font-bold border border-2 border-black p-8 bg-white mb-4 text-center",
                )["Maxime Filippini"],
                h.div(class_="flex gap-4 justify-center sm:text-2xl text-xl")[
                    h.p(class_="border-r border-black px-4 text-center w-1/2")[
                        "Risk manager"
                    ],
                    h.p(class_="px-4 text-center w-1/2")["Software developer"],
                ],
            ],
            h.div(class_="space-y-6 mt-12")[
                h.section[
                    h.h2(class_="text-2xl font-semibold mb-4")["Experience"],
                    h.p(class_="text-gray-700")["CV content will go here..."],
                ],
                h.section[
                    h.h2(class_="text-2xl font-semibold mb-4")["Education"],
                    h.p(class_="text-gray-700")["CV content will go here..."],
                ],
                h.section[
                    h.h2(class_="text-2xl font-semibold mb-4")["Technologies"],
                    h.p(class_="text-gray-700")["CV content will go here..."],
                ],
                h.section[
                    h.h2(class_="text-2xl font-semibold mb-4")["Languages"],
                    h.p(class_="text-gray-700")["CV content will go here..."],
                ],
            ],
        ]
    ]


def home_page(theme: str):
    return main_layout(theme=theme, title="Maxime Filippini")[
        h.div(
            class_="flex flex-col h-screen items-center justify-center gap-8 max-w-2xl mx-auto"
        )[
            h.h1(
                class_="sm:text-5xl text-3xl text-center font-bold border border-2 border-black p-8 bg-white w-full",
                style="view-transition-name: name-title",
            )["Maxime Filippini"],
            h.div(
                class_="flex w-full justify-center",
                style="view-transition-name: subtitle-title",
            )[
                h.h2(
                    class_="sm:text-2xl text-xl border-r border-black px-4 w-1/2 text-center"
                )["Risk manager"],
                h.h2(class_="sm:text-2xl text-xl px-4 w-1/2 text-center")[
                    "Software developer"
                ],
            ],
            h.div(class_="flex w-full justify-center")[
                fancy_link(emoji="🤓", text="CV", href="/cv/"),
                fancy_link(emoji="👨🏼‍💻", text="Blog", href="/posts/", last=True),
            ],
        ],
    ]


def posts_index(posts: list[PostMetadata], *, theme: str):
    """Layout for the posts index page"""

    today = datetime.date.today()

    def _days_since_post(metadata: PostMetadata):
        days = (today - metadata.posted_on).days

        match days:
            case 0:
                return "Posted today"
            case 1:
                return "Posted yesterday"
            case _:
                return f"Posted {days} days ago"

    post_data = [
        h.article(class_="border-b border-base-300 pb-6")[
            h.h2(class_="text-2xl font-semibold mb-2")[
                h.a(
                    href=f"/posts/{post.slug}",
                    class_="link link-hover text-primary",
                )[post.title]
            ],
            h.p(class_="text-xs mb-2 text-stone-400")[_days_since_post(post)],
            h.p[post.abstract],
        ]
        for post in posts
        if (settings.BLOG_PROD and not post.draft) or (not settings.BLOG_PROD)
    ]

    return with_topnav(theme=theme, title="Posts")[
        h.div(class_="max-w-4xl mx-auto")[
            h.div(class_="space-y-6")[post_data]
            if post_data
            else h.p(class_="text-base-content/70")["No posts found."],
        ]
    ]
