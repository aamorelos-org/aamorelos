from typing import Any, Dict
from dependencies import get_current_access_token, get_evento_service
from fastapi import APIRouter, Depends, Query, status
from schemas.evento import (
    AdminEventoCreateResponseSchema,
    AdminEventoDetailResponseSchema,
    AdminEventoListResponseSchema,
    AdminEventoStatusResponseSchema,
    EventoCreateSchema,
    EventoEstadoUpdateSchema,
)
from services.evento_service import EventoService

router = APIRouter(
    prefix="/api/v1/admin/eventos",
    tags=["Admin Eventos"],
    dependencies=[Depends(get_current_access_token)],
)


@router.get("/", response_model=AdminEventoListResponseSchema)
def get_admin_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: EventoService = Depends(get_evento_service),
) -> Dict[str, Any]:
    return service.get_all_eventos_admin(skip=skip, limit=limit)


@router.post(
    "",
    response_model=AdminEventoCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token faltante, inválido o expirado"},
        status.HTTP_409_CONFLICT: {"description": "Ya existe un evento con ese slug"},
        422: {"description": "Datos inválidos"},
        status.HTTP_502_BAD_GATEWAY: {"description": "No se pudo subir la imagen a Cloudflare R2"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "No se pudo guardar el evento"},
    },
)
@router.post(
    "/",
    response_model=AdminEventoCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token faltante, inválido o expirado"},
        status.HTTP_409_CONFLICT: {"description": "Ya existe un evento con ese slug"},
        422: {"description": "Datos inválidos"},
        status.HTTP_502_BAD_GATEWAY: {"description": "No se pudo subir la imagen a Cloudflare R2"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "No se pudo guardar el evento"},
    },
)
def create_admin_event(
    payload: EventoCreateSchema,
    service: EventoService = Depends(get_evento_service),
) -> Dict[str, Any]:
    return service.create_evento_admin(payload)


@router.get(
    "/{evento_id}",
    response_model=AdminEventoDetailResponseSchema,
    responses={404: {"description": "Evento no encontrado"}},
)
def get_admin_event_by_id(
    evento_id: int,
    service: EventoService = Depends(get_evento_service),
) -> Dict[str, Any]:
    return service.get_evento_by_id_admin(evento_id)


@router.post(
    "/{evento_id}/estado",
    response_model=AdminEventoStatusResponseSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token faltante, inválido o expirado"},
        status.HTTP_404_NOT_FOUND: {"description": "Evento no encontrado"},
        422: {"description": "Datos inválidos"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "No se pudo actualizar el evento"},
    },
)
def update_admin_event_estado(
    evento_id: int,
    payload: EventoEstadoUpdateSchema,
    service: EventoService = Depends(get_evento_service),
) -> Dict[str, Any]:
    return service.actualizar_estado_evento(evento_id, payload.es_activo)
