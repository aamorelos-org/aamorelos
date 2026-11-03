from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config import settings
from database.database import engine
from routers import (
    areas,
    auth,
    countries,
    districts,
    events,
    group_genders,
    group_types,
    groups,
    languages,
    reflections,
    regions,
    states,
)

app = FastAPI(
    title="API Geoadministrativa y de Grupos",
    description="API oficial para consultar la red de grupos",
    version="1.0.0",
)

allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
api_router.include_router(events.router)
api_router.include_router(reflections.router)

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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=reload)