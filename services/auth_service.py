from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.security import verify_password
from repositories.auth_repository import AuthRepository
from schemas.auth import LoginRequestSchema
from services.token_service import TokenService

# Hash bcrypt de relleno utilizado para igualar el tiempo de respuesta cuando
# el usuario no existe y evitar ataques de enumeración por temporización.
_DUMMY_PASSWORD_HASH = "$2b$12$UmZU1SJcOV/krCKQ223XG.AxvgODdI6aqhuZoHruo3N1XEiWmjyYG"


class InvalidCredentialsError(Exception):
    """El usuario no existe o la contraseña no coincide."""


class InactiveUserError(Exception):
    """El usuario existe pero su cuenta está deshabilitada."""


@dataclass(frozen=True)
class ClientInfo:
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuthService:
    def __init__(self, repository: AuthRepository, token_service: TokenService):
        self._repository = repository
        self._token_service = token_service

    def login(self, credentials: LoginRequestSchema, client: ClientInfo) -> Dict[str, Any]:
        identifier = credentials.username_or_email.strip()
        usuario = self._repository.get_by_username_or_email(identifier)

        if usuario is None:
            verify_password(credentials.password, _DUMMY_PASSWORD_HASH)
            raise InvalidCredentialsError()

        if not verify_password(credentials.password, usuario.password_hash):
            self._register_attempt(usuario.id, client, exitoso=False)
            raise InvalidCredentialsError()

        if not usuario.activo:
            self._register_attempt(usuario.id, client, exitoso=False)
            raise InactiveUserError()

        claims = {
            "username": usuario.username,
            "email": usuario.email,
            "nombre_completo": usuario.nombre_completo,
        }
        usuario_id = usuario.id

        self._register_attempt(usuario_id, client, exitoso=True)

        token = self._token_service.create_access_token(
            subject=str(usuario_id),
            claims=claims,
        )

        return {
            "ok": True,
            "mensaje": "Inicio de sesión exitoso",
            "data": {
                "access_token": token,
                "token_type": "bearer",
            },
        }

    def _register_attempt(self, usuario_id: int, client: ClientInfo, exitoso: bool) -> None:
        self._repository.registrar_login(
            usuario_id=usuario_id,
            ip_address=client.ip_address,
            user_agent=client.user_agent,
            exitoso=exitoso,
        )
