from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID


class Source(BaseModel):
    name: str
    url: HttpUrl


class Entity(BaseModel):
    id: UUID
    entity_type: str
    name: str
    description: str = ""
    url: HttpUrl
    categories: List[str] = Field(default_factory=list)
    source: Source
    metadata: dict = Field(default_factory=dict)


class RepositoryMetadata(BaseModel):
    stars: int = 0
    primary_language: Optional[str] = None
    last_updated: Optional[str] = None