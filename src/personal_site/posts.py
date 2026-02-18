import abc
import dataclasses
import datetime
import pathlib
from typing import TYPE_CHECKING

import frontmatter
import htpy as h
from pydantic import BaseModel
from pydantic import ConfigDict
from r2_client import Client

if TYPE_CHECKING:
    from personal_site.renderer import BaseRenderer


class PostMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    slug: str  # Auto-generated from filename, no need to specify in frontmatter
    posted_on: datetime.date
    last_update: datetime.date

    abstract: str
    draft: bool = True


@dataclasses.dataclass
class Post:
    metadata: PostMetadata
    html: h.Renderable


class PostRepository(abc.ABC):
    posts: dict[str, Post]
    renderer: BaseRenderer

    def __init__(self) -> None:
        self.posts = {}

    @abc.abstractmethod
    def collect_posts(self) -> None: ...

    @abc.abstractmethod
    def update_post(self, slug: str) -> None: ...

    def update_all_posts(self) -> None:
        for slug in self.posts.keys():
            self.update_post(slug)

    def process_post_markdown(self, slug: str, markdown: str) -> Post:
        post = frontmatter.loads(markdown)
        metadata = PostMetadata(slug=slug, **dict(post.metadata))  # type: ignore

        return Post(
            metadata=metadata,
            html=self.renderer.to_html(post.content, metadata=metadata),
        )


class Bucket(PostRepository):
    def __init__(
        self, client: Client, bucket_name: str, renderer: BaseRenderer
    ) -> None:
        self.client = client
        self.bucket_name = bucket_name
        self.renderer = renderer

        super().__init__()

    def update_post(self, slug: str) -> None:
        obj = self.client.get_object(
            bucket_name=self.bucket_name, object_name=f"posts/{slug}.md"
        )

        read_obj = self.client.read_object(obj)

        self.posts[slug] = self.process_post_markdown(slug=slug, markdown=read_obj.body)

    def collect_posts(self) -> None:
        objs = [
            self.client.read_object(obj)
            for obj in self.client.list_objects(self.bucket_name)
            if obj.key.endswith(".md")
        ]
        posts: dict[str, Post] = {}

        for obj in objs:
            post = self.process_post_markdown(
                slug=obj.object_.key.removesuffix(".md"), markdown=obj.body
            )
            posts[post.metadata.slug] = post

        self.posts = posts


class LocalDirectory(PostRepository):
    def __init__(self, path: pathlib.Path, renderer: BaseRenderer) -> None:
        self.path = path
        self.renderer = renderer
        super().__init__()

    def update_post(self, slug: str):
        path = self.path / f"{slug}.md"

        with path.open() as fd:
            markdown = fd.read()

        self.posts[slug] = self.process_post_markdown(slug=slug, markdown=markdown)

    def collect_posts(self) -> None:
        posts: dict[str, Post] = {}

        for file in self.path.glob("*.md"):
            with open(file, "r") as fd:
                markdown = fd.read()

            post = frontmatter.loads(markdown)
            slug = file.name.removesuffix(".md")

            metadata_dict = dict(post.metadata)
            metadata_dict["slug"] = slug
            metadata = PostMetadata(**metadata_dict)  # type: ignore

            post = Post(
                metadata=metadata,
                html=self.renderer.to_html(post.content, metadata=metadata),
            )

            posts[metadata.slug] = post

        self.posts = posts
