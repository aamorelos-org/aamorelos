"""Rate limiting en memoria para el endpoint de login.

Almacena contadores por clave (normalmente la IP) dentro del proceso.
Es correcto para un único proceso/instancia, pero en un despliegue con
varios workers o réplicas habría que mover el estado a Redis o a una
tabla compartida para que el límite sea coherente entre procesos.
"""

from collections import deque
from threading import Lock
from time import monotonic


class TooManyAttemptsError(Exception):
    """Se superó el límite de intentos fallidos."""

    def __init__(self, detail: str, retry_after: int):
        self.detail = detail
        self.retry_after = retry_after
        super().__init__(detail)


class LoginRateLimiter:
    def __init__(self, max_attempts: int, window_minutes: int):
        if max_attempts < 1:
            raise ValueError("max_attempts debe ser al menos 1")
        if window_minutes < 1:
            raise ValueError("window_minutes debe ser al menos 1")

        self._max_attempts = max_attempts
        self._window_seconds = window_minutes * 60
        self._attempts: dict[str, deque[float]] = {}
        self._lock = Lock()

    def check(self, key: str) -> None:
        with self._lock:
            attempts = self._prune(key)
            if len(attempts) >= self._max_attempts:
                oldest = attempts[0]
                retry_after = int(self._window_seconds - (monotonic() - oldest))
                raise TooManyAttemptsError(
                    detail="Demasiados intentos fallidos. Intenta más tarde.",
                    retry_after=max(retry_after, 1),
                )

    def record_failure(self, key: str) -> None:
        with self._lock:
            attempts = self._prune(key)
            attempts.append(monotonic())

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)

    def _prune(self, key: str) -> deque[float]:
        attempts = self._attempts.setdefault(key, deque())
        cutoff = monotonic() - self._window_seconds
        while attempts and attempts[0] < cutoff:
            attempts.popleft()
        return attempts
