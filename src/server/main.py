from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from r2_client import Client

from server.constants import CONTENT_DIR
from server.constants import DATA_DIR
from server.constants import RENDERER
from server.html.pages import contact_page
from server.html.pages import cv_page
from server.html.pages import home_page
from server.html.pages import posts_index
from server.posts import get_posts_from_local_dir
from server.schemas import Post
from server.settings import settings
from server.webhook import router as webhook_router

r2_client = Client(
    url=settings.CLOUDFLARE_R2_URL,
    access_key_id=settings.CLOUDFLARE_R2_ACCESS_ID,
    secret_access_key=settings.CLOUDFLARE_R2_SECRET,
)

BUCKET_NAME = "blog"

blog_posts: dict[str, Post] = get_posts_from_local_dir(
    DATA_DIR / ".dev" / "bucket", renderer=RENDERER
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount(
    "/components",
    StaticFiles(directory=str(CONTENT_DIR / "svelte/dist/components")),
    name="components",
)

app.include_router(webhook_router)


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
