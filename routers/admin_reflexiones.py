import logging
from typing import Annotated, Any, Dict, Optional

from dependencies import (
    get_current_access_token,
    get_notification_service,
    get_reflexion_service,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas.reflexion import (
    AdminReflexionCreateResponseSchema,
    AdminReflexionDetailResponseSchema,
    AdminReflexionListResponseSchema,
    AdminReflexionStatusResponseSchema,
    ReflexionCreateSchema,
    ReflexionEstadoUpdateSchema,
)
from services.firebase_notification_service import (
    REFLEXIONES_TOPIC,
    FirebaseNotificationService,
)
from services.reflexion_service import (
    ReflexionNotFoundError,
    ReflexionService,
)

logger = logging.getLogger(__name__)

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


def _notify_reflexiones_topic(
    notification_service: Optional[FirebaseNotificationService],
    payload: ReflexionCreateSchema,
    result: Dict[str, Any],
) -> None:
    """Notifica al topic ``reflexiones`` sin bloquear el alta si FCM no está disponible.

    Best-effort: si no hay servicio (fuera de prod) se omite; si el envío
    falla solo se registra y el POST sigue devolviendo 201.
    """
    if notification_service is None:
        return

    data = result.get("data") or {}
    # Se priorizan los valores persistidos y se cae al payload.
    titulo = (data.get("titulo") or payload.titulo or "").strip()
    subtitulo = (data.get("subtitulo") or "").strip()
    reflexion_id = data.get("id")
    slogan = data.get("slogan") or payload.slogan
    imagen = (data.get("imagen") or "").strip() or f"https://images.aamorelos.org/reflections/{slogan}.webp"

    title = f"Nueva reflexión: {titulo}" if titulo else "Nueva reflexión"
    body = subtitulo or "Nueva reflexión disponible"

    notification_data: Dict[str, str] = {
        "tipo": "reflexion",
        "slogan": str(slogan),
        "reflexion_id": str(reflexion_id) if reflexion_id is not None else "",
    }

    try:
        message_id = notification_service.send_topic(
            REFLEXIONES_TOPIC,
            title,
            body,
            data=notification_data,
            image=imagen,
        )
        logger.info(
            "Notificación enviada al topic %s (reflexion %s, mensaje %s)",
            REFLEXIONES_TOPIC,
            reflexion_id,
            message_id,
        )
    except Exception:
        logger.exception(
            "No se pudo enviar la notificación al topic %s (reflexion %s)",
            REFLEXIONES_TOPIC,
            reflexion_id,
        )


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
    notification_service: Annotated[
        Optional[FirebaseNotificationService], Depends(get_notification_service)
    ] = None,
) -> Dict[str, Any]:
    result = service.create_reflexion_admin(payload)
    _notify_reflexiones_topic(notification_service, payload, result)
    return result


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
