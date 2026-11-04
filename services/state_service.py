from typing import Any, Dict

from fastapi import HTTPException

from repositories.state_repository import StateRepository
from schemas.catalog import StateSchema


class StateService:
    def __init__(self, repository: StateRepository):
        self.repository = repository

    def get_states_by_country_id(self, pais_id: str) -> Dict[str, Any]:
        parent = self.repository.get_pais_by_id(pais_id)
        if not parent:
            raise HTTPException(status_code=404, detail="País no encontrado")
        states = self.repository.get_by_pais_id(pais_id)
        data = [StateSchema.model_validate(s).model_dump() for s in states]
        return {
            "ok": True,
            "total_registros": len(data),
            "pais_id": pais_id,
            "data": data,
        }
