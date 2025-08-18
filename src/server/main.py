import debugpy
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from server.config import settings
from server.constants import CONTENT_DIR
from server.constants import RENDERER
from server.html.pages import cv_page
from server.html.pages import home_page
from server.html.pages import posts_index
from server.posts import discover_posts
from server.utils import current_sha
from server.utils import get_or_render
from server.webhook import router as webhook_router

# Enable debugger
try:
    debugpy.listen(("0.0.0.0", 5678))
    print("Debugger listening on port 5678...")
except RuntimeError as e:
    if "Address already in use" in str(e):
        print("Debugger port 5678 already in use, skipping debugger setup")
    else:
        raise

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount(
    "/components",
    StaticFiles(directory="data/content/svelte/dist/components"),
    name="components",
)


print(settings)
app.include_router(webhook_router)


@app.get("/")
async def show_first_page():
    return HTMLResponse(home_page(theme="lofi"))


@app.get("/posts/")
async def show_posts_index():
    posts = discover_posts()
    return HTMLResponse(posts_index(posts, theme="lofi"))


@app.get("/cv/")
async def show_cv_page():
    return HTMLResponse(cv_page(theme="lofi"))


@app.get("/{slug:path}")
async def markdown_page(slug: str, request: Request):
    sha = current_sha()
    md_path = (CONTENT_DIR / slug).with_suffix(".md")

    if not md_path.exists():
        raise HTTPException(404)

    etag, html, metadata = await get_or_render(RENDERER, slug, sha, md_path)

    if metadata.draft and settings.BLOG_PROD:
        raise HTTPException(404)

    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304)

    return HTMLResponse(
        html,
        headers={
            "Cache-Control": "public, max-age=600, stale-while-revalidate=300",
            "ETag": etag,
        },
    )
