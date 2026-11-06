from typing import Any, Dict

from repositories.reflexion_diaria_repository import ReflexionDiariaRepository
from schemas.reflexion_diaria import ReflexionDiariaListItemSchema


class ReflexionDiariaService:
    def __init__(self, repository: ReflexionDiariaRepository):
        self.repository = repository

    def get_by_fecha(self, fecha: str) -> Dict[str, Any]:
        registros = self.repository.get_by_fecha(fecha)
        data = [ReflexionDiariaListItemSchema.model_validate(item).model_dump() for item in registros]
        return {
            "ok": True,
            "total_registros": len(data),
            "fecha": fecha,
            "data": data,
        }
