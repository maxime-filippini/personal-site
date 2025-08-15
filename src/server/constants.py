import os
import pathlib

from server.renderer import TestRenderer

DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "/data"))
CONTENT_DIR = DATA_DIR / "content"
VERSION_FILE = DATA_DIR / ".VERSION"
TEMPLATES_DIR = DATA_DIR / "templates"

RENDERER = TestRenderer()
