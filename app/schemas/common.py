from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    error: dict[str, str]


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    total_pages: int

    @classmethod
    def build(cls, *, items: list[T], total: int, page: int, size: int):
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            total_pages=ceil(total / size) if total else 0,
        )


class IdName(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
