import dataclasses
import datetime

import htpy as h
from pydantic import BaseModel
from pydantic import ConfigDict


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
