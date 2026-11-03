from typing import Optional

import models
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


class UsuarioRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_username(self, username: str) -> Optional[models.Usuario]:
        return (
            self._db.query(models.Usuario)
            .filter(models.Usuario.username == username)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[models.Usuario]:
        return (
            self._db.query(models.Usuario)
            .filter(models.Usuario.email == email)
            .first()
        )

    def create(
        self,
        username: str,
        email: str,
        password_hash: str,
        nombre_completo: Optional[str],
        activo: bool,
    ) -> models.Usuario:
        usuario = models.Usuario(
            username=username,
            email=email,
            password_hash=password_hash,
            nombre_completo=nombre_completo,
            activo=activo,
        )
        self._db.add(usuario)
        try:
            self._db.commit()
        except IntegrityError:
            self._db.rollback()
            raise
        self._db.refresh(usuario)
        return usuario
