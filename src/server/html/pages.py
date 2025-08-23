import datetime

import htpy as h

from server.config import settings
from server.html.layouts import main_layout
from server.html.layouts import with_topnav
from server.html.utils import fancy_link
from server.schemas import PostMetadata


def home_page(theme: str):
    return main_layout(theme=theme, title="Maxime Filippini")[
        h.div(
            class_="flex flex-col h-screen items-center justify-center gap-8 max-w-2xl mx-auto"
        )[
            h.h1(
                class_="sm:text-5xl text-3xl text-center font-bold border border-2 border-black p-8 bg-white w-full",
            )["Maxime Filippini"],
            h.div(
                class_="flex w-full justify-center items-center",
            )[
                h.h2(
                    class_="sm:text-2xl text-xl border-r border-black px-4 w-1/2 text-center"
                )["Risk manager"],
                h.h2(class_="sm:text-2xl text-xl px-4 w-1/2 text-center")[
                    "Software developer"
                ],
            ],
            h.div(
                class_="flex flex-col sm:flex-row gap-2 items-center w-full justify-center"
            )[
                fancy_link(text="CV", href="/cv/"),
                fancy_link(text="Blog", href="/posts/"),
                fancy_link(text="Contact me", href="/contact/", last=True),
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
                    hx_boost="true",
                )[post.title]
            ],
            h.p(class_="text-xs mb-2 text-stone-400")[_days_since_post(post)],
            h.p[post.abstract],
        ]
        for post in reversed(sorted(posts, key=lambda item: item.last_update))
        if (settings.BLOG_PROD and not post.draft) or (not settings.BLOG_PROD)
    ]

    return with_topnav(theme=theme, title="Posts", description="The posts index")[
        h.div(class_="max-w-4xl mx-auto")[
            h.div(class_="space-y-6")[post_data]
            if post_data
            else h.p(class_="text-base-content/70")["No posts found."],
        ]
    ]


@h.with_children
def _exp_block(
    children: h.Node,
    *,
    company: str,
    grade: str,
    start_date: datetime.date,
    end_date: datetime.date | None = None,
) -> h.Renderable:
    start = start_date.strftime("%b %Y")
    end = end_date.strftime("%b %Y") if end_date else "Present"

    return h.div[
        h.div(class_="flex flex-row gap-8 mb-4")[
            h.p(class_="text-lg")[f"{start} - {end}"],
            h.div(class_="flex flex-col")[
                h.p(class_="text-xl font-semibold")[f"{company}"],
                h.p(class_="font-semibold")[f"({grade})"],
            ],
        ],
        h.div(class_="text-base italic text-stone-500")[children],
    ]


@h.with_children
def _edu_block(
    children: h.Node,
    *,
    year: int,
    diploma: str,
    institution: str,
) -> h.Renderable:
    return h.div[
        h.div(class_="flex flex-row gap-8 mb-4")[
            h.p(class_="text-lg")[year],
            h.div(class_="flex flex-col")[
                h.p(class_="text-xl font-semibold")[diploma],
                h.p(class_="font-semibold")[institution],
            ],
        ],
        h.div(class_="text-base italic text-stone-500")[children],
    ]


@h.with_children
def _tech_block(
    children: h.Node,
    *,
    name: str,
    lst: list[str],
) -> h.Renderable:
    *lst, last = lst
    return h.div[
        h.h3(class_="text-xl mb-2 flex w-full")[h.span(class_="font-semibold")[name],],
        h.div(class_="flex flex-row flex-wrap")[
            *[h.p(class_="after:content-['•'] after:mx-3")[item] for item in lst],
            h.p[last],
        ],
    ]


def cv_page(theme: str):
    return with_topnav(title="My CV", theme=theme, description="My CV")[
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
                    h.div(class_="flex flex-col gap-4")[
                        _exp_block(
                            company="Deloitte Luxembourg",
                            grade="Manager → Senior Manager",
                            start_date=datetime.date(2023, 10, 1),
                            end_date=None,
                        )[
                            h.p[
                                """
                                Since my return to Deloitte, I have assisted Luxembourg management companies on risk management topics, through trainings (Deloitte Quantitative Masterclasses) and advisory.
                                
                                This work includes in-depth validation of market risk and liquidity risk models, in accordance with regulatory expectations.

                                In addition, I have led and contributed to a substantial Python library designed to help business teams define their own data workflows,
                                thus streamlining client onboarding for our reporting activities.
                        
                                """
                            ]
                        ],
                        _exp_block(
                            company="Banque Internationale à Luxembourg (BIL)",
                            grade="Senior Quantitative Analyst",
                            start_date=datetime.date(2021, 9, 1),
                            end_date=datetime.date(2023, 9, 30),
                        )[
                            h.p[
                                "As part of the Internal Validation, and Model Risk Management teams, I was involved in the review of risk models at the Bank."
                            ],
                            h.p(class_="my-4")["Model types include:"],
                            h.ul(class_="list-disc list-inside")[
                                h.li[
                                    "Market risk for the trading book (e.g. Value-at-Risk);"
                                ],
                                h.li[
                                    "Valuation of derivatives and structured products;"
                                ],
                                h.li["Initial margin;"],
                                h.li["Economic capital models (ICAAP);"],
                                h.li[
                                    "IRRBB-related models (e.g. Non-Maturity Deposits);"
                                ],
                            ],
                            h.p(class_="my-4")[
                                "In addition to model reviews, I participated in the building of a standard set of libraries and Python-based tools for the model validation activities, e.g. statistical testing and methodology documentation."
                            ],
                        ],
                        _exp_block(
                            company="Deloitte Luxembourg",
                            grade="Analyst → Consultant → Senior Consultant → Manager",
                            start_date=datetime.date(2016, 4, 1),
                            end_date=datetime.date(2021, 8, 31),
                        )[
                            h.p(class_="mb-4")["Relevant activities include:"],
                            h.ul(class_="list-disc list-inside")[
                                h.li[
                                    "Promotion of best programming practices to business teams within a 80-person department"
                                ],
                                h.li[
                                    "Training of staff on quantitative methods involved in the production of regulatory reporting activities for investment funds"
                                ],
                                h.li[
                                    "Various developments in Python (incl. a full analytics pipeline for PRIIPs analytics)"
                                ],
                                h.li[
                                    "Validation of VaR models for Global Exposure calculation under CSSF Circular 11/512"
                                ],
                                h.li[
                                    "Development and Facilitation of technical training programs (Deloitte Quantitative Masterclasses) covering various risk management topics (Value-at-Risk, Liquidity Risk, Stress testing)"
                                ],
                            ],
                        ],
                    ],
                ],
                h.section[
                    h.h2(class_="text-2xl font-semibold mb-4")["Education"],
                    h.div(class_="flex flex-col gap-4")[
                        _edu_block(
                            year=2021,
                            diploma="Certificate in Investment Performance Measurement (CIPM®)",
                            institution="CFA Institute",
                        )[
                            h.p(class_="text-right w-full text-sm")[
                                "Earned the certificate, membership has since lapsed"
                            ]
                        ],
                        _edu_block(
                            year=2019,
                            diploma="Financial Risk Manager (FRM®)",
                            institution="Global Association of Risk Professionals (GARP)",
                        )[
                            h.div(class_="flex w-full")[
                                h.div(class_="mr-auto"),
                                h.a(
                                    class_="text-sm link",
                                    href="https://my.garp.org/DigitalBadgeFRM?id=0031W00001z8OFEQA2",
                                )["Click to see badge"],
                            ]
                        ],
                        _edu_block(
                            year=2016,
                            diploma="Master in Probability and Statistics",
                            institution="Université de Lorraine",
                        )[
                            h.p(class_="mb-4")["Relevant coursework include:"],
                            h.ul(class_="list-disc list-inside")[
                                h.li[
                                    "Stochastic Calculus and financial applications (Option pricing and Interest Rate models, Vasicek, HJM, HW, HL, CIR, ...)"
                                ],
                                h.li[
                                    "Financial Econometrics (Linear/Nonlinear regressions, cross section analysis, univariate/multivariate timeseries analysis, vector autoregression)"
                                ],
                                h.li[
                                    "Market Risk Management (Review of financial markets, Review of stylized facts of asset returns, Risk measures, VaR/ES, European regulatory framework)"
                                ],
                                h.li[
                                    "Quantitative Risk Modelling (Probability theory for Risk Management, liquidity risk, spectral measures, tail modelling, extensions of CLT, stable distributions, stochastic volatility models)"
                                ],
                                h.li["Monte-Carlo techniques for finance"],
                                h.li["Biostatistics"],
                                h.li["Statistical signal processing"],
                                h.li["Spatial statistics"],
                                h.li[
                                    "GNU R, SQL, Matlab, Microsoft Excel VBA, Microsoft Access"
                                ],
                            ],
                        ],
                    ],
                ],
                h.section[
                    h.h2(class_="text-2xl font-semibold mb-4")["Technologies"],
                    h.div(class_="flex flex-col gap-4")[
                        _tech_block(
                            name="Programming languages",
                            lst=[
                                "Python",
                                "JavaScript",
                                "TypeScript",
                                "Elixir",
                                "Gleam",
                                "Visual Basic for Application",
                                "Bash",
                            ],
                        ),
                        _tech_block(
                            name="Web development",
                            lst=[
                                "HTML",
                                "CSS",
                                "JavaScript",
                                "FastAPI",
                                "SQL",
                                "htmx",
                                "Phoenix (and LiveView)",
                                "Svelte",
                                "TailwindCSS",
                            ],
                        ),
                        _tech_block(
                            name="Development tools",
                            lst=["Git", "Terminal utilities (UNIX)", "Docker", "tbd"],
                        ),
                        _tech_block(
                            name="Back-end",
                            lst=[
                                "PostgreSQL",
                                "SQLite",
                                "Continuous Integration",
                                "Continuous Deployment",
                                "Self-hosting",
                            ],
                        ),
                        _tech_block(
                            name="Techniques and paradigms",
                            lst=[
                                "Metaprogramming (Python)",
                                "Object-Oriented Programming (Python)",
                                "Functional Programming (Elixir, Gleam)",
                                "Snapshot testing",
                            ],
                        ),
                    ],
                ],
                h.section(class_="pb-8 border-b border-stone-200")[
                    h.h2(class_="text-2xl font-semibold mb-4")["Languages"],
                    h.div(class_="flex flex-col gap-2")[
                        h.p["French (Native)"],
                        h.p["English (TOEIC 990/990)"],
                        h.p["Croatian (Basic proficiency, actively learning)"],
                    ],
                ],
                h.div(class_="pb-8"),
            ],
        ]
    ]


def contact_page(theme: str):
    return with_topnav(theme=theme, title="Contact me", description="Contact me")[
        h.div(class_="max-w-4xl mx-auto")[
            h.div(class_="space-y-6")[
                h.p[
                    "To contact me, send me an ",
                    h.span[
                        h.a(
                            class_="link link-primary hover:font-semibold",
                            href="mailto:maxime.filippini@gmail.com",
                        )["email"]
                    ],
                    " or connect and message me on ",
                    h.span[
                        h.a(
                            class_="link link-primary hover:font-semibold",
                            href="https://www.linkedin.com/in/maxime-filippini/",
                        )["LinkedIn"]
                    ],
                    ".",
                ]
            ]
        ]
    ]
