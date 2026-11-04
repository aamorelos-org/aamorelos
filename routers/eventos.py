from typing import Any, Dict
from dependencies import get_current_access_token, get_evento_service
from fastapi import APIRouter, Depends, status
from schemas.evento import (
    EventoCreateResponseSchema,
    EventoCreateSchema,
    EventoDetailResponseSchema,
    EventoListResponseSchema,
)
from services.evento_service import EventoService

router = APIRouter(prefix="/api/v1/eventos", tags=["Eventos"])


@router.get("/", response_model=EventoListResponseSchema)
def get_events(service: EventoService = Depends(get_evento_service)) -> Dict[str, Any]:
    return service.get_all_eventos()


# Se registra con y sin barra final: el frontend envía "/eventos/" y
# FastAPI no redirige porque esa ruta ya coincide con el GET (devolvería 405).
@router.post(
    "",
    response_model=EventoCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_access_token)],
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
    response_model=EventoCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_access_token)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token faltante, inválido o expirado"},
        status.HTTP_409_CONFLICT: {"description": "Ya existe un evento con ese slug"},
        422: {"description": "Datos inválidos"},
        status.HTTP_502_BAD_GATEWAY: {"description": "No se pudo subir la imagen a Cloudflare R2"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "No se pudo guardar el evento"},
    },
)
def create_event(
    payload: EventoCreateSchema,
    service: EventoService = Depends(get_evento_service),
) -> Dict[str, Any]:
    return service.create_evento(payload)


@router.get(
    "/{evento_id}",
    response_model=EventoDetailResponseSchema,
    responses={404: {"description": "Evento no encontrado"}},
)
def get_event_by_id(
    evento_id: int,
    service: EventoService = Depends(get_evento_service),
) -> Dict[str, Any]:
    return service.get_evento_by_id(evento_id)
