from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import models


class ReflexionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Reflexion]:
        return self.db.query(models.Reflexion).all()

    def get_by_id(self, reflexion_id: int) -> Optional[models.Reflexion]:
        return self.db.query(models.Reflexion).filter(models.Reflexion.id == reflexion_id).first()

    def get_by_slug(self, slug: str) -> Optional[models.Reflexion]:
        return self.db.query(models.Reflexion).filter(models.Reflexion.slug == slug).first()

    def create(
        self,
        *,
        slug: str,
        title: str,
        subtitle: str,
        image: str,
        alt: str,
        url: str,
        description: str,
    ) -> models.Reflexion:
        reflexion = models.Reflexion(
            slug=slug,
            title=title,
            subtitle=subtitle,
            image=image,
            alt=alt,
            url=url,
            description=description,
        )
        self.db.add(reflexion)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(reflexion)
        return reflexion
