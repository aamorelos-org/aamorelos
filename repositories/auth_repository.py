from datetime import datetime, timedelta, timezone
from typing import Optional

import models
from sqlalchemy import func, or_
from sqlalchemy.orm import Session


class AuthRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_username_or_email(self, identifier: str) -> Optional[models.Usuario]:
        return (
            self._db.query(models.Usuario)
            .filter(
                or_(
                    models.Usuario.username == identifier,
                    func.lower(models.Usuario.email) == identifier.lower(),
                )
            )
            .first()
        )

    def count_recent_failures(
        self,
        usuario_id: int,
        ip_address: Optional[str],
        window_minutes: int,
    ) -> int:
        since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        query = self._db.query(func.count(models.HistorialLogin.id)).filter(
            models.HistorialLogin.usuario_id == usuario_id,
            models.HistorialLogin.exitoso.is_(False),
            models.HistorialLogin.fecha_login >= since,
        )
        if ip_address:
            query = query.filter(models.HistorialLogin.ip_address == ip_address)
        return query.scalar() or 0

    def registrar_login(
        self,
        usuario_id: int,
        ip_address: Optional[str],
        user_agent: Optional[str],
        exitoso: bool,
    ) -> None:
        self._db.add(
            models.HistorialLogin(
                usuario_id=usuario_id,
                ip_address=ip_address,
                user_agent=user_agent,
                exitoso=exitoso,
            )
        )
        self._db.commit()
