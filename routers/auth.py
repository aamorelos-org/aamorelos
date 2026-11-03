from typing import Any, Dict

from dependencies import get_auth_service
from fastapi import APIRouter, Depends, HTTPException, Request, status
from schemas.auth import LoginRequestSchema, LoginResponseSchema
from services.auth_service import (
    AuthService,
    ClientInfo,
    InactiveUserError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/api/v1", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Credenciales inválidas"},
        status.HTTP_403_FORBIDDEN: {"description": "Usuario inactivo"},
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

    try:
        return service.login(credentials, client)
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo",
        ) from exc
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
