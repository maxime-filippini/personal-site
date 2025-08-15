from typing import List

import frontmatter

from server.constants import CONTENT_DIR
from server.schemas import PostMetadata


def discover_posts() -> List[PostMetadata]:
    """Discover all posts in the posts directory"""
    posts_dir = CONTENT_DIR / "posts"

    if not posts_dir.exists():
        return []

    posts = []
    for md_file in posts_dir.glob("*.md"):
        try:
            with open(md_file, encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Create metadata, using filename as fallback for slug
            metadata_dict = dict(post.metadata)
            if "slug" not in metadata_dict:
                metadata_dict["slug"] = md_file.stem
            if "title" not in metadata_dict:
                metadata_dict["title"] = md_file.stem.replace("-", " ").title()

            metadata = PostMetadata(**{k: str(v) for k, v in metadata_dict.items()})
            posts.append(metadata)
        except Exception:
            # Skip files that can't be parsed
            continue

    # Sort by title for now (could add date sorting later)
    posts.sort(key=lambda p: p.title)
    return posts
