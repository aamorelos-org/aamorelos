from typing import List

from sqlalchemy.orm import Session

import models


class DirectorioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Directorio]:
        return self.db.query(models.Directorio).order_by(models.Directorio.pagina, models.Directorio.id).all()
