from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import models


class ReflexionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Reflexion]:
        return self.db.query(models.Reflexion).order_by(models.Reflexion.id).all()

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
