from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

import models


class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_distrito_id(self, distrito_id: str) -> List[models.Group]:
        return (
            self.db.query(models.Group)
            .options(
                selectinload(models.Group.grupo_tipo),
                selectinload(models.Group.lengua),
                selectinload(models.Group.genero),
                selectinload(models.Group.municipio),
                selectinload(models.Group.distrito),
            )
            .filter(models.Group.distrito_id == distrito_id)
            .all()
        )

    def get_by_municipio_ids(self, municipio_ids: List[str]) -> List[models.Group]:
        if not municipio_ids:
            return []
        return (
            self.db.query(models.Group)
            .options(
                selectinload(models.Group.grupo_tipo),
                selectinload(models.Group.lengua),
                selectinload(models.Group.genero),
                selectinload(models.Group.municipio),
                selectinload(models.Group.distrito),
            )
            .filter(models.Group.municipio_id.in_(municipio_ids))
            .all()
        )

    def get_filtered(
        self,
        municipio_id: str,
        tipo_id: Optional[int] = None,
        lengua_id: Optional[int] = None,
        genero_id: Optional[int] = None,
        permite_fumar: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[models.Group]:
        query = self.db.query(models.Group).options(
            selectinload(models.Group.grupo_tipo),
            selectinload(models.Group.lengua),
            selectinload(models.Group.genero),
            selectinload(models.Group.municipio),
            selectinload(models.Group.distrito),
        )

        query = query.filter(models.Group.municipio_id == municipio_id)

        if tipo_id is not None:
            query = query.filter(models.Group.tipo_id == tipo_id)
        if lengua_id is not None:
            query = query.filter(models.Group.lengua_id == lengua_id)
        if genero_id is not None:
            query = query.filter(models.Group.genero_id == genero_id)
        if permite_fumar is not None:
            query = query.filter(models.Group.permite_fumar == permite_fumar)

        if search is not None and search.strip() != "":
            search_term = search.strip()
            search_filter = or_(
                models.Group.direccion.ilike(f"%{search_term}%"),
                models.Group.vecinos.ilike(f"%{search_term}%"),
                models.Group.codigo_postal.ilike(f"%{search_term}%"),
                models.Group.referencias.ilike(f"%{search_term}%"),
                models.Group.localidad.ilike(f"%{search_term}%"),
                models.Group.nombre.ilike(f"%{search_term}%"),
            )
            query = query.filter(search_filter)

        if limit < 0:
            limit = 100
        if limit > 500:
            limit = 500
        if skip < 0:
            skip = 0

        return query.offset(skip).limit(limit).all()

    def count_filtered(
        self,
        municipio_id: str,
        tipo_id: Optional[int] = None,
        lengua_id: Optional[int] = None,
        genero_id: Optional[int] = None,
        permite_fumar: Optional[int] = None,
        search: Optional[str] = None,
    ) -> int:
        query = self.db.query(models.Group)

        query = query.filter(models.Group.municipio_id == municipio_id)

        if tipo_id is not None:
            query = query.filter(models.Group.tipo_id == tipo_id)
        if lengua_id is not None:
            query = query.filter(models.Group.lengua_id == lengua_id)
        if genero_id is not None:
            query = query.filter(models.Group.genero_id == genero_id)
        if permite_fumar is not None:
            query = query.filter(models.Group.permite_fumar == permite_fumar)

        if search is not None and search.strip() != "":
            search_term = search.strip()
            search_filter = or_(
                models.Group.direccion.ilike(f"%{search_term}%"),
                models.Group.vecinos.ilike(f"%{search_term}%"),
                models.Group.codigo_postal.ilike(f"%{search_term}%"),
                models.Group.referencias.ilike(f"%{search_term}%"),
                models.Group.localidad.ilike(f"%{search_term}%"),
                models.Group.nombre.ilike(f"%{search_term}%"),
            )
            query = query.filter(search_filter)

        return query.count()
