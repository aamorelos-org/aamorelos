from typing import Any, Dict

from dependencies import get_area_service, get_region_service
from fastapi import APIRouter, Depends
from schemas.catalog import AreaListResponseSchema, RegionListResponseSchema
from services.area_service import AreaService
from services.region_service import RegionService

router = APIRouter(prefix="/api/v1/regiones", tags=["Regiones"])


@router.get("/", response_model=RegionListResponseSchema)
def get_regions(service: RegionService = Depends(get_region_service)) -> Dict[str, Any]:
    return service.get_all_regions()


@router.get("/{region_id}/areas", response_model=AreaListResponseSchema)
def get_areas_by_region(
    region_id: str,
    service: AreaService = Depends(get_area_service),
) -> Dict[str, Any]:
    return service.obtener_areas_por_region(region_id)

