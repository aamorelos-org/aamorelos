import logging
from typing import Annotated, Any, Dict, Optional

from dependencies import get_current_access_token, get_evento_service, get_notification_service
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
from services.firebase_notification_service import (
    EVENTOS_TOPIC,
    FirebaseNotificationService,
)

logger = logging.getLogger(__name__)

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


def _notify_eventos_topic(
    notification_service: Optional[FirebaseNotificationService],
    payload: EventoCreateSchema,
    result: Dict[str, Any],
) -> None:
    """Notifica al topic ``eventos`` sin bloquear el alta si FCM no está disponible.

    Best-effort: si no hay servicio (fuera de prod) se omite; si el envío
    falla solo se registra y el POST sigue devolviendo 201.
    """
    if notification_service is None:
        return

    data = result.get("data") or {}
    # Se priorizan los valores persistidos y se cae al payload.
    titulo = (data.get("titulo") or payload.titulo or "").strip()
    subtitulo = (data.get("subtitulo") or "").strip()
    evento_id = data.get("id")
    slogan = data.get("slogan") or payload.slogan
    tipo = data.get("tipo") or payload.tipo
    imagen = (data.get("imagen") or "").strip() or f"https://images.aamorelos.org/events/{slogan}.webp"

    title = f"Nuevo evento: {titulo}" if titulo else "Nuevo evento"
    body = subtitulo or "Nuevo evento disponible"

    # Tipo (informativo/invitacion), slogan y evento_id en el payload FCM.
    data_tipo = "invitacion" if tipo == "aniversario" else str(tipo)
    notification_data: Dict[str, str] = {
        "tipo": data_tipo,
        "slogan": str(slogan),
        "evento_id": str(evento_id) if evento_id is not None else "",
    }

    try:
        message_id = notification_service.send_topic(
            EVENTOS_TOPIC,
            title,
            body,
            data=notification_data,
            image=imagen,
        )
        logger.info(
            "Notificación enviada al topic %s (evento %s, mensaje %s)",
            EVENTOS_TOPIC,
            evento_id,
            message_id,
        )
    except Exception:
        logger.exception(
            "No se pudo enviar la notificación al topic %s (evento %s)",
            EVENTOS_TOPIC,
            evento_id,
        )


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
    notification_service: Annotated[
        Optional[FirebaseNotificationService], Depends(get_notification_service)
    ] = None,
) -> Dict[str, Any]:
    result = service.create_evento_admin(payload)
    _notify_eventos_topic(notification_service, payload, result)
    return result


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
