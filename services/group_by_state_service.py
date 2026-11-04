from typing import Any, Dict

from fastapi import HTTPException

from repositories.group_repository import GroupRepository
from repositories.municipality_repository import MunicipalityRepository
from repositories.state_repository import StateRepository
from schemas.group import GroupEnrichedResponseSchema


class GroupByStateService:
    def __init__(
        self,
        group_repository: GroupRepository,
        municipality_repository: MunicipalityRepository,
        state_repository: StateRepository,
    ):
        self.group_repository = group_repository
        self.municipality_repository = municipality_repository
        self.state_repository = state_repository

    def obtener_grupos_por_estado(self, estado_id: str) -> Dict[str, Any]:
        state = self.state_repository.get_by_id(estado_id)
        if not state:
            raise HTTPException(status_code=404, detail="Estado no encontrado")

        municipalities = self.municipality_repository.get_by_estado_id(estado_id)
        municipio_ids = [m.id for m in municipalities]

        groups = self.group_repository.get_by_municipio_ids(municipio_ids)
        data = [GroupEnrichedResponseSchema.from_model(g).model_dump() for g in groups]
        return {
            "ok": True,
            "estado_id": estado_id,
            "total_registros": len(data),
            "data": data,
        }
