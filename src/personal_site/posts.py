import pathlib

import frontmatter
from r2_client import Client

from personal_site.renderer import BaseRenderer
from personal_site.schemas import Post
from personal_site.schemas import PostMetadata


def get_posts_from_bucket(
    client: Client, bucket: str, renderer: BaseRenderer
) -> dict[str, Post]:
    objs = [client.read_object(obj) for obj in client.list_objects(bucket)]
    posts: dict[str, Post] = {}

    for obj in objs:
        etag = obj.object_.etag
        post = frontmatter.loads(obj.body)
        metadata_dict = dict(post.metadata)
        metadata_dict["slug"] = obj.object_.key.removesuffix(".md")
        metadata = PostMetadata(**metadata_dict)  # type: ignore

        posts[etag] = Post(
            metadata=metadata, html=renderer.to_html(post.content, metadata=metadata)
        )

    return posts


def get_posts_from_local_dir(
    path_dir: pathlib.Path, renderer: BaseRenderer
) -> dict[str, Post]:
    posts: dict[str, Post] = {}

    for file in path_dir.glob("*.md"):
        with open(file, "r") as fd:
            markdown = fd.read()

        post = frontmatter.loads(markdown)
        slug = file.name.removesuffix(".md")

        metadata_dict = dict(post.metadata)
        metadata_dict["slug"] = slug
        metadata = PostMetadata(**metadata_dict)  # type: ignore

        posts[slug] = Post(
            metadata=metadata, html=renderer.to_html(post.content, metadata=metadata)
        )

    return posts


# def discover_posts() -> List[PostMetadata]:
#     """Discover all posts in the posts directory"""
#     posts_dir = CONTENT_DIR / "posts"

#     if not posts_dir.exists():
#         return []

#     posts = []
#     for md_file in posts_dir.glob("*.md"):
#         try:
#             with open(md_file, encoding="utf-8") as f:
#                 post = frontmatter.load(f)

#             # Create metadata, auto-generating slug from filename
#             metadata_dict = dict(post.metadata)
#             metadata_dict["slug"] = md_file.stem  # Always use filename as slug
#             if "title" not in metadata_dict:
#                 metadata_dict["title"] = md_file.stem.replace("-", " ").title()

#             metadata = PostMetadata(**{k: str(v) for k, v in metadata_dict.items()})  # type: ignore

#             if metadata.draft:
#                 metadata.title += " [DRAFT]"

#             posts.append(metadata)
#         except Exception:
#             # Skip files that can't be parsed
#             continue

#     # Sort by title for now (could add date sorting later)
#     posts.sort(key=lambda p: p.title)
#     return posts
