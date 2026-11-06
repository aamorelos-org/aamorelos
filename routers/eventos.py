from typing import Any, Dict
from dependencies import get_evento_service
from fastapi import APIRouter, Depends, Query
from schemas.evento import (
    EventoDetailResponseSchema,
    EventoListResponseSchema,
)
from services.evento_service import EventoService

router = APIRouter(prefix="/api/v1/eventos", tags=["Eventos"])


@router.get("/", response_model=EventoListResponseSchema)
def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: EventoService = Depends(get_evento_service),
) -> Dict[str, Any]:
    return service.get_all_eventos(skip=skip, limit=limit)


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
