from typing import Any, Dict

from dependencies import get_group_gender_service
from fastapi import APIRouter, Depends
from schemas.catalog import CatalogListResponseSchema
from services.group_gender_service import GroupGenderService

router = APIRouter(prefix="/api/v1", tags=["Géneros de Grupo"])


@router.get("/grupos-generos", response_model=CatalogListResponseSchema)
def get_group_genders(service: GroupGenderService = Depends(get_group_gender_service)) -> Dict[str, Any]:
    return service.get_all_group_genders()
