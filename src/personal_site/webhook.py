# webhook.py (can live in the same app)
import hashlib
import hmac
import json
import logging
import os
import pathlib
import subprocess

from fastapi import APIRouter
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request

from personal_site.constants import CONTENT_DIR
from personal_site.constants import RENDERER
from personal_site.constants import VERSION_FILE
from personal_site.constants import get_preview_content_dir
from personal_site.constants import get_preview_version_file
from personal_site.utils import current_sha
from personal_site.utils import get_or_render
from personal_site.utils import invalidate
from personal_site.utils import run

router = APIRouter()
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "change-me")  # set in env


def content_paths_to_slugs(
    paths: list[str], content_dir_name: str = "content"
) -> list[str]:
    # map repo paths like "content/posts/my-thing.md" -> "posts/my-thing"
    slugs = []
    for p in paths:
        if not p.endswith(".md"):
            continue

        rel = (
            pathlib.Path(p).relative_to(content_dir_name)
            if p.startswith(f"{content_dir_name}/")
            else pathlib.Path(p)
        )
        slugs.append(str(rel.with_suffix("")))
    return slugs


def extract_branch_info(ref: str) -> tuple[bool, str | None]:
    """Extract branch info from GitHub ref.

    Returns (is_preview_branch, branch_name_or_None)
    """
    if not ref.startswith("refs/heads/"):
        return False, None

    branch_name = ref.removeprefix("refs/heads/")

    if branch_name.startswith("preview/"):
        return True, branch_name.removeprefix("preview/")

    return branch_name == "main", None


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
    new_sha = payload.get("sha")
    ref = payload.get("ref", "")

    print(f"Full webhook payload: {payload}")
    print(f"Webhook received: sha={new_sha}, ref={ref}")
    logging.info(f"Full webhook payload: {payload}")
    logging.info(f"Webhook received: sha={new_sha}, ref={ref}")

    if not new_sha:
        raise HTTPException(400, "Missing sha")

    # Extract branch information
    is_valid_branch, preview_branch = extract_branch_info(ref)

    print(
        f"Branch extraction: is_valid_branch={is_valid_branch}, preview_branch={preview_branch}"
    )
    logging.info(
        f"Branch extraction: is_valid_branch={is_valid_branch}, preview_branch={preview_branch}"
    )

    if not is_valid_branch:
        response = {"ok": True, "message": f"Ignoring push to {ref}"}
        print(f"Ignoring branch: {response}")
        logging.info(f"Ignoring branch: {response}")
        return response

    # Determine target directories
    if preview_branch:
        content_dir = get_preview_content_dir(preview_branch)
        version_file = get_preview_version_file(preview_branch)
        branch_name = f"preview/{preview_branch}"
        cache_branch = f"preview-{preview_branch}"
    else:
        content_dir = CONTENT_DIR
        version_file = VERSION_FILE
        branch_name = "main"
        cache_branch = "main"

    # Ensure content directory exists
    content_dir.mkdir(exist_ok=True)

    # Read current version before updating
    old_sha = current_sha(version_file) if version_file.exists() else None

    # Initialize or update the repository
    if not (content_dir / ".git").exists():
        # Clone the repository for the first time
        try:
            repo_url = os.environ.get("REPO_URL")
            if not repo_url:
                raise HTTPException(500, "REPO_URL not configured")

            run(f"git clone --branch {branch_name} {repo_url} {content_dir}")
            run(f"git checkout --detach {new_sha}", cwd=content_dir)
        except subprocess.CalledProcessError as e:
            raise HTTPException(500, f"git clone error: {e}")
    else:
        # Update existing repository
        try:
            run("git fetch --all --prune", cwd=content_dir)
            run(f"git checkout --detach {new_sha}", cwd=content_dir)
        except subprocess.CalledProcessError as e:
            raise HTTPException(500, f"git error: {e}")

    # Compute changed Markdown files (old..new); fall back to invalidating all
    changed_slugs: list[str] = []
    if old_sha:
        try:
            diff = run(f"git diff --name-only {old_sha}..{new_sha}", cwd=content_dir)
            changed = [p.strip() for p in diff.splitlines() if p.strip()]
            changed_slugs = content_paths_to_slugs(changed, content_dir.name)
        except Exception:
            pass

    # Persist the active sha
    version_file.write_text(new_sha)

    # Invalidate cache (only changed if we could compute them; else all)
    invalidate(changed_slugs or None, cache_branch)

    # Optional: warm caches for changed slugs
    for slug in changed_slugs[:20]:  # cap to keep it quick
        try:
            md_path = (content_dir / slug).with_suffix(".md")
            await get_or_render(RENDERER, slug, new_sha, md_path, cache_branch)
        except Exception:
            pass

    output = {
        "ok": True,
        "branch": branch_name,
        "preview": preview_branch,
        "old": old_sha,
        "new": new_sha,
        "invalidated": changed_slugs,
        "content_dir": str(content_dir),
        "version_file": str(version_file),
        "ref": ref,
    }

    print(f"Webhook processed: {output}")
    logging.info(f"Webhook processed: {output}")

    return output
