"""
Application configuration.

Everything here is driven by environment variables (see .env.example at the
project root). Nothing is hardcoded. If a variable is missing, sensible
local-development defaults are used so the app can still boot in DEMO mode.
"""
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- General ---
    APP_NAME: str = "EPIGRAPH-AI"
    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    API_V1_PREFIX: str = "/api"

    # --- Security ---
    JWT_SECRET: str = "CHANGE_ME_DEV_ONLY_INSECURE_SECRET"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # --- Database ---
    # Defaults to a local SQLite file so the project runs with zero external
    # services for demo/dev purposes. Point this at Postgres in production:
    # postgresql+psycopg2://user:password@localhost:5432/digital_archaeologist
    DATABASE_URL: str = "sqlite:///./digital_archaeologist.db"

    # --- Vector DB (RAG) ---
    VECTOR_DATABASE_URL: str = ""  # e.g. postgresql+psycopg2://... (with pgvector)

    # --- Neo4j (Knowledge Graph) ---
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = ""

    # --- LLM provider ---
    LLM_PROVIDER: Literal["claude", "openai_compatible", "local", "demo"] = "demo"
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""  # for OpenAI-compatible / local servers
    LLM_MODEL: str = "claude-sonnet-4-6"

    # --- Feature-provider mode ---
    # When true (or when the corresponding model/API key/service isn't
    # configured), every AI module falls back to its Demo provider, which is
    # clearly labelled as DEMO/FALLBACK in every response it returns.
    USE_DEMO_PROVIDERS: bool = True

    # --- File uploads ---
    UPLOAD_DIR: str = os.environ.get(
        "UPLOAD_DIR",
        str(Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw")
        if (Path(__file__).resolve().parent.parent.parent.parent / "data").exists()
        else "../data/raw"
    )
    PROCESSED_DIR: str = os.environ.get(
        "PROCESSED_DIR",
        str(Path(__file__).resolve().parent.parent.parent.parent / "data" / "processed")
        if (Path(__file__).resolve().parent.parent.parent.parent / "data").exists()
        else "../data/processed"
    )
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_IMAGE_TYPES: tuple = (
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
        "image/pjpeg",
        "image/x-png",
    )

    # --- CORS ---
    CORS_ORIGINS: tuple = ("http://localhost:5173",)


@lru_cache
def get_settings() -> Settings:
    return Settings()
