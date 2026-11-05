from typing import Any, Dict

from dependencies import get_district_by_state_service, get_group_by_district_service
from fastapi import APIRouter, Depends
from schemas.district import DistrictDetailResponseSchema
from schemas.group import GroupByDistrictListResponseSchema
from services.district_by_state_service import DistrictByStateService
from services.group_by_district_service import GroupByDistrictService

router = APIRouter(prefix="/api/v1/distritos", tags=["Distritos"])


@router.get("/{distrito_id}", response_model=DistrictDetailResponseSchema)
def get_district(
    distrito_id: str,
    service: DistrictByStateService = Depends(get_district_by_state_service),
) -> Dict[str, Any]:
    return service.obtener_distrito_por_id(distrito_id)


@router.get("/{distrito_id}/grupos", response_model=GroupByDistrictListResponseSchema)
def get_groups_by_district(
    distrito_id: str,
    service: GroupByDistrictService = Depends(get_group_by_district_service),
) -> Dict[str, Any]:
    return service.obtener_grupos_por_distrito(distrito_id)
