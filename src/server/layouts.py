import htpy as h
from markupsafe import Markup

from server.schemas import PostMetadata


def posthog():
    return h.script()[
        Markup("""
    !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init Re Ms Fs Pe Rs Cs capture Ve calculateEventProperties Ds register register_once register_for_session unregister unregister_for_session zs getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSurveysLoaded onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey canRenderSurveyAsync identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty Ls As createPersonProfile Ns Is Us opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing is_capturing clear_opt_in_out_capturing Os debug I js getPageViewId captureTraceFeedback captureTraceMetric".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
    posthog.init('phc_3tb9L4xZN6rEgGXV9cgo4f2HWomZgZ6ssFLjUM7HKpY', {
        api_host: 'https://eu.i.posthog.com',
        defaults: '2025-05-24',
        person_profiles: 'always', 
    })               
""")
    ]


@h.with_children
def main_layout(children: h.Node, *, theme: str, title: str):
    return h.html(data_theme=theme, lang="en")[
        h.head[
            h.meta(charset="UTF-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            h.title[title],
            h.link(rel="stylesheet", href="/static/output.css"),
            posthog(),
            h.script(src="/static/htmx.min.js"),
        ],
        h.body(class_="p-8 font-mono bg-stone-50 h-screen")[children],
    ]


@h.with_children
def post_layout(children: h.Node, *, theme: str, metadata: PostMetadata):
    return main_layout(theme=theme, title=metadata.title)[children]


def link_arrow():
    return Markup(r"""
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="size-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 19.5 15-15m0 0H8.25m11.25 0v11.25" />
</svg>
""")


def fancy_link(emoji: str, text: str, href: str):
    return (
        h.a(
            class_="text-xl border-r border-black px-4 w-1/2 group cursor-pointer flex gap-2 items-center justify-center",
            href=href,
            hx_boost="true",
        )[
            h.span[emoji],
            h.span(
                class_="group-hover:underline group-hover:font-bold underline-offset-8 duration-100"
            )[text],
            h.div(class_="group-hover:stroke-2 duration-100")[link_arrow()],
        ],
    )


def first_page(theme: str):
    return main_layout(theme=theme, title="Maxime Filippini")[
        h.div(
            class_="flex flex-col h-screen items-center justify-center gap-8 max-w-2xl mx-auto"
        )[
            h.h1(class_="text-5xl font-bold border border-2 border-black p-8 bg-white")[
                "Maxime Filippini"
            ],
            h.div(class_="flex w-full justify-center")[
                h.h2(class_="text-2xl border-r border-black px-4 w-1/2 text-center")[
                    "Risk manager"
                ],
                h.h2(class_="text-2xl px-4 w-1/2 text-center")["Software developer"],
            ],
            h.div(class_="flex w-full justify-center")[
                fancy_link(emoji="🤓", text="My CV", href="/cv/"),
                fancy_link(emoji="👨🏼‍💻", text="My blog", href="/blog/"),
            ],
        ],
    ]


def posts_index_layout(posts: list[PostMetadata], *, theme: str):
    """Layout for the posts index page"""
    return main_layout(theme=theme, title="Posts")[
        h.div(class_="max-w-4xl mx-auto")[
            h.h1(class_="text-4xl font-bold mb-8")["Posts"],
            h.div(class_="space-y-6")[
                [
                    h.article(class_="border-b border-base-300 pb-6")[
                        h.h2(class_="text-2xl font-semibold mb-2")[
                            h.a(
                                href=f"/posts/{post.slug}",
                                class_="link link-hover text-primary",
                            )[post.title]
                        ],
                    ]
                    for post in posts
                ]
            ]
            if posts
            else h.p(class_="text-base-content/70")["No posts found."],
        ]
    ]


def cv_page():
    return h.p()["hi"]
