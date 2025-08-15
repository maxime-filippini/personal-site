from pydantic import BaseModel


class PostMetadata(BaseModel):
    title: str
    slug: str
