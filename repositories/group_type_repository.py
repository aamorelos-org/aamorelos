from typing import List
from sqlalchemy.orm import Session

import models


class GroupTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.GroupType]:
        return self.db.query(models.GroupType).order_by(models.GroupType.nombre).all()
