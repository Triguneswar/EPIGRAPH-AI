"""
Application configuration for EPIGRAPH-AI.

Driven by environment variables (.env at project root).
Supports multimodal vision models (Google Gemini, OpenAI GPT-4o, Anthropic Claude)
and local paleographic vision fallback.
"""
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    _root_dir = Path(__file__).resolve().parent.parent.parent.parent
    _backend_dir = Path(__file__).resolve().parent.parent.parent

    model_config = SettingsConfigDict(
        env_file=(
            str(_root_dir / ".env"),
            str(_backend_dir / ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- General ---
    APP_NAME: str = "EPIGRAPH-AI"
    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    API_V1_PREFIX: str = "/api"

    # --- Security ---
    JWT_SECRET: str = "CHANGE_ME_DEV_ONLY_INSECURE_SECRET"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./digital_archaeologist.db"

    # --- Vector DB (RAG) ---
    VECTOR_DATABASE_URL: str = ""

    # --- Neo4j (Knowledge Graph) ---
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = ""

    # --- LLM & Multimodal Vision Providers ---
    # One of: gemini | openai_compatible | claude | local | demo
    LLM_PROVIDER: str = "gemini"
    LLM_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_BASE_URL: str = ""  # for OpenAI-compatible / local servers
    LLM_MODEL: str = "gemini-flash-lite-latest"

    # --- Feature-provider mode ---
    # Set to False so real vision analysis & paleography run on every photo
    USE_DEMO_PROVIDERS: bool = False

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
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_IMAGE_TYPES: tuple = (
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
        "image/pjpeg",
        "image/x-png",
    )

    # --- CORS ---
    CORS_ORIGINS: tuple = ("http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000")


@lru_cache
def get_settings() -> Settings:
    # Also check fallback locations for .env if root wasn't found
    root_env = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
    if not root_env.exists() and backend_env.exists():
        return Settings(_env_file=str(backend_env))
    return Settings()


def update_env_setting(key: str, value: str) -> None:
    """Persist an environment variable into .env (both root and backend dirs) and update process env."""
    os.environ[key] = value
    root_env = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
    
    for env_path in [root_env, backend_env]:
        try:
            lines = []
            found = False
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith(f"{key}="):
                            lines.append(f"{key}={value}\n")
                            found = True
                        else:
                            lines.append(line)
            if not found:
                lines.append(f"{key}={value}\n")
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception:
            pass
    # Clear cache so next get_settings() re-reads
    get_settings.cache_clear()
