from typing import List, Optional
from sqlalchemy.orm import Session

import models


class CountryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Country]:
        return self.db.query(models.Country).order_by(models.Country.nombre).all()

    def get_by_id(self, country_id: str) -> Optional[models.Country]:
        return self.db.query(models.Country).filter(models.Country.id == country_id).first()

