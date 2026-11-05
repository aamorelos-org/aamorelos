from typing import Any, Dict, List, Optional

import models
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload


class EventoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Evento]:
        return self.db.query(models.Evento).order_by(models.Evento.id).all()

    def get_paginated(self, skip: int = 0, limit: int = 100) -> List[models.Evento]:
        if skip < 0:
            skip = 0
        if limit < 1:
            limit = 100
        if limit > 500:
            limit = 500
        return (
            self.db.query(models.Evento)
            .order_by(models.Evento.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self) -> int:
        return self.db.query(models.Evento).count()

    def get_by_id(self, evento_id: int) -> Optional[models.Evento]:
        return (
            self.db.query(models.Evento)
            .options(
                selectinload(models.Evento.aniversario).selectinload(models.Aniversario.dias)
            )
            .filter(models.Evento.id == evento_id)
            .first()
        )

    def get_by_slogan(self, slogan: str) -> Optional[models.Evento]:
        return (
            self.db.query(models.Evento)
            .options(
                selectinload(models.Evento.aniversario).selectinload(models.Aniversario.dias)
            )
            .filter(models.Evento.slogan == slogan)
            .first()
        )

    def create(
        self,
        *,
        tipo: str,
        slogan: str,
        url: str,
        titulo: str,
        subtitulo: Optional[str],
        imagen: str,
        alt: str,
        pie: Optional[str],
        frases: Optional[List[str]],
        aniversario: Optional[Dict[str, Any]] = None,
        dias: Optional[List[Dict[str, Any]]] = None,
    ) -> models.Evento:
        evento = models.Evento(
            tipo=tipo,
            slogan=slogan,
            url=url,
            titulo=titulo,
            subtitulo=subtitulo,
            imagen=imagen,
            alt=alt,
            pie=pie,
            frases=frases,
        )

        if aniversario is not None:
            evento.aniversario = models.Aniversario(
                epigrafe=aniversario["epigrafe"],
                kicker=aniversario["kicker"],
                frase_reflexion=aniversario["frase_reflexion"],
                sede=aniversario["sede"],
                dias_unidad=aniversario["dias_unidad"],
                junta_publica=aniversario["junta_publica"],
                contacto_nombre=aniversario["contacto_nombre"],
                contacto_telefono=aniversario["contacto_telefono"],
                dias=[
                    models.AniversarioDia(
                        dia=dia["dia"],
                        tema=dia["tema"],
                        fecha=dia["fecha"],
                        grupos=dia["grupos"],
                        numero=dia["numero"],
                        # La columna es bit(1): Postgres no acepta bool ni int.
                        es_junta_publica="1" if dia["es_junta_publica"] else "0",
                    )
                    for dia in (dias or [])
                ],
            )

        self.db.add(evento)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(evento)
        return evento
