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
from server.constants import VERSION_FILE
from server.constants import get_preview_content_dir
from server.constants import get_preview_version_file
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
    StaticFiles(directory="../../../data/content/svelte/dist/components"),
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


@app.get("/api/routes")
async def list_routes():
    from server.constants import DATA_DIR
    
    routes = {
        "main": {},
        "previews": {}
    }
    
    # Main content routes
    if CONTENT_DIR.exists():
        for md_file in CONTENT_DIR.rglob("*.md"):
            slug = str(md_file.relative_to(CONTENT_DIR).with_suffix(""))
            routes["main"][slug] = f"/{slug}"
    
    # Preview branch routes
    for preview_dir in DATA_DIR.glob("content-preview-*"):
        if preview_dir.is_dir():
            branch_name = preview_dir.name.removeprefix("content-preview-")
            routes["previews"][branch_name] = {}
            
            for md_file in preview_dir.rglob("*.md"):
                slug = str(md_file.relative_to(preview_dir).with_suffix(""))
                routes["previews"][branch_name][slug] = f"/_preview/{branch_name}/{slug}"
    
    return routes


@app.get("/api/debug")
async def debug_info():
    from server.constants import DATA_DIR
    
    info = {
        "data_dir": str(DATA_DIR),
        "main_content": {
            "exists": CONTENT_DIR.exists(),
            "path": str(CONTENT_DIR),
            "version_file": str(VERSION_FILE),
            "version_exists": VERSION_FILE.exists()
        },
        "preview_branches": []
    }
    
    # Check all preview directories
    for preview_dir in DATA_DIR.glob("content-preview-*"):
        branch_name = preview_dir.name.removeprefix("content-preview-")
        version_file = get_preview_version_file(branch_name)
        
        branch_info = {
            "branch": branch_name,
            "content_dir": str(preview_dir),
            "exists": preview_dir.exists(),
            "version_file": str(version_file),
            "version_exists": version_file.exists(),
            "file_count": len(list(preview_dir.rglob("*.md"))) if preview_dir.exists() else 0
        }
        info["preview_branches"].append(branch_info)
    
    return info


@app.get("/_preview/{branch}/{slug:path}")
async def preview_markdown_page(branch: str, slug: str, request: Request):
    preview_content_dir = get_preview_content_dir(branch)
    preview_version_file = get_preview_version_file(branch)

    if not preview_content_dir.exists():
        raise HTTPException(404, f"Preview branch '{branch}' not found")

    if not preview_version_file.exists():
        raise HTTPException(404, f"Preview branch '{branch}' not initialized")

    sha = current_sha(preview_version_file)
    md_path = (preview_content_dir / slug).with_suffix(".md")

    if not md_path.exists():
        raise HTTPException(404)

    etag, html, metadata = await get_or_render(
        RENDERER, slug, sha, md_path, f"preview-{branch}"
    )

    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304)

    return HTMLResponse(
        html,
        headers={
            "Cache-Control": "public, max-age=60, stale-while-revalidate=30",  # Shorter cache for previews
            "ETag": etag,
        },
    )


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
