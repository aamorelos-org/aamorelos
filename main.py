from fastapi import APIRouter, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config import settings
from database.database import engine
from core.images import ImageTooLargeError
from routers import (
    areas,
    auth,
    countries,
    directorio,
    districts,
    eventos,
    group_genders,
    group_types,
    groups,
    languages,
    reflections,
    regions,
    states,
)
from services.auth_service import InactiveUserError, InvalidCredentialsError
from services.evento_service import EventoAlreadyExistsError, EventoPersistenceError
from services.login_rate_limiter import TooManyAttemptsError
from services.reflexion_service import ReflexionAlreadyExistsError, ReflexionPersistenceError
from services.r2_storage_service import R2StorageError
from services.token_service import InvalidAccessTokenError

app = FastAPI(
    title="API Geoadministrativa y de Grupos",
    description="API oficial para consultar la red de grupos",
    version="1.0.0",
)

# ── Configuración CORS segura ──
# En producción ALLOWED_ORIGINS debe listar explícitamente los dominios permitidos.
# Nunca combinar "*" con allow_credentials=True (inválido per la espec CORS).
_allowed_origins_raw = settings.allowed_origins
allowed_origins = [origin.strip() for origin in _allowed_origins_raw.split(",") if origin.strip()]

if "*" in allowed_origins:
    if settings.app_env != "dev":
        raise ValueError(
            "ALLOWED_ORIGINS no puede ser '*' con allow_credentials=True en entorno no-dev. "
            "Define explícitamente los dominios permitidos en ALLOWED_ORIGINS."
        )
    # En dev se permite wildcard solo si se desactivan las credenciales.
    allow_credentials = False
else:
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "User-Agent",
        "X-Requested-With",
    ],
    expose_headers=["Content-Range", "X-Total-Count"],
    max_age=86400,  # 24 horas de preflight cacheado
)


# ── Manejadores globales de excepción (evita try/except repetitivo en routers) ──
@app.exception_handler(ImageTooLargeError)
async def image_too_large_handler(request: Request, exc: ImageTooLargeError):
    return JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content={"detail": str(exc)},
    )


@app.exception_handler(R2StorageError)
async def r2_storage_handler(request: Request, exc: R2StorageError):
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": "No se pudo subir la imagen a Cloudflare R2"},
    )


@app.exception_handler(SQLAlchemyError)
async def db_error_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error de base de datos"},
    )


@app.exception_handler(InvalidAccessTokenError)
async def invalid_token_handler(request: Request, exc: InvalidAccessTokenError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Token de autenticación inválido o expirado"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(TooManyAttemptsError)
async def too_many_attempts_handler(request: Request, exc: TooManyAttemptsError):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": exc.detail},
        headers={"Retry-After": str(exc.retry_after)},
    )


@app.exception_handler(EventoAlreadyExistsError)
@app.exception_handler(ReflexionAlreadyExistsError)
async def already_exists_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


@app.exception_handler(EventoPersistenceError)
@app.exception_handler(ReflexionPersistenceError)
async def persistence_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Credenciales inválidas"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(InactiveUserError)
async def inactive_user_handler(request: Request, exc: InactiveUserError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "El usuario está inactivo"},
    )

api_router = APIRouter(prefix="/aa")

api_router.include_router(auth.router)
api_router.include_router(countries.router)
api_router.include_router(regions.router)
api_router.include_router(areas.router)
api_router.include_router(states.router)
api_router.include_router(districts.router)
api_router.include_router(group_genders.router)
api_router.include_router(languages.router)
api_router.include_router(group_types.router)
api_router.include_router(groups.router)
api_router.include_router(eventos.router)
api_router.include_router(reflections.router)
api_router.include_router(directorio.router)

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ready")
def readiness_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        return {"status": "not_ready", "error": str(exc)}


if __name__ == "__main__":
    import uvicorn

    reload = settings.app_env == "dev"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=reload)