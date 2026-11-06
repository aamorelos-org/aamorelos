import logging
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.images import decode_base64_image
from repositories.reflexion_repository import ReflexionRepository
from schemas.reflexion import (
    AdminReflexionListItemSchema,
    AdminReflexionResponseSchema,
    ReflexionResponseSchema,
    ReflexionCreateSchema,
    ReflexionListItemSchema,
)
from services.r2_storage_service import R2StorageService

logger = logging.getLogger(__name__)

IMAGE_URL_PREFIX = "https://images.aamorelos.org/reflections/"
PAGE_URL_PREFIX = "pages/reflexiones/"


class ReflexionNotFoundError(Exception):
    """La reflexión no existe o no está disponible."""


class ReflexionAlreadyExistsError(Exception):
    """Ya existe una reflexión con el slug indicado."""


class ReflexionPersistenceError(Exception):
    """No se pudo guardar la reflexión en la base de datos."""


class ReflexionService:
    def __init__(self, repository: ReflexionRepository, storage: Optional[R2StorageService] = None):
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

    def get_all_reflexiones(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        reflexiones = self.repository.get_paginated(skip=skip, limit=limit)
        total = self.repository.count()
        data = [ReflexionListItemSchema.model_validate(r).model_dump() for r in reflexiones]
        return {
            "ok": True,
            "total_registros": total,
            "skip": skip,
            "limit": limit,
            "data": data,
        }

    def get_all_reflexiones_admin(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        reflexiones = self.repository.get_paginated_admin(skip=skip, limit=limit)
        total = self.repository.count_admin()
        data = [AdminReflexionListItemSchema.model_validate(r).model_dump() for r in reflexiones]
        return {
            "ok": True,
            "total_registros": total,
            "skip": skip,
            "limit": limit,
            "data": data,
        }

    def get_reflexion_by_identifier(self, identifier: str) -> Dict[str, Any]:
        cleaned = identifier.strip()
        if not cleaned:
            raise ReflexionNotFoundError()

        reflexion = self.repository.get_by_slogan(cleaned)
        if reflexion is None and cleaned.isdigit():
            reflexion = self.repository.get_by_id(int(cleaned))

        if reflexion is None:
            raise ReflexionNotFoundError()

        return {
            "ok": True,
            "data": ReflexionResponseSchema.model_validate(reflexion).model_dump(),
        }

    def get_reflexion_by_identifier_admin(self, identifier: str) -> Dict[str, Any]:
        cleaned = identifier.strip()
        if not cleaned:
            raise ReflexionNotFoundError()

        reflexion = self.repository.get_by_slogan(cleaned)
        if reflexion is None and cleaned.isdigit():
            reflexion = self.repository.get_by_id(int(cleaned))

        if reflexion is None:
            raise ReflexionNotFoundError()

        return {
            "ok": True,
            "data": AdminReflexionResponseSchema.model_validate(reflexion).model_dump(),
        }

    def _persist_reflexion(self, payload: ReflexionCreateSchema):
        slogan = payload.slogan

        if self.repository.get_by_slogan(slogan) is not None:
            raise ReflexionAlreadyExistsError(f"Ya existe una reflexión con el slug '{slogan}'")

        image_bytes = decode_base64_image(payload.imagen)
        imagen = f"{IMAGE_URL_PREFIX}{slogan}.webp"
        alt = payload.titulo
        url = f"{PAGE_URL_PREFIX}{slogan}.php"

        if len(url) > 1000:
            raise ValueError("La URL generada excede el máximo de 1000 caracteres")

        storage = self._get_storage()
        storage.upload_reflection_image(slogan, image_bytes)

        try:
            reflexion = self.repository.create(
                slogan=slogan,
                titulo=payload.titulo,
                subtitulo=payload.subtitulo,
                imagen=imagen,
                alt=alt,
                url=url,
                descripcion=payload.descripcion,
            )
        except IntegrityError as exc:
            storage.delete_reflection_image(slogan)
            raise ReflexionAlreadyExistsError(f"Ya existe una reflexión con el slug '{slogan}'") from exc
        except SQLAlchemyError as exc:
            storage.delete_reflection_image(slogan)
            logger.exception("No se pudo guardar la reflexión %s", slogan)
            raise ReflexionPersistenceError("No se pudo guardar la reflexión") from exc
        except Exception:
            storage.delete_reflection_image(slogan)
            logger.exception("Error inesperado al guardar la reflexión %s", slogan)
            raise

        return reflexion

    def create_reflexion(self, payload: ReflexionCreateSchema) -> Dict[str, Any]:
        reflexion = self._persist_reflexion(payload)

        data = ReflexionResponseSchema.model_validate(reflexion).model_dump()
        return {
            "ok": True,
            "mensaje": "Reflexión creada correctamente",
            "data": data,
        }

    def create_reflexion_admin(self, payload: ReflexionCreateSchema) -> Dict[str, Any]:
        reflexion = self._persist_reflexion(payload)

        data = AdminReflexionResponseSchema.model_validate(reflexion).model_dump()
        return {
            "ok": True,
            "mensaje": "Reflexión creada correctamente",
            "data": data,
        }

    def actualizar_estado_reflexion(self, identifier: str, es_activo: str) -> Dict[str, Any]:
        cleaned = identifier.strip()
        if not cleaned:
            raise ReflexionNotFoundError()

        reflexion = self.repository.get_by_slogan(cleaned)
        if reflexion is None and cleaned.isdigit():
            reflexion = self.repository.get_by_id(int(cleaned))

        if reflexion is None:
            raise ReflexionNotFoundError()

        mensaje = (
            "Reflexión activada correctamente" if es_activo == "S" else "Reflexión desactivada correctamente"
        )

        try:
            actualizada = self.repository.update_es_activo(reflexion.id, es_activo)
        except IntegrityError as exc:
            self.repository.db.rollback()
            raise ReflexionPersistenceError("No se pudo actualizar la reflexión") from exc
        except SQLAlchemyError as exc:
            self.repository.db.rollback()
            logger.exception("No se pudo actualizar el estado de la reflexión %s", cleaned)
            raise ReflexionPersistenceError("No se pudo actualizar la reflexión") from exc

        if actualizada is None:
            raise ReflexionNotFoundError()

        return {
            "ok": True,
            "mensaje": mensaje,
            "data": AdminReflexionResponseSchema.model_validate(actualizada).model_dump(),
        }
