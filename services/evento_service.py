import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload

from core.images import decode_base64_image
from repositories.evento_repository import EventoRepository
from schemas.evento import (
    AniversarioCreateSchema,
    AniversarioDiaSchema,
    AniversarioSchema,
    EventoCreateSchema,
    EventoDetailDataSchema,
    EventoListItemSchema,
    EventoResponseSchema,
)
from services.r2_storage_service import R2StorageService

logger = logging.getLogger(__name__)

IMAGE_URL_PREFIX = "https://images.aamorelos.org/events/"
PAGE_URL_PREFIX = "pages/eventos/"


class EventoAlreadyExistsError(Exception):
    """Ya existe un evento con el slug indicado."""


class EventoPersistenceError(Exception):
    """No se pudo guardar el evento en la base de datos."""


def _to_bool(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "t", "y", "yes"}


def _aniversario_payload(aniversario) -> Optional[Dict[str, Any]]:
    if aniversario is None:
        return None

    dias = [
        AniversarioDiaSchema(
            dia=dia.dia,
            tema=dia.tema,
            fecha=dia.fecha,
            grupos=dia.grupos,
            numero=dia.numero,
            es_junta_publica=_to_bool(dia.es_junta_publica),
        ).model_dump()
        for dia in aniversario.dias
    ]

    return AniversarioSchema(
        epigrafe=aniversario.epigrafe,
        kicker=aniversario.kicker,
        frase_reflexion=aniversario.frase_reflexion,
        sede=aniversario.sede,
        dias_unidad=aniversario.dias_unidad,
        junta_publica=aniversario.junta_publica,
        contacto_nombre=aniversario.contacto_nombre,
        contacto_telefono=aniversario.contacto_telefono,
        dias=dias,
    ).model_dump()


class EventoService:
    def __init__(self, repository: EventoRepository, storage: Optional[R2StorageService] = None):
        self.repository = repository
        self.storage = storage

    def _get_storage(self) -> R2StorageService:
        if self.storage is None:
            from config import settings

            self.storage = R2StorageService(
                account_id=settings.r2_account_id,
                access_key_id=settings.r2_access_key_id,
                secret_access_key=settings.r2_secret_access_key,
                bucket_name=settings.r2_bucket_name,
            )
        return self.storage

    def get_all_eventos(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        eventos = self.repository.get_paginated(skip=skip, limit=limit)
        total = self.repository.count()
        data = [EventoListItemSchema.model_validate(e).model_dump() for e in eventos]
        return {
            "ok": True,
            "total_registros": total,
            "skip": skip,
            "limit": limit,
            "data": data,
        }

    def get_evento_by_id(self, evento_id: int) -> Dict[str, Any]:
        evento = self.repository.get_by_id(evento_id)
        if not evento:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        data = EventoDetailDataSchema(
            **EventoResponseSchema.model_validate(evento).model_dump(),
            aniversario=_aniversario_payload(evento.aniversario),
        ).model_dump()
        return {
            "ok": True,
            "data": data,
        }

    def create_evento(self, payload: EventoCreateSchema) -> Dict[str, Any]:
        slogan = payload.slogan

        if self.repository.get_by_slogan(slogan) is not None:
            raise EventoAlreadyExistsError(f"Ya existe un evento con el slug '{slogan}'")

        image_bytes = decode_base64_image(payload.imagen)
        imagen = f"{IMAGE_URL_PREFIX}{slogan}.webp"
        url = f"{PAGE_URL_PREFIX}{slogan}.php"
        alt = payload.titulo

        if len(url) > 1000:
            raise ValueError("La URL generada excede el máximo de 1000 caracteres")

        es_aniversario = payload.tipo == "aniversario"
        aniversario_data: Optional[Dict[str, Any]] = None
        dias_data: Optional[list] = None
        frases: Optional[list] = None

        if es_aniversario:
            aniversario_data = {
                "epigrafe": payload.epigrafe,
                "kicker": payload.kicker,
                "frase_reflexion": payload.frase_reflexion,
                "sede": payload.sede,
                "dias_unidad": payload.dias_unidad,
                "junta_publica": payload.junta_publica,
                "contacto_nombre": payload.contacto_nombre,
                "contacto_telefono": payload.contacto_telefono,
            }
            dias_data = [dia.model_dump() for dia in payload.dias]
        else:
            frases = [payload.parrafo1, payload.parrafo2]

        storage = self._get_storage()
        storage.upload_event_image(slogan, image_bytes)

        try:
            evento = self.repository.create(
                tipo=payload.tipo,
                slogan=slogan,
                url=url,
                titulo=payload.titulo,
                subtitulo=payload.subtitulo,
                imagen=imagen,
                alt=alt,
                pie=payload.pie,
                frases=frases,
                aniversario=aniversario_data,
                dias=dias_data,
            )
        except IntegrityError as exc:
            storage.delete_event_image(slogan)
            raise EventoAlreadyExistsError(f"Ya existe un evento con el slug '{slogan}'") from exc
        except SQLAlchemyError as exc:
            storage.delete_event_image(slogan)
            logger.exception("No se pudo guardar el evento %s", slogan)
            raise EventoPersistenceError("No se pudo guardar el evento") from exc
        except Exception:
            storage.delete_event_image(slogan)
            logger.exception("Error inesperado al guardar el evento %s", slogan)
            raise

        evento = self.repository.get_by_id(evento.id)
        data = EventoDetailDataSchema(
            **EventoResponseSchema.model_validate(evento).model_dump(),
            aniversario=_aniversario_payload(evento.aniversario),
        ).model_dump()
        return {
            "ok": True,
            "mensaje": "Evento creado correctamente",
            "data": data,
        }
