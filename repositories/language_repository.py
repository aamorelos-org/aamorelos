from typing import List
from sqlalchemy.orm import Session

import models


class LanguageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Language]:
        return self.db.query(models.Language).order_by(models.Language.nombre).all()
