"""
SQLAlchemy ORM models covering the full pipeline described in the spec:
users, analyses, images, preprocessing, script predictions, OCR,
reconstruction, translation, entities, sources, verification, reports.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class AnalysisStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PREPROCESSING = "PREPROCESSING"
    SCRIPT_DETECTION = "SCRIPT_DETECTION"
    OCR = "OCR"
    RECONSTRUCTION = "RECONSTRUCTION"
    TRANSLATION = "TRANSLATION"
    RESEARCH = "RESEARCH"
    ENTITY_EXTRACTION = "ENTITY_EXTRACTION"
    GRAPH_BUILDING = "GRAPH_BUILDING"
    VERIFICATION = "VERIFICATION"
    REPORT_GENERATION = "REPORT_GENERATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EvidenceStatus(str, enum.Enum):
    OBSERVED = "OBSERVED"
    OCR = "OCR"
    RECONSTRUCTED = "RECONSTRUCTED"
    RETRIEVED = "RETRIEVED"
    INFERRED = "INFERRED"
    UNCERTAIN = "UNCERTAIN"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    analyses = relationship("Analysis", back_populates="owner", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.UPLOADED)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="analyses")
    image = relationship("ImageRecord", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    preprocessing = relationship("PreprocessingResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    script_prediction = relationship("ScriptPrediction", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    ocr_result = relationship("OCRResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    reconstruction = relationship("ReconstructionResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    translation = relationship("Translation", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    entities = relationship("HistoricalEntity", back_populates="analysis", cascade="all, delete-orphan")
    sources = relationship("AnalysisSource", back_populates="analysis", cascade="all, delete-orphan")
    verification = relationship("VerificationResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    report = relationship("Report", back_populates="analysis", uselist=False, cascade="all, delete-orphan")


class ImageRecord(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    original_path = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="image")


class PreprocessingResult(Base):
    __tablename__ = "preprocessing_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    processed_path = Column(String, nullable=False)
    steps_applied = Column(JSON, default=list)  # e.g. ["resize","clahe","denoise",...]
    enhancement_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="preprocessing")


class ScriptPrediction(Base):
    __tablename__ = "script_predictions"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    script = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    alternatives = Column(JSON, default=list)  # [{"script":..,"confidence":..}]
    provider = Column(String, default="demo")  # which provider produced this
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="script_prediction")


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    lines = Column(JSON, default=list)
    characters = Column(JSON, default=list)
    uncertain_regions = Column(JSON, default=list)  # damaged/uncertain char spans
    provider = Column(String, default="demo")
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="ocr_result")


class ReconstructionResult(Base):
    __tablename__ = "reconstruction_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    observed_text = Column(Text, nullable=False)
    candidates = Column(JSON, default=list)  # [{"text":..,"confidence":..,"reason":..}]
    provider = Column(String, default="demo")
    requires_expert_verification = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="reconstruction")


class Translation(Base):
    __tablename__ = "translations"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    modern_tamil = Column(Text, nullable=True)
    english = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    uncertain_spans = Column(JSON, default=list)
    provider = Column(String, default="demo")
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="translation")


class HistoricalEntity(Base):
    __tablename__ = "historical_entities"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # PERSON, KING, DYNASTY, TEMPLE, ...
    confidence = Column(Float, nullable=True)
    status = Column(Enum(EvidenceStatus), default=EvidenceStatus.INFERRED)

    analysis = relationship("Analysis", back_populates="entities")


class Source(Base):
    """A historical document / reference ingested into the RAG knowledge base."""
    __tablename__ = "sources"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    year = Column(String, nullable=True)
    publication = Column(String, nullable=True)
    page = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    region = Column(String, nullable=True)
    period = Column(String, nullable=True)
    source_type = Column(String, nullable=True)  # pdf, txt, docx, md
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisSource(Base):
    """Join table: evidence retrieved for a given analysis, with relevance + excerpt."""
    __tablename__ = "analysis_sources"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    source_id = Column(String, ForeignKey("sources.id"), nullable=True)
    relevance_score = Column(Float, nullable=True)
    extracted_evidence = Column(Text, nullable=True)

    analysis = relationship("Analysis", back_populates="sources")
    source = relationship("Source")


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    statements = Column(JSON, default=list)  # [{"claim":..,"status":..,"confidence":..}]
    conflicts = Column(JSON, default=list)   # [{"topic":..,"source_a":..,"source_b":..}]
    overall_confidence = Column(Float, nullable=True)
    requires_human_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="verification")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=gen_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    pdf_path = Column(String, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="report")
