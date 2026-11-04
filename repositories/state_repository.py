from typing import List, Optional

from sqlalchemy.orm import Session

import models


class StateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_pais_id(self, pais_id: str) -> List[models.State]:
        return (
            self.db.query(models.State)
            .filter(models.State.pais_id == pais_id)
            .order_by(models.State.nombre)
            .all()
        )

    def get_pais_by_id(self, pais_id: str) -> Optional[models.Country]:
        return self.db.query(models.Country).filter(models.Country.id == pais_id).first()

    def get_by_id(self, estado_id: str) -> Optional[models.State]:
        return self.db.query(models.State).filter(models.State.id == estado_id).first()
