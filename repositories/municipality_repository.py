from typing import List

import models
from sqlalchemy.orm import Session


class MunicipalityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_estado_id(self, estado_id: str) -> List[models.Municipality]:
        return (
            self.db.query(models.Municipality)
            .filter(models.Municipality.estado_id == estado_id)
            .all()
        )
