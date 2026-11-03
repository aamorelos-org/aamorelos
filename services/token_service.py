from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt


class InvalidAccessTokenError(Exception):
    """El token no es válido, expiró o no corresponde a un token de acceso."""


class TokenService:
    """Encapsula la creación de tokens JWT firmados."""

    def __init__(self, secret_key: str, algorithm: str, expire_minutes: int):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def create_access_token(
        self,
        subject: str,
        claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        now = datetime.now(timezone.utc)
        payload: Dict[str, Any] = {
            "sub": subject,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=self._expire_minutes),
            "type": "access",
        }
        if claims:
            payload.update(claims)

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Decodifica y valida un token de acceso emitido por el login."""
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={"require": ["sub", "exp", "nbf", "iat", "type"]},
            )
        except jwt.PyJWTError as exc:
            raise InvalidAccessTokenError("Token de autenticación inválido o expirado") from exc

        if payload.get("type") != "access":
            raise InvalidAccessTokenError("El token no es un token de acceso")

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise InvalidAccessTokenError("El token no contiene un sujeto válido")

        return payload
