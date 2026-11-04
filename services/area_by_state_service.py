from typing import Any, Dict

from fastapi import HTTPException

from repositories.area_repository import AreaRepository
from repositories.municipality_repository import MunicipalityRepository
from repositories.state_repository import StateRepository
from schemas.catalog import AreaSchema


class AreaByStateService:
    def __init__(
        self,
        area_repository: AreaRepository,
        municipality_repository: MunicipalityRepository,
        state_repository: StateRepository,
    ):
        self.area_repository = area_repository
        self.municipality_repository = municipality_repository
        self.state_repository = state_repository

    def obtener_areas_por_estado(self, estado_id: str) -> Dict[str, Any]:
        state = self.state_repository.get_by_id(estado_id)
        if not state:
            raise HTTPException(status_code=404, detail="Estado no encontrado")

        municipalities = self.municipality_repository.get_by_estado_id(estado_id)
        result = []
        for municipality in municipalities:
            areas = self.area_repository.get_by_municipio_id(municipality.id)
            for area in areas:
                result.append(AreaSchema.model_validate(area).model_dump())
        return {
            "ok": True,
            "estado_id": estado_id,
            "total_registros": len(result),
            "data": result,
        }
