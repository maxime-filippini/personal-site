# webhook.py (can live in the same app)
import hashlib
import hmac
import json
import os
import pathlib
import subprocess

from fastapi import APIRouter
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request

from server.constants import CONTENT_DIR
from server.constants import RENDERER
from server.constants import VERSION_FILE
from server.utils import current_sha
from server.utils import get_or_render
from server.utils import invalidate
from server.utils import run

router = APIRouter()
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "change-me")  # set in env


def content_paths_to_slugs(paths: list[str]) -> list[str]:
    # map repo paths like "content/posts/my-thing.md" -> "posts/my-thing"
    slugs = []
    for p in paths:
        if not p.endswith(".md"):
            continue

        rel = (
            pathlib.Path(p).relative_to(CONTENT_DIR.name)
            if p.startswith(f"{CONTENT_DIR.name}/")
            else pathlib.Path(p)
        )
        slugs.append(str(rel.with_suffix("")))
    return slugs


@router.post("/webhook/publish")
async def webhook_publish(request: Request, x_signature_256: str | None = Header(None)):
    body = await request.body()

    if not x_signature_256 or not x_signature_256.startswith("sha256="):
        raise HTTPException(401, "Missing signature")

    expected = (
        "sha256=" + hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    )

    if not hmac.compare_digest(expected, x_signature_256):
        raise HTTPException(401, "Bad signature")

    payload = json.loads(body.decode())
    new_sha = payload.get("sha")  # provided by your Action (see below)
    if not new_sha:
        raise HTTPException(400, "Missing sha")

    # Read current version before updating
    old_sha = current_sha() if VERSION_FILE.exists() else None

    # Pull fast‑forward to the new SHA
    try:
        run("git fetch --all --prune", cwd=CONTENT_DIR)
        run(f"git checkout --detach {new_sha}", cwd=CONTENT_DIR)

    except subprocess.CalledProcessError as e:
        raise HTTPException(500, f"git error: {e}")

    # Compute changed Markdown files (old..new); fall back to invalidating all
    changed_slugs: list[str] = []
    if old_sha:
        try:
            diff = run(f"git diff --name-only {old_sha}..{new_sha}", cwd=CONTENT_DIR)
            changed = [p.strip() for p in diff.splitlines() if p.strip()]
            changed_slugs = content_paths_to_slugs(changed)
        except Exception:
            pass

    # Persist the active sha
    VERSION_FILE.write_text(new_sha)

    # Invalidate cache (only changed if we could compute them; else all)
    invalidate(changed_slugs or None)

    # Optional: warm caches for changed slugs
    for slug in changed_slugs[:20]:  # cap to keep it quick
        try:
            md_path = (CONTENT_DIR / slug).with_suffix(".md")
            await get_or_render(RENDERER, slug, new_sha, md_path)
        except Exception:
            pass

    return {"ok": True, "old": old_sha, "new": new_sha, "invalidated": changed_slugs}
