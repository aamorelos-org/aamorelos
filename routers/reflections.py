from typing import Any, Dict
from dependencies import get_reflexion_service
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas.reflexion import (
    ReflexionDetailResponseSchema,
    ReflexionListResponseSchema,
)
from services.reflexion_service import (
    ReflexionNotFoundError,
    ReflexionService,
)

router = APIRouter(prefix="/api/v1/reflexiones", tags=["Reflexiones"])


@router.get("/", response_model=ReflexionListResponseSchema)
def get_reflections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: ReflexionService = Depends(get_reflexion_service),
) -> Dict[str, Any]:
    return service.get_all_reflexiones(skip=skip, limit=limit)


@router.get(
    "/{identifier}",
    response_model=ReflexionDetailResponseSchema,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Reflexión no encontrada"}},
)
def get_reflection(
    identifier: str,
    service: ReflexionService = Depends(get_reflexion_service),
) -> Dict[str, Any]:
    try:
        return service.get_reflexion_by_identifier(identifier)
    except ReflexionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reflexión no encontrada",
        ) from exc
