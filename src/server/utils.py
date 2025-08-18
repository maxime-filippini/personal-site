import asyncio
import hashlib
import pathlib
import shlex
import subprocess

from cachetools import LRUCache

from server.constants import VERSION_FILE
from server.renderer import BaseRenderer
from server.schemas import PostMetadata

cache: LRUCache[str, tuple[str, str, PostMetadata]] = LRUCache(maxsize=2000)
locks: dict[str, asyncio.Lock] = {}


def current_sha(version_file: pathlib.Path = VERSION_FILE) -> str:
    return version_file.read_text().strip()


def key(slug: str, sha: str, branch: str = "main") -> str:
    return f"{branch}::{slug}::{sha}"


def etag_of(html: str) -> str:
    return hashlib.sha256(html.encode("utf-8")).hexdigest()[:16]


async def get_or_render(
    renderer: BaseRenderer,
    slug: str,
    sha: str,
    md_path: pathlib.Path,
    branch: str = "main",
) -> tuple[str, str, PostMetadata]:
    k = key(slug, sha, branch)

    if k in cache:
        return cache[k]

    lock = locks.setdefault(k, asyncio.Lock())

    async with lock:
        if k in cache:
            return cache[k]

        # Use the new renderer's render_content method
        html, metadata = renderer.render_content(md_path)
        etag = etag_of(html)
        cache[k] = (etag, html, metadata)
        return etag, html, metadata


def invalidate(slugs: list[str] | None = None, branch: str = "main"):
    if not slugs:
        if branch == "main":
            cache.clear()
        else:
            # Clear only this preview branch
            for k in list(cache.keys()):
                if k.startswith(f"{branch}::"):
                    cache.pop(k, None)
        return
    for slug in slugs:
        # remove all versions for that slug on this branch
        for k in list(cache.keys()):
            if k.startswith(f"{branch}::{slug}::"):
                cache.pop(k, None)


def run(cmd: str, cwd: pathlib.Path | None = None) -> str:
    return subprocess.check_output(
        shlex.split(cmd), cwd=str(cwd) if cwd else None
    ).decode()
