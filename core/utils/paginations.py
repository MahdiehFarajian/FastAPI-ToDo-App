from fastapi import Request
from sqlalchemy.orm import Query
from typing import Type, TypeVar
from urllib.parse import urlencode
from math import ceil

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginationLinks(BaseModel):
    next: Optional[str]
    previous: Optional[str]
    current: int


class PaginatedResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    links: PaginationLinks
    total_items: int
    total_pages: int
    results: List[T]


def paginate(
    *,
    query: Query,
    schema: Type[T],
    request: Request,
    page: int,
    page_size: int
) -> PaginatedResponse[T]:
    total = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    results = [schema.from_orm(item) for item in items]

    base_url = str(request.url).split("?")[0]
    query_params = dict(request.query_params)
    query_params["page_size"] = str(page_size)

    next_url = previous_url = None

    if offset + page_size < total:
        query_params["page"] = str(page + 1)
        next_url = f"{base_url}?{urlencode(query_params)}"

    if page > 1:
        query_params["page"] = str(page - 1)
        previous_url = f"{base_url}?{urlencode(query_params)}"

    return PaginatedResponse[T](
        links=PaginationLinks(
            next=next_url,
            previous=previous_url,
            current=page
        ),
        total_items=total,
        total_pages=ceil(total / page_size),
        results=results
    )
