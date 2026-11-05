from typing import Any, Dict

from fastapi import HTTPException

from repositories.district_repository import DistrictRepository
from repositories.municipality_repository import MunicipalityRepository
from repositories.state_repository import StateRepository
from schemas.district import DistrictByStateResponseSchema, DistrictDetailResponseSchema, DistrictListItemSchema


class DistrictByStateService:
    def __init__(
        self,
        district_repository: DistrictRepository,
        municipality_repository: MunicipalityRepository,
        state_repository: StateRepository,
    ):
        self.district_repository = district_repository
        self.municipality_repository = municipality_repository
        self.state_repository = state_repository

    def obtener_distritos_por_estado(self, estado_id: str) -> Dict[str, Any]:
        state = self.state_repository.get_by_id(estado_id)
        if not state:
            raise HTTPException(status_code=404, detail="Estado no encontrado")

        municipalities = self.municipality_repository.get_by_estado_id(estado_id)
        municipio_ids = [m.id for m in municipalities]

        districts = self.district_repository.get_by_municipio_ids(municipio_ids)
        data = [DistrictListItemSchema.from_model(d).model_dump() for d in districts]
        return {
            "ok": True,
            "estado_id": estado_id,
            "total_registros": len(data),
            "data": data,
        }

    def obtener_distrito_por_id(self, distrito_id: str) -> Dict[str, Any]:
        from sqlalchemy.orm import selectinload

        import models

        district = (
            self.district_repository.db.query(models.District)
            .options(selectinload(models.District.municipio), selectinload(models.District.area))
            .filter(models.District.id == distrito_id)
            .one_or_none()
        )
        if not district:
            raise HTTPException(status_code=404, detail="Distrito no encontrado")
        return DistrictDetailResponseSchema.from_model(district).model_dump()
