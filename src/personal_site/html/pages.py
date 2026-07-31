import datetime

import htpy as h

from personal_site.html.layouts import main_layout
from personal_site.html.layouts import with_topnav
from personal_site.html.utils import fancy_link
from personal_site.posts import PostMetadata
from personal_site.settings import settings


def home_page(theme: str):
    return main_layout(theme=theme, title="Maxime Filippini")[
        h.div(
            class_="min-h-screen max-w-6xl mx-auto border-x border-base-300 flex flex-col justify-center"
        )[
            h.header(
                class_="border-y border-base-300",
            )[
                h.div(class_="max-w-4xl mx-auto px-6 py-10 sm:px-8 sm:py-14")[
                    h.p(
                        class_="text-2xl sm:text-3xl text-base-content font-semibold mb-4"
                    )["Maxime Filippini"],
                    h.h1(class_="text-3xl sm:text-5xl font-bold leading-tight")[
                        "Quantitative Risk Leader"
                    ],
                ],
            ],
            h.section(
                class_="border-b border-base-300",
            )[
                h.div(
                    class_="max-w-4xl mx-auto px-6 py-7 sm:px-8 sm:py-8 flex flex-col gap-3"
                )[
                    h.h2(class_="text-lg sm:text-xl font-semibold leading-relaxed")[
                        "Investment-fund risk · Model validation · Regulatory reporting"
                    ],
                    h.p(class_="text-sm sm:text-base text-base-content/70")[
                        "Risk technology and quantitative development"
                    ],
                ],
            ],
            h.section(
                class_="border-b border-base-300",
            )[
                h.div(
                    class_="max-w-4xl mx-auto px-6 py-8 sm:px-8 sm:py-10 text-sm sm:text-lg text-base-content/70 flex flex-col gap-4"
                )[
                    h.p[
                        "Ten years across investment-fund risk, model validation and regulatory reporting—combining quantitative depth, client leadership and hands-on technology."
                    ],
                    h.p[
                        "I help financial institutions turn quantitative risk methodologies into dependable calculations, reporting services and decision-making systems."
                    ],
                ],
            ],
            h.div(
                class_="grid grid-cols-2 sm:grid-cols-2 items-stretch w-full border-b border-base-300"
            )[
                fancy_link(
                    text="LinkedIn",
                    href="https://www.linkedin.com/in/maxime-filippini/",
                    class_="border-r border-b border-base-300",
                ),
                fancy_link(
                    text="CV",
                    href="/cv/",
                    class_="border-b sm:border-r border-base-300",
                ),
                fancy_link(
                    text="Blog",
                    href="/posts/",
                    class_="border-r border-base-300",
                ),
                fancy_link(
                    text="Contact me",
                    href="/contact/",
                ),
            ],
        ],
    ]


def _page_header(*, eyebrow: str, title: str, description: str) -> h.Renderable:
    return h.header(class_="border-b border-base-300")[
        h.div(class_="max-w-4xl mx-auto px-6 py-10 sm:px-8 sm:py-14")[
            # h.p(class_="text-sm text-base-content/60 font-semibold mb-4")[eyebrow],
            h.h1(class_="text-4xl sm:text-5xl font-bold leading-tight")[title],
            h.p(class_="mt-5 max-w-3xl text-sm sm:text-lg text-base-content/70")[
                description
            ],
        ]
    ]


def posts_index(posts: list[PostMetadata], *, theme: str):
    """Layout for the posts index page"""

    post_data = []

    for post in reversed(sorted(posts, key=lambda item: item.last_update)):
        if settings.BLOG_PROD and post.draft:
            continue

        href = f"/drafts/{post.slug}" if post.draft else f"/posts/{post.slug}"
        draft_status = [h.span["·"], h.p["Draft"]] if post.draft else []

        post_html = h.article(class_="border-b border-base-300")[
            h.div(class_="max-w-4xl mx-auto px-6 py-7 sm:px-8 sm:py-9")[
                h.div(
                    class_="flex items-center gap-3 text-xs text-base-content/60 mb-3"
                )[
                    h.p[post.posted_on.strftime("%Y-%m-%d")],
                    *draft_status,
                ],
                h.h2(class_="text-xl sm:text-2xl font-semibold mb-3")[
                    h.a(
                        href=href,
                        class_="link link-hover",
                        hx_boost="true",
                    )[post.title]
                ],
                h.p(class_="text-sm sm:text-base text-base-content/70 leading-relaxed")[
                    post.abstract
                ],
            ]
        ]

        post_data.append(post_html)

    return with_topnav(
        theme=theme,
        title="Blog",
        description="Writing on quantitative risk, risk technology, and software systems.",
    )[
        _page_header(
            eyebrow="Blog",
            title="Blog",
            description="On topics such as quantitative risk, risk technology, and practical software systems.",
        ),
        *(
            post_data
            if post_data
            else [
                h.div(class_="border-b border-base-300")[
                    h.p(class_="max-w-4xl mx-auto px-6 py-8 text-base-content/70")[
                        "No posts found."
                    ]
                ]
            ]
        ),
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

    return h.article(class_="grid sm:grid-cols-[10rem_1fr] gap-3 sm:gap-8 py-6")[
        h.p(class_="text-sm text-base-content/60")[f"{start} – {end}"],
        h.div[
            h.p(class_="text-lg sm:text-xl font-semibold")[company],
            h.p(class_="text-sm font-semibold text-base-content/70 mb-4")[grade],
            h.div(class_="text-sm sm:text-base text-base-content/70 leading-relaxed")[
                children
            ],
        ],
    ]


@h.with_children
def _edu_block(
    children: h.Node,
    *,
    year: int,
    diploma: str,
    institution: str,
) -> h.Renderable:
    return h.article(class_="grid sm:grid-cols-[10rem_1fr] gap-3 sm:gap-8 py-6")[
        h.p(class_="text-sm text-base-content/60")[year],
        h.div[
            h.p(class_="text-lg sm:text-xl font-semibold")[diploma],
            h.p(class_="text-sm font-semibold text-base-content/70 mb-4")[institution],
            h.div(class_="text-sm sm:text-base text-base-content/70 leading-relaxed")[
                children
            ],
        ],
    ]


@h.with_children
def _tech_block(
    children: h.Node,
    *,
    name: str,
    lst: list[str],
) -> h.Renderable:
    *lst, last = lst
    return h.div(class_="grid sm:grid-cols-[14rem_1fr] gap-3 sm:gap-8 py-5")[
        h.h3(class_="text-base font-semibold")[name],
        h.div(class_="flex flex-row flex-wrap text-sm text-base-content/70")[
            *[h.p(class_="after:content-['•'] after:mx-3")[item] for item in lst],
            h.p[last],
        ],
    ]


@h.with_children
def _cv_section(children: h.Node, *, title: str) -> h.Renderable:
    return h.section(class_="border-b border-base-300")[
        h.div(class_="max-w-4xl mx-auto px-6 py-8 sm:px-8 sm:py-10")[
            h.h2(class_="text-2xl sm:text-3xl font-semibold mb-4")[title],
            children,
        ]
    ]


def cv_page(theme: str):
    return with_topnav(
        title="Maxime Filippini — CV",
        theme=theme,
        description="Quantitative risk leadership, model validation, regulatory reporting, and risk technology experience.",
    )[
        _page_header(
            eyebrow="Curriculum vitae",
            title="Maxime Filippini",
            description="Quantitative Risk Leader · Investment-fund risk · Model validation · Regulatory reporting · Risk technology",
        ),
        _cv_section(title="Experience")[
            h.div(class_="divide-y divide-base-300")[
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
                        h.li["Market risk for the trading book (e.g. Value-at-Risk);"],
                        h.li["Valuation of derivatives and structured products;"],
                        h.li["Initial margin;"],
                        h.li["Economic capital models (ICAAP);"],
                        h.li["IRRBB-related models (e.g. Non-Maturity Deposits);"],
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
            ]
        ],
        _cv_section(title="Education")[
            h.div(class_="divide-y divide-base-300")[
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
            ]
        ],
        _cv_section(title="Technologies")[
            h.div(class_="divide-y divide-base-300")[
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
                    lst=["Git", "Terminal utilities (UNIX)", "Docker"],
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
            ]
        ],
        _cv_section(title="Languages")[
            h.div(class_="grid sm:grid-cols-3 gap-3 text-sm text-base-content/70")[
                h.p["French (Native)"],
                h.p["English (TOEIC 990/990)"],
                h.p["Croatian (Basic proficiency, actively learning)"],
            ]
        ],
    ]


def contact_page(theme: str):
    return with_topnav(
        theme=theme,
        title="Contact Maxime Filippini",
        description="Contact Maxime Filippini about quantitative risk, model validation, regulatory reporting, or risk technology.",
    )[
        _page_header(
            eyebrow="Contact",
            title="Let’s talk",
            description="For conversations about quantitative risk, model validation, regulatory reporting, or risk technology.",
        ),
        h.div(class_="grid grid-cols-2 border-b border-base-300")[
            fancy_link(
                text="Email",
                href="mailto:maxime.filippini@gmail.com",
                class_="border-r border-base-300",
            ),
            fancy_link(
                text="LinkedIn",
                href="https://www.linkedin.com/in/maxime-filippini/",
            ),
        ],
    ]
