from typing import Any, Dict

from dependencies import get_directorio_service
from fastapi import APIRouter, Depends
from schemas.directorio import DirectorioListResponseSchema
from services.directorio_service import DirectorioService

router = APIRouter(prefix="/api/v1/directorio", tags=["Directorio"])


@router.get("/", response_model=DirectorioListResponseSchema)
def get_directorio(service: DirectorioService = Depends(get_directorio_service)) -> Dict[str, Any]:
    return service.get_all_directorio()
