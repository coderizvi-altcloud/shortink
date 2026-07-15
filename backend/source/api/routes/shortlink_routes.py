"""API routes for shortlink CRUD."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from backend.source.config import get_redis_client
from backend.source.config.settings.redis_setting import PUBLIC_BASE_URL
from backend.source.models.schemas.shortlink_schema import (
    ShortlinkCreate,
    ShortlinkResponse,
    ShortlinkUpdate,
)
from backend.source.repository.crud.shortlink_crud import ShortlinkRecord, ShortlinkRepository

router = APIRouter(prefix="/shortlinks", tags=["shortlinks"])
redirect_router = APIRouter(tags=["redirect"])
repository = ShortlinkRepository()


def _short_url(request: Request, short_code: str) -> str:
    base_url = PUBLIC_BASE_URL or str(request.base_url).rstrip("/")
    return f"{base_url}/{short_code}"


def _serialize_shortlink(request: Request, shortlink: ShortlinkRecord) -> ShortlinkResponse:
    return ShortlinkResponse(
        id=shortlink.id,
        short_code=shortlink.short_code,
        short_url=_short_url(request, shortlink.short_code),
        url=shortlink.url,
        click_count=shortlink.click_count,
    )


@router.post("", response_model=ShortlinkResponse, status_code=status.HTTP_201_CREATED)
def create_shortlink(
    payload: ShortlinkCreate,
    request: Request,
    redis_client=Depends(get_redis_client),
) -> ShortlinkResponse:
    created = repository.create(redis_client, url=payload.url, user_id=0)
    return _serialize_shortlink(request, created)


@router.get("", response_model=list[ShortlinkResponse])
def list_shortlinks(
    request: Request,
    redis_client=Depends(get_redis_client),
) -> list[ShortlinkResponse]:
    return [_serialize_shortlink(request, s) for s in repository.list_all(redis_client)]


@router.get("/{shortlink_id}", response_model=ShortlinkResponse)
def get_shortlink(
    shortlink_id: int,
    request: Request,
    redis_client=Depends(get_redis_client),
) -> ShortlinkResponse:
    shortlink = repository.get_by_id(redis_client, shortlink_id)
    if shortlink is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlink not found")
    return _serialize_shortlink(request, shortlink)


@router.put("/{shortlink_id}", response_model=ShortlinkResponse)
def update_shortlink(
    shortlink_id: int,
    payload: ShortlinkUpdate,
    request: Request,
    redis_client=Depends(get_redis_client),
) -> ShortlinkResponse:
    shortlink = repository.get_by_id(redis_client, shortlink_id)
    if shortlink is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlink not found")

    if payload.url is None and payload.short_code is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nothing to update")

    try:
        updated = repository.update(redis_client, shortlink, url=payload.url, short_code=payload.short_code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _serialize_shortlink(request, updated)


@router.delete("/{shortlink_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shortlink(
    shortlink_id: int,
    redis_client=Depends(get_redis_client),
) -> Response:
    shortlink = repository.get_by_id(redis_client, shortlink_id)
    if shortlink is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlink not found")
    repository.delete(redis_client, shortlink)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _redirect(short_code: str, redis_client) -> RedirectResponse:
    shortlink = repository.get_by_short_code(redis_client, short_code)
    if shortlink is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlink not found")
    repository.increment_click_count(redis_client, shortlink)
    return RedirectResponse(url=shortlink.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@redirect_router.get("/{short_code}", include_in_schema=False)
def redirect_shortlink(short_code: str, redis_client=Depends(get_redis_client)):
    return _redirect(short_code, redis_client)


@redirect_router.get("/s/{short_code}", include_in_schema=False)
def redirect_shortlink_tiny(short_code: str, redis_client=Depends(get_redis_client)):
    return _redirect(short_code, redis_client)


@redirect_router.get("/r/{short_code}", include_in_schema=False)
def redirect_shortlink_legacy(short_code: str, redis_client=Depends(get_redis_client)):
    return _redirect(short_code, redis_client)
