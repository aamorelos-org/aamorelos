from typing import List

from sqlalchemy.orm import Session

import models


class ReflexionDiariaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_fecha(self, fecha: str) -> List[models.ReflexionDiaria]:
        return (
            self.db.query(models.ReflexionDiaria)
            .filter(models.ReflexionDiaria.fecha == fecha)
            .order_by(models.ReflexionDiaria.id)
            .all()
        )
