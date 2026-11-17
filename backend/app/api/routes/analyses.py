import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
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
    if not analysis.preprocessing:
        raise HTTPException(status_code=400, detail="Run preprocessing before script detection")

    classifier = get_script_classifier(use_demo=settings.USE_DEMO_PROVIDERS)
    result = classifier.classify(analysis.preprocessing.processed_path)

    if analysis.script_prediction:
        db.delete(analysis.script_prediction)
        db.flush()

    record = ScriptPrediction(
        analysis_id=analysis.id,
        script=result.script,
        confidence=result.confidence,
        alternatives=result.alternatives,
        provider=result.provider,
    )
    db.add(record)
    analysis.status = AnalysisStatus.OCR
    db.commit()
    return {"script": result.script, "confidence": result.confidence, "alternatives": result.alternatives, "provider": result.provider}


@router.post("/{analysis_id}/ocr")
def run_ocr(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    if not analysis.preprocessing:
        raise HTTPException(status_code=400, detail="Run preprocessing before OCR")

    provider = get_ocr_provider(use_demo=settings.USE_DEMO_PROVIDERS)
    result = provider.extract_text(analysis.preprocessing.processed_path)

    if analysis.ocr_result:
        db.delete(analysis.ocr_result)
        db.flush()

    record = OCRResultModel(
        analysis_id=analysis.id,
        text=result.text,
        confidence=result.confidence,
        lines=result.lines,
        characters=result.characters,
        uncertain_regions=result.uncertain_regions,
        provider=result.provider,
    )
    db.add(record)
    analysis.status = AnalysisStatus.RECONSTRUCTION
    db.commit()
    return {
        "text": result.text,
        "confidence": result.confidence,
        "uncertain_regions": result.uncertain_regions,
        "provider": result.provider,
    }


@router.post("/{analysis_id}/reconstruct")
def run_reconstruction(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    if not analysis.ocr_result:
        raise HTTPException(status_code=400, detail="Run OCR before reconstruction")

    provider = get_reconstruction_provider(use_demo=settings.USE_DEMO_PROVIDERS)
    result = provider.reconstruct(analysis.ocr_result.text)

    if analysis.reconstruction:
        db.delete(analysis.reconstruction)
        db.flush()

    record = ReconstructionResultModel(
        analysis_id=analysis.id,
        observed_text=result.observed_text,
        candidates=[c.__dict__ for c in result.candidates],
        provider=result.provider,
        requires_expert_verification=result.requires_expert_verification,
    )
    db.add(record)
    analysis.status = AnalysisStatus.TRANSLATION
    db.commit()
    return {
        "observed_text": result.observed_text,
        "candidates": [c.__dict__ for c in result.candidates],
        "requires_expert_verification": result.requires_expert_verification,
        "provider": result.provider,
    }


@router.post("/{analysis_id}/translate")
def run_translation(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = _analysis_or_404(analysis_id, user, db)
    ocr_text = analysis.ocr_result.text if analysis.ocr_result else ""
    script = analysis.script_prediction.script if analysis.script_prediction else "Unknown"

    from app.translation.providers import EpigraphTranslator
    translator = EpigraphTranslator(use_demo=settings.USE_DEMO_PROVIDERS)
    result = translator.translate(ocr_text, script=script)

    if analysis.translation:
        db.delete(analysis.translation)
        db.flush()

    from app.models.models import Translation
    record = Translation(
        analysis_id=analysis.id,
        english=result.english,
        modern_tamil=result.modern_tamil,
        confidence=result.confidence,
        uncertain_spans=result.uncertain_spans,
        provider=result.provider,
    )
    db.add(record)
    analysis.status = AnalysisStatus.COMPLETED
    db.commit()
    return {
        "english": result.english,
        "modern_tamil": result.modern_tamil,
        "confidence": result.confidence,
        "uncertain_spans": result.uncertain_spans,
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

    # 2. Script Identification
    classifier = get_script_classifier(use_demo=settings.USE_DEMO_PROVIDERS)
    script_res = classifier.classify(prep_result.processed_path)
    if analysis.script_prediction:
        db.delete(analysis.script_prediction)
        db.flush()
    record_script = ScriptPrediction(
        analysis_id=analysis.id,
        script=script_res.script,
        confidence=script_res.confidence,
        alternatives=script_res.alternatives,
        provider=script_res.provider,
    )
    db.add(record_script)
    db.flush()

    # 3. OCR Text Extraction
    ocr_prov = get_ocr_provider(use_demo=settings.USE_DEMO_PROVIDERS)
    ocr_res = ocr_prov.extract_text(prep_result.processed_path)
    if analysis.ocr_result:
        db.delete(analysis.ocr_result)
        db.flush()
    record_ocr = OCRResultModel(
        analysis_id=analysis.id,
        text=ocr_res.text,
        confidence=ocr_res.confidence,
        lines=ocr_res.lines,
        characters=ocr_res.characters,
        uncertain_regions=ocr_res.uncertain_regions,
        provider=ocr_res.provider,
    )
    db.add(record_ocr)
    db.flush()

    # 4. Text Reconstruction
    recon_prov = get_reconstruction_provider(use_demo=settings.USE_DEMO_PROVIDERS)
    recon_res = recon_prov.reconstruct(ocr_res.text)
    if analysis.reconstruction:
        db.delete(analysis.reconstruction)
        db.flush()
    record_recon = ReconstructionResultModel(
        analysis_id=analysis.id,
        observed_text=recon_res.observed_text,
        candidates=[c.__dict__ for c in recon_res.candidates],
        provider=recon_res.provider,
        requires_expert_verification=recon_res.requires_expert_verification,
    )
    db.add(record_recon)
    db.flush()

    # 5. English Translation
    from app.translation.providers import EpigraphTranslator
    translator = EpigraphTranslator(use_demo=settings.USE_DEMO_PROVIDERS)
    trans_res = translator.translate(ocr_res.text, script=script_res.script)
    if analysis.translation:
        db.delete(analysis.translation)
        db.flush()
    from app.models.models import Translation
    record_trans = Translation(
        analysis_id=analysis.id,
        english=trans_res.english,
        modern_tamil=trans_res.modern_tamil,
        confidence=trans_res.confidence,
        uncertain_spans=trans_res.uncertain_spans,
        provider=trans_res.provider,
    )
    db.add(record_trans)

    analysis.status = AnalysisStatus.COMPLETED
    db.commit()
    # Re-query with eager loading so all relationships are populated
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
