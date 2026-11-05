from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import models


class ReflexionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Reflexion]:
        return self.db.query(models.Reflexion).order_by(models.Reflexion.id).all()

    def get_paginated(self, skip: int = 0, limit: int = 100) -> List[models.Reflexion]:
        if skip < 0:
            skip = 0
        if limit < 1:
            limit = 100
        if limit > 500:
            limit = 500
        return (
            self.db.query(models.Reflexion)
            .order_by(models.Reflexion.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self) -> int:
        return self.db.query(models.Reflexion).count()

    def get_by_id(self, reflexion_id: int) -> Optional[models.Reflexion]:
        return self.db.query(models.Reflexion).filter(models.Reflexion.id == reflexion_id).first()

    def get_by_slogan(self, slogan: str) -> Optional[models.Reflexion]:
        return self.db.query(models.Reflexion).filter(models.Reflexion.slogan == slogan).first()

    def create(
        self,
        *,
        slogan: str,
        titulo: str,
        subtitulo: str,
        imagen: str,
        alt: str,
        url: str,
        descripcion: str,
    ) -> models.Reflexion:
        reflexion = models.Reflexion(
            slogan=slogan,
            titulo=titulo,
            subtitulo=subtitulo,
            imagen=imagen,
            alt=alt,
            url=url,
            descripcion=descripcion,
        )
        self.db.add(reflexion)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(reflexion)
        return reflexion
