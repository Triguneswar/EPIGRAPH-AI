import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.ai.script_classifier import get_script_classifier
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.models import (
    Analysis,
    AnalysisStatus,
    ImageRecord,
    OCRResult as OCRResultModel,
    PreprocessingResult,
    ReconstructionResult as ReconstructionResultModel,
    ScriptPrediction,
    User,
)
from app.ocr.providers import get_ocr_provider
from app.reconstruction.providers import get_reconstruction_provider
from app.schemas.schemas import AnalysisOut
from app.vision.preprocessing import preprocess_image

router = APIRouter(prefix="/api/analyses", tags=["analyses"])
settings = get_settings()


def _eager_options():
    """Return joinedload options to eagerly fetch all analysis relationships."""
    return [
        joinedload(Analysis.image),
        joinedload(Analysis.preprocessing),
        joinedload(Analysis.script_prediction),
        joinedload(Analysis.ocr_result),
        joinedload(Analysis.reconstruction),
        joinedload(Analysis.translation),
    ]


def _analysis_or_404(analysis_id: str, user: User, db: Session) -> Analysis:
    analysis = (
        db.query(Analysis)
        .options(*_eager_options())
        .filter(Analysis.id == analysis_id, Analysis.user_id == user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@router.post("", response_model=AnalysisOut, status_code=201)
async def create_analysis(
    file: UploadFile = File(...),
    auto_run: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    orig_ext = os.path.splitext(file.filename or "")[1].lower()
    valid_ext = orig_ext in [".jpg", ".jpeg", ".jfif", ".jpe", ".png", ".webp"]
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES and not valid_ext:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {file.content_type}")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")

    analysis = Analysis(user_id=user.id, status=AnalysisStatus.UPLOADED)
    db.add(analysis)
    db.flush()

    orig_ext = os.path.splitext(file.filename)[1].lower()
    if orig_ext in [".jfif", ".jpe", ".jpeg"]:
        safe_ext = ".jpg"
    elif orig_ext not in [".jpg", ".png", ".webp"]:
        safe_ext = ".png"
    else:
        safe_ext = orig_ext

    safe_name = f"{analysis.id}_{uuid.uuid4().hex[:8]}{safe_ext}"
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(settings.UPLOAD_DIR, safe_name)
    with open(save_path, "wb") as f:
        f.write(contents)

    try:
        import cv2

        img = cv2.imread(save_path)
        height, width = (img.shape[0], img.shape[1]) if img is not None else (None, None)
    except Exception:
        width = height = None

    image_record = ImageRecord(
        analysis_id=analysis.id,
        original_path=save_path,
        filename=file.filename,
        width=width,
        height=height,
        file_size_bytes=len(contents),
        content_type=file.content_type,
    )
    db.add(image_record)
    db.commit()
    db.refresh(analysis)

    if auto_run:
        analysis = _execute_full_pipeline(analysis, db)

    # Re-query with eager loading to ensure all relationships are populated for the response
    analysis = (
        db.query(Analysis)
        .options(*_eager_options())
        .filter(Analysis.id == analysis.id)
        .first()
    )
    return analysis


@router.get("", response_model=list[AnalysisOut])
def list_analyses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Analysis)
        .options(*_eager_options())
        .filter(Analysis.user_id == user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _analysis_or_404(analysis_id, user, db)


@router.get("/{analysis_id}/image")
def get_analysis_image(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    if not analysis.image or not os.path.exists(analysis.image.original_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(analysis.image.original_path)


@router.get("/{analysis_id}/processed_image")
def get_analysis_processed_image(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    if not analysis.preprocessing or not os.path.exists(analysis.preprocessing.processed_path):
        raise HTTPException(status_code=404, detail="Processed image file not found")
    return FileResponse(analysis.preprocessing.processed_path)


@router.delete("/{analysis_id}", status_code=204)
def delete_analysis(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    db.delete(analysis)
    db.commit()


@router.post("/{analysis_id}/preprocess")
def run_preprocessing(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    if not analysis.image:
        raise HTTPException(status_code=400, detail="No image uploaded for this analysis")

    analysis.status = AnalysisStatus.PREPROCESSING
    db.commit()

    base_name = os.path.splitext(os.path.basename(analysis.image.original_path))[0]
    out_name = f"{base_name}_processed.png"
    out_path = os.path.join(settings.PROCESSED_DIR, out_name)
    try:
        result = preprocess_image(analysis.image.original_path, out_path)
    except Exception as e:
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=422, detail=str(e))

    if analysis.preprocessing:
        db.delete(analysis.preprocessing)
        db.flush()

    record = PreprocessingResult(
        analysis_id=analysis.id,
        processed_path=result.processed_path,
        steps_applied=result.steps_applied,
        enhancement_metadata=result.metadata,
    )
    db.add(record)
    analysis.status = AnalysisStatus.SCRIPT_DETECTION
    db.commit()
    return {"processed_path": result.processed_path, "steps_applied": result.steps_applied, "metadata": result.metadata}


@router.post("/{analysis_id}/script")
def run_script_detection(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    if not analysis.image:
        raise HTTPException(status_code=400, detail="No image found for this analysis")

    from app.ai.epigraph_vision_engine import get_epigraph_vision_engine
    engine = get_epigraph_vision_engine()
    prep_path = analysis.preprocessing.processed_path if analysis.preprocessing else None
    result = engine.analyze_inscription(analysis.image.original_path, prep_path)

    if analysis.script_prediction:
        db.delete(analysis.script_prediction)
        db.flush()

    alts = list(result.script_alternatives)
    alts.insert(0, {
        "script": result.detected_script,
        "language": result.detected_language,
        "period": result.period_era,
        "confidence": result.confidence,
    })
    record = ScriptPrediction(
        analysis_id=analysis.id,
        script=result.detected_script,
        confidence=result.confidence,
        alternatives=alts,
        provider=result.provider,
    )
    db.add(record)
    analysis.status = AnalysisStatus.OCR
    db.commit()
    return {"script": result.detected_script, "confidence": result.confidence, "alternatives": alts, "provider": result.provider}


@router.post("/{analysis_id}/ocr")
def run_ocr(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    if not analysis.image:
        raise HTTPException(status_code=400, detail="No image found for this analysis")

    from app.ai.epigraph_vision_engine import get_epigraph_vision_engine
    engine = get_epigraph_vision_engine()
    prep_path = analysis.preprocessing.processed_path if analysis.preprocessing else None
    result = engine.analyze_inscription(analysis.image.original_path, prep_path)

    if analysis.ocr_result:
        db.delete(analysis.ocr_result)
        db.flush()

    record = OCRResultModel(
        analysis_id=analysis.id,
        text=result.transcription,
        confidence=result.confidence,
        lines=result.lines,
        characters=[],
        uncertain_regions=result.uncertain_spans,
        provider=result.provider,
    )
    db.add(record)
    analysis.status = AnalysisStatus.RECONSTRUCTION
    db.commit()
    return {
        "text": result.transcription,
        "confidence": result.confidence,
        "uncertain_regions": result.uncertain_spans,
        "provider": result.provider,
    }


@router.post("/{analysis_id}/reconstruct")
def run_reconstruction(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    if not analysis.image:
        raise HTTPException(status_code=400, detail="No image found for this analysis")

    from app.ai.epigraph_vision_engine import get_epigraph_vision_engine
    engine = get_epigraph_vision_engine()
    prep_path = analysis.preprocessing.processed_path if analysis.preprocessing else None
    result = engine.analyze_inscription(analysis.image.original_path, prep_path)

    if analysis.reconstruction:
        db.delete(analysis.reconstruction)
        db.flush()

    candidates = [
        {
            "text": result.reconstructed_text or result.transcription,
            "confidence": result.confidence,
            "reason": f"Paleographic decipherment ({result.detected_language}, {result.period_era})",
        }
    ]
    record = ReconstructionResultModel(
        analysis_id=analysis.id,
        observed_text=result.transcription,
        candidates=candidates,
        provider=result.provider,
        requires_expert_verification=False,
    )
    db.add(record)
    analysis.status = AnalysisStatus.TRANSLATION
    db.commit()
    return {
        "observed_text": result.transcription,
        "candidates": candidates,
        "requires_expert_verification": False,
        "provider": result.provider,
    }


@router.post("/{analysis_id}/translate")
def run_translation(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    if not analysis.image:
        raise HTTPException(status_code=400, detail="No image found for this analysis")

    from app.ai.epigraph_vision_engine import get_epigraph_vision_engine
    engine = get_epigraph_vision_engine()
    prep_path = analysis.preprocessing.processed_path if analysis.preprocessing else None
    result = engine.analyze_inscription(analysis.image.original_path, prep_path)

    if analysis.translation:
        db.delete(analysis.translation)
        db.flush()

    english_full = result.english_translation
    if not english_full.startswith("["):
        english_full = f"[{result.detected_language} · {result.period_era}]\n\n{english_full}"

    meta_spans = [
        {
            "language": result.detected_language,
            "era": result.period_era,
            "transliteration": result.transliteration,
            "multilingual": result.multilingual,
            "hindi": result.hindi_translation,
            "tamil": result.tamil_translation or result.vernacular_translation,
            "telugu": result.telugu_translation,
            "kannada": result.kannada_translation,
            "vernacular": result.vernacular_translation,
        }
    ]
    from app.models.models import Translation
    record = Translation(
        analysis_id=analysis.id,
        english=english_full,
        modern_tamil=result.tamil_translation or result.vernacular_translation,
        confidence=result.confidence,
        uncertain_spans=meta_spans,
        provider=result.provider,
    )
    db.add(record)
    analysis.status = AnalysisStatus.COMPLETED
    db.commit()
    return {
        "english": english_full,
        "modern_tamil": result.tamil_translation or result.vernacular_translation,
        "confidence": result.confidence,
        "uncertain_spans": meta_spans,
        "multilingual": result.multilingual,
        "provider": result.provider,
    }


def _execute_full_pipeline(analysis: Analysis, db: Session) -> Analysis:
    if not analysis.image:
        raise HTTPException(status_code=400, detail="No image uploaded for this analysis")

    # 1. Preprocessing
    base_name = os.path.splitext(os.path.basename(analysis.image.original_path))[0]
    out_name = f"{base_name}_processed.png"
    out_path = os.path.join(settings.PROCESSED_DIR, out_name)
    try:
        prep_result = preprocess_image(analysis.image.original_path, out_path)
    except Exception as e:
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=422, detail=str(e))

    if analysis.preprocessing:
        db.delete(analysis.preprocessing)
        db.flush()

    record_prep = PreprocessingResult(
        analysis_id=analysis.id,
        processed_path=prep_result.processed_path,
        steps_applied=prep_result.steps_applied,
        enhancement_metadata=prep_result.metadata,
    )
    db.add(record_prep)
    db.flush()

    # 2. Multimodal Vision Epigraphic Analysis
    from app.ai.epigraph_vision_engine import get_epigraph_vision_engine
    vision_engine = get_epigraph_vision_engine()
    decipher_res = vision_engine.analyze_inscription(
        analysis.image.original_path,
        prep_result.processed_path,
    )

    # 3. Script Identification
    if analysis.script_prediction:
        db.delete(analysis.script_prediction)
        db.flush()
    alts = list(decipher_res.script_alternatives)
    alts.insert(0, {
        "script": decipher_res.detected_script,
        "language": decipher_res.detected_language,
        "period": decipher_res.period_era,
        "confidence": decipher_res.confidence,
    })
    record_script = ScriptPrediction(
        analysis_id=analysis.id,
        script=decipher_res.detected_script,
        confidence=decipher_res.confidence,
        alternatives=alts,
        provider=decipher_res.provider,
    )
    db.add(record_script)
    db.flush()

    # 4. OCR Text Extraction
    if analysis.ocr_result:
        db.delete(analysis.ocr_result)
        db.flush()
    record_ocr = OCRResultModel(
        analysis_id=analysis.id,
        text=decipher_res.transcription,
        confidence=decipher_res.confidence,
        lines=decipher_res.lines,
        characters=[],
        uncertain_regions=decipher_res.uncertain_spans,
        provider=decipher_res.provider,
    )
    db.add(record_ocr)
    db.flush()

    # 5. Text Reconstruction
    if analysis.reconstruction:
        db.delete(analysis.reconstruction)
        db.flush()
    record_recon = ReconstructionResultModel(
        analysis_id=analysis.id,
        observed_text=decipher_res.transcription,
        candidates=[
            {
                "text": decipher_res.reconstructed_text or decipher_res.transcription,
                "confidence": decipher_res.confidence,
                "reason": f"Epigraphic & paleographic decipherment ({decipher_res.detected_language}, {decipher_res.period_era})",
            }
        ],
        provider=decipher_res.provider,
        requires_expert_verification=False,
    )
    db.add(record_recon)
    db.flush()

    # 6. English Translation
    if analysis.translation:
        db.delete(analysis.translation)
        db.flush()
    from app.models.models import Translation
    english_full = decipher_res.english_translation
    if not english_full.startswith("["):
        english_full = f"[{decipher_res.detected_language} · {decipher_res.period_era}]\n\n{english_full}"

    meta_spans = [
        {
            "language": decipher_res.detected_language,
            "era": decipher_res.period_era,
            "transliteration": decipher_res.transliteration,
            "multilingual": decipher_res.multilingual,
            "hindi": decipher_res.hindi_translation,
            "tamil": decipher_res.tamil_translation or decipher_res.vernacular_translation,
            "telugu": decipher_res.telugu_translation,
            "kannada": decipher_res.kannada_translation,
            "vernacular": decipher_res.vernacular_translation,
        }
    ]
    record_trans = Translation(
        analysis_id=analysis.id,
        english=english_full,
        modern_tamil=decipher_res.tamil_translation or decipher_res.vernacular_translation,
        confidence=decipher_res.confidence,
        uncertain_spans=meta_spans,
        provider=decipher_res.provider,
    )
    db.add(record_trans)
    db.flush()

    # 7. Extract Historical Entities for Knowledge Graph
    from app.models.models import HistoricalEntity, EvidenceStatus
    db.query(HistoricalEntity).filter(HistoricalEntity.analysis_id == analysis.id).delete()
    if decipher_res.named_entities:
        for ent in decipher_res.named_entities:
            db.add(HistoricalEntity(
                analysis_id=analysis.id,
                name=ent.get("name", "Unknown"),
                type=ent.get("type", "INSCRIPTION_ENTITY"),
                confidence=decipher_res.confidence,
                status=EvidenceStatus.OBSERVED,
            ))

    analysis.status = AnalysisStatus.COMPLETED
    db.commit()

    analysis = (
        db.query(Analysis)
        .options(*_eager_options())
        .filter(Analysis.id == analysis.id)
        .first()
    )
    return analysis


@router.post("/{analysis_id}/pipeline", response_model=AnalysisOut)
def run_full_pipeline(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    return _execute_full_pipeline(analysis, db)
