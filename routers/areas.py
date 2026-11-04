from typing import Any, Dict

from dependencies import get_district_service
from fastapi import APIRouter, Depends
from schemas.district import DistrictListResponseSchema
from services.district_service import DistrictService

router = APIRouter(prefix="/api/v1/areas", tags=["Áreas"])


@router.get("/{area_id}/distritos", response_model=DistrictListResponseSchema)
def get_districts_by_area(
    area_id: str,
    service: DistrictService = Depends(get_district_service),
) -> Dict[str, Any]:
    return service.obtener_distritos_por_area(area_id)
