from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analyses, auth, settings as settings_route
from app.core.config import get_settings
from app.core.database import Base, engine

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-assisted historical inscription analysis, reconstruction and "
        "contextual understanding. All AI outputs are probabilistic and "
        "require expert verification — see /api docs for status semantics "
        "(OBSERVED / RECONSTRUCTED / RETRIEVED / INFERRED / UNCERTAIN)."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Creates tables for the configured DATABASE_URL (SQLite by default for
    # zero-config local dev; point DATABASE_URL at Postgres for production
    # and use Alembic migrations instead of create_all there).
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "docs": "/docs",
        "api_health": "/api/health",
        "frontend": "http://localhost:5173",
        "message": "Backend API is running. Access the web UI at http://localhost:5173 or API docs at /docs."
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "demo_mode": settings.USE_DEMO_PROVIDERS,
        "llm_provider": settings.LLM_PROVIDER,
    }


app.include_router(auth.router)
app.include_router(analyses.router)
app.include_router(settings_route.router)
