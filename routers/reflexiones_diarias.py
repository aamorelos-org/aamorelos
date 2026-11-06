from typing import Any, Dict

from dependencies import get_reflexion_diaria_service
from fastapi import APIRouter, Depends, Query
from schemas.reflexion_diaria import ReflexionDiariaListResponseSchema
from services.reflexion_diaria_service import ReflexionDiariaService

router = APIRouter(prefix="/api/v1/reflexiones-diarias", tags=["Reflexiones diarias"])


@router.get("/", response_model=ReflexionDiariaListResponseSchema)
def get_reflexiones_diarias(
    fecha: str = Query(..., min_length=5, max_length=5, pattern=r"^\d{2}-\d{2}$", description="Fecha en formato MM-DD"),
    service: ReflexionDiariaService = Depends(get_reflexion_diaria_service),
) -> Dict[str, Any]:
    return service.get_by_fecha(fecha)
