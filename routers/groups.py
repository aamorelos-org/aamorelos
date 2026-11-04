from typing import Any, Dict, Optional

from dependencies import get_group_service
from fastapi import APIRouter, Depends, Query
from schemas.group import GroupListResponseSchema
from services.group_service import GroupService

router = APIRouter(prefix="/api/v1/grupos", tags=["Grupos"])


@router.get("/", response_model=GroupListResponseSchema)
def get_groups(
    municipio_id: str = Query(..., min_length=1),
    tipo_id: Optional[int] = Query(None),
    lengua_id: Optional[int] = Query(None),
    genero_id: Optional[int] = Query(None),
    permite_fumar: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: GroupService = Depends(get_group_service),
) -> Dict[str, Any]:
    return service.get_filtered(
        municipio_id=municipio_id,
        tipo_id=tipo_id,
        lengua_id=lengua_id,
        genero_id=genero_id,
        permite_fumar=permite_fumar,
        search=search,
        skip=skip,
        limit=limit,
    )
