"""
Settings routes for EPIGRAPH-AI.
Allows viewing and updating AI Multimodal Vision provider keys (Gemini, OpenAI, Claude).
"""
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import httpx

from app.api.deps import get_current_user
from app.core.config import get_settings, update_env_setting
from app.models.models import User

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    api_key: Optional[str] = None
    llm_provider: Optional[str] = "gemini"
    model: Optional[str] = "gemini-2.0-flash"


class SettingsOut(BaseModel):
    llm_provider: str
    has_api_key: bool
    masked_key: str
    model: str
    active_engine: str
    is_multimodal_live: bool


@router.get("", response_model=SettingsOut)
def get_user_settings(user: User = Depends(get_current_user)):
    settings = get_settings()

    # Determine key
    key = (
        settings.GEMINI_API_KEY
        or os.environ.get("GEMINI_API_KEY")
        or settings.OPENAI_API_KEY
        or os.environ.get("OPENAI_API_KEY")
        or settings.ANTHROPIC_API_KEY
        or os.environ.get("ANTHROPIC_API_KEY")
        or settings.LLM_API_KEY
    )

    has_key = bool(key and len(key.strip()) > 5)
    masked = ""
    if has_key:
        clean_key = key.strip()
        masked = f"{clean_key[:6]}...{clean_key[-4:]}" if len(clean_key) > 10 else "******"

    provider = settings.LLM_PROVIDER or "gemini"
    model = settings.LLM_MODEL or "gemini-2.0-flash"

    if has_key:
        if "gemini" in provider.lower() or key.startswith("AIza"):
            active_engine = f"Google Gemini Vision ({model})"
        elif "openai" in provider.lower() or key.startswith("sk-"):
            active_engine = f"OpenAI Vision ({model})"
        elif "claude" in provider.lower() or key.startswith("sk-ant"):
            active_engine = f"Anthropic Claude Vision ({model})"
        else:
            active_engine = f"Multimodal AI Vision ({provider})"
        is_live = True
    else:
        active_engine = "EPIGRAPH-AI Adaptive Paleographic Engine (Local Vision)"
        is_live = False

    return SettingsOut(
        llm_provider=provider,
        has_api_key=has_key,
        masked_key=masked,
        model=model,
        active_engine=active_engine,
        is_multimodal_live=is_live,
    )


@router.post("", response_model=SettingsOut)
def update_user_settings(data: SettingsUpdate, user: User = Depends(get_current_user)):
    settings = get_settings()
    provider = (data.llm_provider or "gemini").lower().strip()
    model = (data.model or "gemini-2.0-flash").strip()

    if data.api_key is not None:
        key = data.api_key.strip()
        if key:
            if provider == "gemini" or key.startswith("AIza"):
                update_env_setting("GEMINI_API_KEY", key)
                update_env_setting("LLM_PROVIDER", "gemini")
            elif provider == "openai_compatible" or (key.startswith("sk-") and not key.startswith("sk-ant")):
                update_env_setting("OPENAI_API_KEY", key)
                update_env_setting("LLM_PROVIDER", "openai_compatible")
            elif provider == "claude" or key.startswith("sk-ant"):
                update_env_setting("ANTHROPIC_API_KEY", key)
                update_env_setting("LLM_PROVIDER", "claude")
            else:
                update_env_setting("LLM_API_KEY", key)
                update_env_setting("LLM_PROVIDER", provider)
        else:
            # Clearing keys
            update_env_setting("GEMINI_API_KEY", "")
            update_env_setting("OPENAI_API_KEY", "")
            update_env_setting("ANTHROPIC_API_KEY", "")
            update_env_setting("LLM_API_KEY", "")

    if model:
        update_env_setting("LLM_MODEL", model)

    update_env_setting("USE_DEMO_PROVIDERS", "false")

    # Re-read
    return get_user_settings(user)


@router.post("/test")
async def test_api_key(data: SettingsUpdate, user: User = Depends(get_current_user)):
    """Tests the provided or saved API key with a fast ping to verify validity."""
    key = data.api_key.strip() if data.api_key else ""
    provider = (data.llm_provider or "gemini").lower().strip()

    if not key:
        settings = get_settings()
        key = (
            settings.GEMINI_API_KEY
            or os.environ.get("GEMINI_API_KEY")
            or settings.OPENAI_API_KEY
            or settings.LLM_API_KEY
        )

    if not key:
        raise HTTPException(status_code=400, detail="No API Key provided to test.")

    if provider == "gemini" or key.startswith("AIza"):
        candidate_models = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-pro-latest"]
        for i, m in enumerate(candidate_models):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
            payload = {
                "contents": [{"parts": [{"text": "Hello, respond with OK"}]}],
                "generationConfig": {"maxOutputTokens": 10},
            }
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        return {"success": True, "message": f"Gemini API Key verified and working successfully with {m}!"}
                    elif i == len(candidate_models) - 1:
                        return {"success": False, "message": f"Gemini API returned status {resp.status_code}: {resp.text[:200]}"}
            except Exception as e:
                if i == len(candidate_models) - 1:
                    return {"success": False, "message": f"Connection error: {str(e)}"}

    elif provider == "openai_compatible" or key.startswith("sk-"):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    return {"success": True, "message": "OpenAI API Key verified and working successfully!"}
                else:
                    return {"success": False, "message": f"OpenAI returned status {resp.status_code}: {resp.text[:200]}"}
        except Exception as e:
            return {"success": False, "message": f"Connection error: {str(e)}"}

    return {"success": True, "message": "API Key saved successfully."}
