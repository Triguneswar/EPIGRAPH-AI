from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, EmailStr


# ---------- Auth ----------
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Analysis Result Sub-schemas ----------
class PreprocessingResultOut(BaseModel):
    processed_path: str
    steps_applied: list[str] = []
    enhancement_metadata: dict[str, Any] = {}

    class Config:
        from_attributes = True


class ScriptPredictionOut(BaseModel):
    script: str
    confidence: float
    alternatives: list[dict[str, Any]] = []
    provider: str

    class Config:
        from_attributes = True


class OCRResultOut(BaseModel):
    text: str
    confidence: float
    lines: list[Any] = []
    characters: list[Any] = []
    uncertain_regions: list[Any] = []
    provider: str

    class Config:
        from_attributes = True


class ReconstructionCandidate(BaseModel):
    text: str
    confidence: float
    reason: str


class ReconstructionOut(BaseModel):
    observed_text: str
    candidates: list[ReconstructionCandidate] = []
    requires_expert_verification: bool = False
    provider: str

    class Config:
        from_attributes = True


class TranslationOut(BaseModel):
    modern_tamil: Optional[str] = None
    english: Optional[str] = None
    confidence: Optional[float] = None
    uncertain_spans: list[Any] = []
    multilingual: Optional[dict[str, str]] = None
    provider: str

    class Config:
        from_attributes = True


class ImageRecordOut(BaseModel):
    id: str
    original_path: str
    filename: str
    width: Optional[int] = None
    height: Optional[int] = None

    class Config:
        from_attributes = True


# ---------- Analysis Main Schema ----------
class AnalysisOut(BaseModel):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    image: Optional[ImageRecordOut] = None
    preprocessing: Optional[PreprocessingResultOut] = None
    script_prediction: Optional[ScriptPredictionOut] = None
    ocr_result: Optional[OCRResultOut] = None
    reconstruction: Optional[ReconstructionOut] = None
    translation: Optional[TranslationOut] = None

    class Config:
        from_attributes = True
