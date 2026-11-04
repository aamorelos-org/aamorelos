from typing import List, Optional
from sqlalchemy.orm import Session

import models


class AreaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_region_id(self, region_id: str) -> List[models.Area]:
        return (
            self.db.query(models.Area)
            .filter(models.Area.region_id == region_id)
            .all()
        )

    def get_by_municipio_id(self, municipio_id: str) -> List[models.Area]:
        return (
            self.db.query(models.Area)
            .filter(models.Area.municipio_id == municipio_id)
            .all()
        )

    def get_by_id(self, area_id: str) -> Optional[models.Area]:
        return self.db.query(models.Area).filter(models.Area.id == area_id).first()
