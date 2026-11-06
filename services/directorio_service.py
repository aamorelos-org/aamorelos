from typing import Any, Dict

from repositories.directorio_repository import DirectorioRepository
from schemas.directorio import DirectorioListItemSchema


class DirectorioService:
    def __init__(self, repository: DirectorioRepository):
        self.repository = repository

    def get_all_directorio(self) -> Dict[str, Any]:
        directorio = self.repository.get_all()
        data = [DirectorioListItemSchema.model_validate(item).model_dump() for item in directorio]
        return {
            "ok": True,
            "total_registros": len(data),
            "data": data,
        }
