from typing import List, Optional

from sqlalchemy.orm import Session

import models


class DistrictRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_area_id(self, area_id: str) -> List[models.District]:
        return (
            self.db.query(models.District)
            .filter(models.District.area_id == area_id)
            .all()
        )

    def get_by_area_ids(self, area_ids: List[str]) -> List[models.District]:
        if not area_ids:
            return []
        return (
            self.db.query(models.District)
            .filter(models.District.area_id.in_(area_ids))
            .all()
        )

    def get_by_municipio_ids(self, municipio_ids: List[str]) -> List[models.District]:
        if not municipio_ids:
            return []
        return (
            self.db.query(models.District)
            .filter(models.District.municipio_id.in_(municipio_ids))
            .all()
        )

    def get_by_id(self, distrito_id: str) -> Optional[models.District]:
        return self.db.query(models.District).filter(models.District.id == distrito_id).first()
