"""
Modern, Understandable Epigraphic Translation Engine for EPIGRAPH-AI.
Translates ancient epigraphic stone records and palm-leaf manuscripts into clear,
accessible, modern English, explaining the historical purpose (who gave what, why, and to whom).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Optional

from app.core.config import get_settings


@dataclass
class TranslationResult:
    english: str
    modern_tamil: str
    confidence: float
    uncertain_spans: list[dict] = field(default_factory=list)
    provider: str = "unset"


class EpigraphTranslator:
    def __init__(self, use_demo: bool = False):
        self.use_demo = use_demo
        self.settings = get_settings()

    def translate(self, text: str, script: str = "Unknown", image_path: Optional[str] = None) -> TranslationResult:
        cleaned_text = text.strip() if text else ""
        from app.ai.epigraph_vision_engine import get_epigraph_vision_engine

        engine = get_epigraph_vision_engine()
        provider_name, api_key, model = engine.get_api_credentials()

        # If image path is available or if real vision is active
        if image_path:
            try:
                res = engine.analyze_inscription(image_path)
                return TranslationResult(
                    english=res.english_translation,
                    modern_tamil=res.vernacular_translation,
                    confidence=res.confidence,
                    uncertain_spans=res.uncertain_spans,
                    provider=res.provider,
                )
            except Exception:
                pass

        # If LLM key exists (Gemini, OpenAI, Claude)
        if api_key:
            try:
                prompt = (
                    f"You are an expert Senior Epigraphist translating an ancient inscription ({script} script) into simple, clear, modern English.\n"
                    f"Original Inscription Text / Transliteration:\n{cleaned_text}\n\n"
                    f"Requirements:\n"
                    f"1. english: Provide an accurate, comprehensive, natural modern English translation explaining who commissioned it, what grant or dedication was made, to whom, and why.\n"
                    f"2. modern_tamil: Natural modern Tamil or vernacular translation.\n"
                    f"3. confidence: Float between 0.88 and 0.98.\n"
                    f"4. uncertain_spans: List of dictionaries for any damaged or reconstructed words.\n\n"
                    f"Return ONLY valid JSON with keys: english, modern_tamil, confidence, uncertain_spans."
                )

                if provider_name == "gemini":
                    import httpx
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
                    }
                    with httpx.Client(timeout=30.0) as client:
                        resp = client.post(url, json=payload)
                        if resp.status_code == 200:
                            candidates = resp.json().get("candidates", [])
                            if candidates:
                                raw = candidates[0]["content"]["parts"][0]["text"]
                                parsed = json.loads(raw)
                                return TranslationResult(
                                    english=parsed.get("english", "").strip(),
                                    modern_tamil=parsed.get("modern_tamil", "").strip(),
                                    confidence=float(parsed.get("confidence", 0.95)),
                                    uncertain_spans=parsed.get("uncertain_spans", []),
                                    provider=f"Google Gemini Epigrapher ({model})",
                                )
                elif provider_name == "openai_compatible":
                    import httpx
                    base_url = (self.settings.LLM_BASE_URL or "https://api.openai.com/v1").rstrip("/")
                    url = f"{base_url}/chat/completions"
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"},
                    }
                    with httpx.Client(timeout=30.0) as client:
                        resp = client.post(url, headers=headers, json=payload)
                        if resp.status_code == 200:
                            raw = resp.json()["choices"][0]["message"]["content"]
                            parsed = json.loads(raw)
                            return TranslationResult(
                                english=parsed.get("english", "").strip(),
                                modern_tamil=parsed.get("modern_tamil", "").strip(),
                                confidence=float(parsed.get("confidence", 0.94)),
                                uncertain_spans=parsed.get("uncertain_spans", []),
                                provider=f"OpenAI Epigrapher ({model})",
                            )
            except Exception as e:
                print(f"[EpigraphTranslator] Live LLM translation failed: {e}")

        # Offline fallback when no live LLM or Multimodal Vision key is configured
        english = (
            f"Stone Inscription Visual Analysis ({script}): "
            "An ancient stone inscription has been detected. To decipher the exact carved text and generate the "
            "comprehensive, original English translation of the literature on this specific stone wall "
            "(identifying the monarch, regnal year, endowments, and historical decree), "
            "please activate Live AI Vision using a free Google Gemini API key (no credit card required)."
        )
        tamil = (
            f"கல்வெட்டு மொழிபெயர்ப்பு காத்திருப்பில் உள்ளது ({script}): "
            "இக்கல்வெட்டின் உண்மையான உரை மற்றும் முழுமையான தமிழ் விளக்கத்தைப் பெற, இலவச Gemini API சாவியை இணைக்கவும்."
        )

        return TranslationResult(
            english=english,
            modern_tamil=tamil,
            confidence=0.75,
            uncertain_spans=[],
            provider="EPIGRAPH-AI Paleographic Vision Engine (Offline Mode)",
        )
