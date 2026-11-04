from typing import List
from sqlalchemy.orm import Session

import models


class GroupGenderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.GroupGender]:
        return self.db.query(models.GroupGender).order_by(models.GroupGender.nombre).all()
