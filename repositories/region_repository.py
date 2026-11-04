from typing import List, Optional
from sqlalchemy.orm import Session

import models


class RegionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Region]:
        return self.db.query(models.Region).order_by(models.Region.nombre).all()

    def get_by_id(self, region_id: str) -> Optional[models.Region]:
        return self.db.query(models.Region).filter(models.Region.id == region_id).first()

