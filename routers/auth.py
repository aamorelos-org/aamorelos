from typing import Any, Dict

from dependencies import get_auth_service
from fastapi import APIRouter, Depends, Request, status
from schemas.auth import LoginRequestSchema, LoginResponseSchema
from services.auth_service import AuthService, ClientInfo

router = APIRouter(prefix="/api/v1", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Credenciales inválidas"},
        status.HTTP_403_FORBIDDEN: {"description": "Usuario inactivo"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Demasiados intentos fallidos"},
    },
)
def login(
    credentials: LoginRequestSchema,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> Dict[str, Any]:
    client = ClientInfo(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return service.login(credentials, client)
