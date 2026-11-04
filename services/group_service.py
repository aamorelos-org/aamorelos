from typing import Any, Dict, Optional

from repositories.group_repository import GroupRepository
from schemas.group import GroupEnrichedResponseSchema


class GroupService:
    def __init__(self, repository: GroupRepository):
        self.repository = repository

    def get_filtered(
        self,
        municipio_id: str,
        tipo_id: Optional[int] = None,
        lengua_id: Optional[int] = None,
        genero_id: Optional[int] = None,
        permite_fumar: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        groups = self.repository.get_filtered(
            municipio_id=municipio_id,
            tipo_id=tipo_id,
            lengua_id=lengua_id,
            genero_id=genero_id,
            permite_fumar=permite_fumar,
            search=search,
            skip=skip,
            limit=limit,
        )
        total = self.repository.count_filtered(
            municipio_id=municipio_id,
            tipo_id=tipo_id,
            lengua_id=lengua_id,
            genero_id=genero_id,
            permite_fumar=permite_fumar,
            search=search,
        )
        data = [GroupEnrichedResponseSchema.from_model(g).model_dump() for g in groups]
        return {
            "ok": True,
            "total_registros": total,
            "skip": skip,
            "limit": limit,
            "data": data,
        }

    get_filtered_groups = get_filtered
