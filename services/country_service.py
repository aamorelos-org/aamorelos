from typing import Any, Dict

from repositories.country_repository import CountryRepository
from schemas.catalog import CountrySchema


class CountryService:
    def __init__(self, repository: CountryRepository):
        self.repository = repository

    def get_all_countries(self) -> Dict[str, Any]:
        countries = self.repository.get_all()
        data = [CountrySchema.model_validate(p).model_dump() for p in countries]
        return {
            "ok": True,
            "total_registros": len(data),
            "data": data,
        }
