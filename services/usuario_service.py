import re
from dataclasses import dataclass
from typing import Optional

import models
from core.security import hash_password
from repositories.usuario_repository import UsuarioRepository
from sqlalchemy.exc import IntegrityError

_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_USERNAME_MIN_LENGTH = 3
_USERNAME_MAX_LENGTH = 50
_EMAIL_MAX_LENGTH = 150
_PASSWORD_MIN_LENGTH = 8
_PASSWORD_MAX_BYTES = 72  # Límite de bcrypt


class InvalidUserDataError(ValueError):
    """Los datos proporcionados no cumplen las reglas de validación."""


class UserAlreadyExistsError(Exception):
    """El username o el email ya están registrados."""


@dataclass(frozen=True)
class NewUser:
    username: str
    email: str
    password: str
    nombre_completo: Optional[str] = None
    activo: bool = True


class UsuarioService:
    def __init__(self, repository: UsuarioRepository):
        self._repository = repository

    def create_user(self, data: NewUser) -> models.Usuario:
        username = data.username.strip()
        email = data.email.strip().lower()
        nombre_completo = data.nombre_completo.strip() if data.nombre_completo else None

        self._validate(username, email, data.password)

        if self._repository.get_by_username(username):
            raise UserAlreadyExistsError(f"El username '{username}' ya está registrado")

        if self._repository.get_by_email(email):
            raise UserAlreadyExistsError(f"El email '{email}' ya está registrado")

        try:
            return self._repository.create(
                username=username,
                email=email,
                password_hash=hash_password(data.password),
                nombre_completo=nombre_completo,
                activo=data.activo,
            )
        except IntegrityError as exc:
            # Cubre la condición de carrera entre la validación y el INSERT.
            raise UserAlreadyExistsError(
                "El username o el email ya están registrados"
            ) from exc

    @staticmethod
    def _validate(username: str, email: str, password: str) -> None:
        if not _USERNAME_MIN_LENGTH <= len(username) <= _USERNAME_MAX_LENGTH:
            raise InvalidUserDataError(
                f"El username debe tener entre {_USERNAME_MIN_LENGTH} y "
                f"{_USERNAME_MAX_LENGTH} caracteres"
            )

        if not _USERNAME_PATTERN.match(username):
            raise InvalidUserDataError(
                "El username solo puede contener letras, números, puntos, "
                "guiones y guiones bajos"
            )

        if len(email) > _EMAIL_MAX_LENGTH or not _EMAIL_PATTERN.match(email):
            raise InvalidUserDataError("El email no tiene un formato válido")

        if len(password) < _PASSWORD_MIN_LENGTH:
            raise InvalidUserDataError(
                f"La contraseña debe tener al menos {_PASSWORD_MIN_LENGTH} caracteres"
            )

        if len(password.encode("utf-8")) > _PASSWORD_MAX_BYTES:
            raise InvalidUserDataError(
                f"La contraseña no puede exceder {_PASSWORD_MAX_BYTES} bytes"
            )
