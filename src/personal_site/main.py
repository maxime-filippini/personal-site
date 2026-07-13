import pathlib
import secrets
from typing import Annotated

import click
import uvicorn
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles

from personal_site import posts
from personal_site.constants import BLOG_THEME
from personal_site.constants import BUCKET_NAME
from personal_site.html.pages import contact_page
from personal_site.html.pages import cv_page
from personal_site.html.pages import home_page
from personal_site.html.pages import posts_index
from personal_site.r2_client import Client
from personal_site.renderer import BlogPostRenderer
from personal_site.settings import Settings
from personal_site.settings import settings

RENDERER = BlogPostRenderer()

R2_CLIENT = Client(
    url=settings.CLOUDFLARE_R2_URL,
    access_key_id=settings.CLOUDFLARE_R2_ACCESS_ID,
    secret_access_key=settings.CLOUDFLARE_R2_SECRET,
)


def app_factory(settings: Settings) -> FastAPI:
    publish_security = HTTPBearer(auto_error=False)

    app = FastAPI()
    app.mount("/static", StaticFiles(directory="static"), name="static")

    async def require_publish_token(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None, Depends(publish_security)
        ],
    ) -> None:
        if credentials is None or not secrets.compare_digest(
            credentials.credentials, settings.PUBLISH_TOKEN
        ):
            raise HTTPException(
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )

    if settings.BLOG_PROD:
        click.echo(click.style("\nBlog running in PROD mode...", fg="green"))

        repository = posts.Bucket(
            client=R2_CLIENT, bucket_name=BUCKET_NAME, renderer=RENDERER
        )

        click.echo(
            click.style(
                f"Assets are served from R2 bucket at: {settings.R2_PUBLIC_URL}",
                fg="yellow",
            )
        )

        @app.get("/assets/{slug:path}")
        async def asset_redirect(slug: str):
            print("Redirecting to R2 bucket...")
            return RedirectResponse(url=f"{settings.R2_PUBLIC_URL}/assets/{slug}")

    else:
        click.echo(click.style("\nBlog running in DEV mode...", fg="green"))

        repository = posts.LocalDirectory(
            settings.BLOG_CONTENT_DIR / "posts", renderer=RENDERER
        )

        click.echo(
            click.style(
                f"Assets are served from '{settings.BLOG_CONTENT_DIR}/assets/'",
                fg="yellow",
            )
        )
        app.mount(
            "/assets",
            StaticFiles(directory=settings.BLOG_CONTENT_DIR / "assets"),
            name="assets",
        )

    repository.collect_posts()

    click.echo("Posts loaded:")

    for post in repository.posts.keys():
        click.echo(post)

    @app.get("/")
    async def show_first_page():
        return HTMLResponse(home_page(theme=BLOG_THEME))

    @app.get("/contact/")
    async def show_contact_me_page():
        return HTMLResponse(contact_page(theme=BLOG_THEME))

    @app.get("/posts/")
    async def show_posts_index():
        metadatas = [p.metadata for p in repository.posts.values()]
        return HTMLResponse(posts_index(metadatas, theme=BLOG_THEME))

    @app.get("/cv/")
    async def show_cv_page():
        return HTMLResponse(cv_page(theme=BLOG_THEME))

    @app.get("/posts/{slug:path}")
    async def published_post(slug: str, request: Request):
        res = next(
            (
                post
                for post in repository.posts.values()
                if post.metadata.slug == slug and not post.metadata.draft
            ),
            None,
        )

        if res is None:
            raise HTTPException(404)

        return HTMLResponse(res.html)

    @app.get("/drafts/{slug:path}")
    async def draft_post(slug: str, request: Request):
        res = next(
            (
                post
                for post in repository.posts.values()
                if post.metadata.slug == slug and post.metadata.draft
            ),
            None,
        )

        if res is None:
            raise HTTPException(404)

        return HTMLResponse(res.html)

    @app.post("/posts/update/{slug:path}")
    async def update_post(
        slug: str, _: Annotated[None, Depends(require_publish_token)]
    ):
        repository.update_post(slug)

    @app.post("/posts/update")
    async def update_all_posts(
        _: Annotated[None, Depends(require_publish_token)],
    ):
        repository.update_all_posts()

    return app


app = app_factory(settings=settings)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
