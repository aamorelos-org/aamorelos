from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.security import verify_password
from repositories.auth_repository import AuthRepository
from schemas.auth import LoginRequestSchema
from services.login_rate_limiter import LoginRateLimiter, TooManyAttemptsError
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
    def __init__(
        self,
        repository: AuthRepository,
        token_service: TokenService,
        rate_limiter: LoginRateLimiter,
        max_failed_attempts: int = 5,
        lockout_window_minutes: int = 15,
    ):
        self._repository = repository
        self._token_service = token_service
        self._rate_limiter = rate_limiter
        self._max_failed_attempts = max_failed_attempts
        self._lockout_window_minutes = lockout_window_minutes

    def login(self, credentials: LoginRequestSchema, client: ClientInfo) -> Dict[str, Any]:
        ip_key = client.ip_address or "unknown"
        self._rate_limiter.check(ip_key)

        identifier = credentials.username_or_email.strip()
        usuario = self._repository.get_by_username_or_email(identifier)

        if usuario is None:
            verify_password(credentials.password, _DUMMY_PASSWORD_HASH)
            self._rate_limiter.record_failure(ip_key)
            raise InvalidCredentialsError()

        self._ensure_not_locked(usuario.id, client)

        if not verify_password(credentials.password, usuario.password_hash):
            self._register_attempt(usuario.id, client, exitoso=False)
            self._rate_limiter.record_failure(ip_key)
            raise InvalidCredentialsError()

        if not usuario.activo:
            self._register_attempt(usuario.id, client, exitoso=False)
            self._rate_limiter.record_failure(ip_key)
            raise InactiveUserError()

        claims = {
            "username": usuario.username,
            "email": usuario.email,
            "nombre_completo": usuario.nombre_completo,
        }
        usuario_id = usuario.id

        self._register_attempt(usuario_id, client, exitoso=True)
        self._rate_limiter.reset(ip_key)

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
                "nombre_completo": usuario.nombre_completo,
            },
        }

    def _ensure_not_locked(self, usuario_id: int, client: ClientInfo) -> None:
        recent_failures = self._repository.count_recent_failures(
            usuario_id,
            client.ip_address,
            self._lockout_window_minutes,
        )
        if recent_failures >= self._max_failed_attempts:
            raise TooManyAttemptsError(
                detail="Demasiados intentos fallidos. Intenta más tarde.",
                retry_after=self._lockout_window_minutes * 60,
            )

    def _register_attempt(self, usuario_id: int, client: ClientInfo, exitoso: bool) -> None:
        self._repository.registrar_login(
            usuario_id=usuario_id,
            ip_address=client.ip_address,
            user_agent=client.user_agent,
            exitoso=exitoso,
        )
