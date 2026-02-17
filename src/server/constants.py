import os
import pathlib

from server.renderer import BlogPostRenderer

DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "./data"))
CONTENT_DIR = DATA_DIR / "content"
VERSION_FILE = DATA_DIR / ".VERSION"
TEMPLATES_DIR = DATA_DIR / "templates"

RENDERER = BlogPostRenderer()


def get_preview_content_dir(branch: str) -> pathlib.Path:
    """Get the content directory for a preview branch."""
    return DATA_DIR / f"content-preview-{branch}"


def get_preview_version_file(branch: str) -> pathlib.Path:
    """Get the version file for a preview branch."""
    return DATA_DIR / f".VERSION-preview-{branch}"
