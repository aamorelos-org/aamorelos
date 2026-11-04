from typing import Any, Dict

from dependencies import get_group_type_service
from fastapi import APIRouter, Depends
from schemas.catalog import CatalogListResponseSchema
from services.group_type_service import GroupTypeService

router = APIRouter(prefix="/api/v1", tags=["Tipos de Grupo"])


@router.get("/grupos-tipos", response_model=CatalogListResponseSchema)
def get_group_types(service: GroupTypeService = Depends(get_group_type_service)) -> Dict[str, Any]:
    return service.get_all_group_types()
