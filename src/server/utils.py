import asyncio
import hashlib
import pathlib
import shlex
import subprocess

from cachetools import LRUCache

from server.constants import VERSION_FILE
from server.renderer import Renderer

cache: LRUCache[str, tuple[str, str]] = LRUCache(maxsize=2000)
locks: dict[str, asyncio.Lock] = {}


def current_sha() -> str:
    return VERSION_FILE.read_text().strip()


def key(slug: str, sha: str) -> str:
    return f"{slug}::{sha}"


def etag_of(html: str) -> str:
    return hashlib.sha256(html.encode("utf-8")).hexdigest()[:16]


async def get_or_render(
    renderer: Renderer, slug: str, sha: str, md_path: pathlib.Path
) -> tuple[str, str]:
    k = key(slug, sha)

    if k in cache:
        return cache[k]

    lock = locks.setdefault(k, asyncio.Lock())

    async with lock:
        if k in cache:
            return cache[k]

        # Use the new renderer's render_content method
        html = renderer.render_content(md_path)
        etag = etag_of(html)
        cache[k] = (etag, html)
        return etag, html


def invalidate(slugs: list[str] | None = None):
    if not slugs:
        cache.clear()
        return
    for slug in slugs:
        # remove all versions for that slug
        for k in list(cache.keys()):
            if k.startswith(f"{slug}::"):
                cache.pop(k, None)


def run(cmd: str, cwd: pathlib.Path | None = None) -> str:
    return subprocess.check_output(
        shlex.split(cmd), cwd=str(cwd) if cwd else None
    ).decode()
