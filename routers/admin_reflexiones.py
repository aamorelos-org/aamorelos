from typing import Any, Dict
from dependencies import get_current_access_token, get_reflexion_service
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas.reflexion import (
    AdminReflexionCreateResponseSchema,
    AdminReflexionDetailResponseSchema,
    AdminReflexionListResponseSchema,
    AdminReflexionStatusResponseSchema,
    ReflexionCreateSchema,
    ReflexionEstadoUpdateSchema,
)
from services.reflexion_service import (
    ReflexionNotFoundError,
    ReflexionService,
)

router = APIRouter(
    prefix="/api/v1/admin/reflexiones",
    tags=["Admin Reflexiones"],
    dependencies=[Depends(get_current_access_token)],
)


@router.get("/", response_model=AdminReflexionListResponseSchema)
def get_admin_reflections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: ReflexionService = Depends(get_reflexion_service),
) -> Dict[str, Any]:
    return service.get_all_reflexiones_admin(skip=skip, limit=limit)


@router.get(
    "/{identifier}",
    response_model=AdminReflexionDetailResponseSchema,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Reflexión no encontrada"}},
)
def get_admin_reflection(
    identifier: str,
    service: ReflexionService = Depends(get_reflexion_service),
) -> Dict[str, Any]:
    try:
        return service.get_reflexion_by_identifier_admin(identifier)
    except ReflexionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reflexión no encontrada",
        ) from exc


@router.post(
    "",
    response_model=AdminReflexionCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token faltante, inválido o expirado"},
        status.HTTP_409_CONFLICT: {"description": "Ya existe una reflexión con ese slug"},
        422: {"description": "Datos inválidos"},
        status.HTTP_502_BAD_GATEWAY: {"description": "No se pudo subir la imagen a Cloudflare R2"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "No se pudo guardar la reflexión"},
    },
)
@router.post(
    "/",
    response_model=AdminReflexionCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token faltante, inválido o expirado"},
        status.HTTP_409_CONFLICT: {"description": "Ya existe una reflexión con ese slug"},
        422: {"description": "Datos inválidos"},
        status.HTTP_502_BAD_GATEWAY: {"description": "No se pudo subir la imagen a Cloudflare R2"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "No se pudo guardar la reflexión"},
    },
)
def create_admin_reflection(
    payload: ReflexionCreateSchema,
    service: ReflexionService = Depends(get_reflexion_service),
) -> Dict[str, Any]:
    return service.create_reflexion_admin(payload)


@router.post(
    "/{identifier}/estado",
    response_model=AdminReflexionStatusResponseSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token faltante, inválido o expirado"},
        status.HTTP_404_NOT_FOUND: {"description": "Reflexión no encontrada"},
        422: {"description": "Datos inválidos"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "No se pudo actualizar la reflexión"},
    },
)
def update_admin_reflection_estado(
    identifier: str,
    payload: ReflexionEstadoUpdateSchema,
    service: ReflexionService = Depends(get_reflexion_service),
) -> Dict[str, Any]:
    try:
        return service.actualizar_estado_reflexion(identifier, payload.es_activo)
    except ReflexionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reflexión no encontrada",
        ) from exc
