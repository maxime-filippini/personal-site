import pathlib

import click
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from r2_client import Client

from personal_site.constants import RENDERER
from personal_site.html.pages import contact_page
from personal_site.html.pages import cv_page
from personal_site.html.pages import home_page
from personal_site.html.pages import posts_index
from personal_site.posts import get_posts_from_local_dir
from personal_site.schemas import Post
from personal_site.settings import Settings
from personal_site.settings import settings

r2_client = Client(
    url=settings.CLOUDFLARE_R2_URL,
    access_key_id=settings.CLOUDFLARE_R2_ACCESS_ID,
    secret_access_key=settings.CLOUDFLARE_R2_SECRET,
)

BUCKET_NAME = "blog"

blog_posts: dict[str, Post] = get_posts_from_local_dir(
    pathlib.Path(".dev") / "bucket" / "posts", renderer=RENDERER
)


def app_factory(settings: Settings) -> FastAPI:
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="static"), name="static")

    if settings.BLOG_PROD:
        click.echo(click.style("\nBlog running in PROD mode...", fg="green"))
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
        click.echo(
            click.style("Assets are served from '.dev/bucket/assets/'", fg="yellow")
        )
        app.mount("/assets", StaticFiles(directory=".dev/bucket/assets"), name="assets")

    @app.get("/")
    async def show_first_page():
        return HTMLResponse(home_page(theme="lofi"))

    @app.get("/contact/")
    async def show_contact_me_page():
        return HTMLResponse(contact_page(theme="lofi"))

    @app.get("/posts/")
    async def show_posts_index():
        metadatas = [p.metadata for p in blog_posts.values()]
        return HTMLResponse(posts_index(metadatas, theme="lofi"))

    @app.get("/cv/")
    async def show_cv_page():
        return HTMLResponse(cv_page(theme="lofi"))

    @app.get("/posts/{slug:path}")
    async def markdown_page(slug: str, request: Request):
        res = next(
            (post for post in blog_posts.values() if post.metadata.slug == slug),
            None,
        )

        if res is None or res.metadata.draft:
            raise HTTPException(404)

        return HTMLResponse(res.html)

    @app.post("/posts/update/{slug:path}")
    async def update_post(slug: str):
        pass

    return app


app = app_factory(settings=settings)
