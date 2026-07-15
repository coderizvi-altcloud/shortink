"""Pydantic schemas for shortlink request/response validation."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ShortlinkCreate(BaseModel):
    url: Annotated[str, Field(min_length=1, max_length=2048)]


class ShortlinkUpdate(BaseModel):
    url: Annotated[str | None, Field(default=None, min_length=1, max_length=2048)]
    short_code: Annotated[str | None, Field(default=None, min_length=1, max_length=128)]


class ShortlinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    short_code: str
    short_url: str
    url: str
    click_count: int
