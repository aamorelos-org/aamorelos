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
