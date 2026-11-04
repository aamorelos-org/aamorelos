from typing import Any, Dict

from dependencies import get_language_service
from fastapi import APIRouter, Depends
from schemas.catalog import CatalogListResponseSchema
from services.language_service import LanguageService

router = APIRouter(prefix="/api/v1", tags=["Idiomas"])


@router.get("/idiomas", response_model=CatalogListResponseSchema)
def get_languages(service: LanguageService = Depends(get_language_service)) -> Dict[str, Any]:
    return service.get_all_languages()
