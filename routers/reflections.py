from typing import Any, Dict
from dependencies import get_current_access_token, get_reflexion_service
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.reflexion import (
    ReflexionCreateResponseSchema,
    ReflexionCreateSchema,
    ReflexionListResponseSchema,
)
from services.reflexion_service import (
    ReflexionAlreadyExistsError,
    ReflexionPersistenceError,
    ReflexionService,
)
from services.r2_storage_service import R2StorageError

router = APIRouter(prefix="/api/v1/reflections", tags=["Reflexiones"])


@router.get("/", response_model=ReflexionListResponseSchema)
def get_reflections(service: ReflexionService = Depends(get_reflexion_service)) -> Dict[str, Any]:
    return service.get_all_reflexiones()


@router.post(
    "",
    response_model=ReflexionCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_access_token)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Token faltante, inválido o expirado"},
        status.HTTP_409_CONFLICT: {"description": "Ya existe una reflexión con ese slug"},
        422: {"description": "Datos inválidos"},
        status.HTTP_502_BAD_GATEWAY: {"description": "No se pudo subir la imagen a Cloudflare R2"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "No se pudo guardar la reflexión"},
    },
)
def create_reflection(
    payload: ReflexionCreateSchema,
    service: ReflexionService = Depends(get_reflexion_service),
) -> Dict[str, Any]:
    try:
        return service.create_reflexion(payload)
    except ReflexionAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una reflexión con ese slug",
        ) from exc
    except R2StorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo subir la imagen a Cloudflare R2",
        ) from exc
    except ReflexionPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo guardar la reflexión",
        ) from exc
