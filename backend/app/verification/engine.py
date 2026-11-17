"""
Evidence-aware verification engine.

Classifies each piece of output produced by the pipeline into one of:
OBSERVED, OCR, RECONSTRUCTED, RETRIEVED, INFERRED, UNCERTAIN

and assembles the final "statements" list shown in the UI/report, plus
source-conflict detection.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Statement:
    claim: str
    status: str  # one of the EvidenceStatus values
    confidence: float | None = None
    evidence: str | None = None


@dataclass
class Conflict:
    topic: str
    source_a: str
    source_b: str
    detail: str


@dataclass
class VerificationSummary:
    statements: list[Statement] = field(default_factory=list)
    conflicts: list[Conflict] = field(default_factory=list)
    overall_confidence: float | None = None
    requires_human_review: bool = False


def build_verification_summary(
    script_prediction: dict | None,
    ocr_result: dict | None,
    reconstruction_result: dict | None,
    translation_result: dict | None,
    retrieved_sources: list[dict] | None,
) -> VerificationSummary:
    statements: list[Statement] = []
    confidences: list[float] = []

    if script_prediction:
        statements.append(
            Statement(
                claim=f"Script classified as {script_prediction['script']}",
                status="OBSERVED",
                confidence=script_prediction["confidence"],
            )
        )
        confidences.append(script_prediction["confidence"])

    if ocr_result:
        statements.append(
            Statement(claim="OCR transcription", status="OCR", confidence=ocr_result["confidence"])
        )
        confidences.append(ocr_result["confidence"])
        if ocr_result.get("uncertain_regions"):
            statements.append(
                Statement(
                    claim=f"{len(ocr_result['uncertain_regions'])} uncertain character region(s) detected",
                    status="UNCERTAIN",
                )
            )

    if reconstruction_result and reconstruction_result.get("candidates"):
        for c in reconstruction_result["candidates"]:
            statements.append(
                Statement(
                    claim=f"Reconstruction candidate: {c['text']}",
                    status="RECONSTRUCTED",
                    confidence=c.get("confidence"),
                    evidence=c.get("reason"),
                )
            )

    if translation_result and translation_result.get("english"):
        statements.append(
            Statement(
                claim="English translation",
                status="RECONSTRUCTED" if translation_result.get("uncertain_spans") else "OBSERVED",
                confidence=translation_result.get("confidence"),
            )
        )

    if retrieved_sources:
        for s in retrieved_sources:
            statements.append(
                Statement(
                    claim=f"Historical context from: {s.get('title')}",
                    status="RETRIEVED",
                    confidence=s.get("relevance_score"),
                    evidence=s.get("extracted_evidence"),
                )
            )
    else:
        statements.append(
            Statement(claim="No supporting historical source found.", status="UNCERTAIN")
        )

    conflicts = _detect_conflicts(retrieved_sources or [])

    overall_confidence = round(sum(confidences) / len(confidences), 3) if confidences else None
    requires_review = bool(conflicts) or (overall_confidence is not None and overall_confidence < 0.6)

    return VerificationSummary(
        statements=statements,
        conflicts=conflicts,
        overall_confidence=overall_confidence,
        requires_human_review=requires_review,
    )


def _detect_conflicts(sources: list[dict]) -> list[Conflict]:
    """
    Placeholder conflict-detection logic: flags when two retrieved sources
    both discuss the same declared 'topic' but disagree on a 'date' /
    'period' field supplied in their metadata. This is intentionally simple
    and transparent — replace with an LLM-based claim-comparison agent for
    production use.
    """
    conflicts: list[Conflict] = []
    by_topic: dict[str, list[dict]] = {}
    for s in sources:
        topic = s.get("topic") or "unspecified"
        by_topic.setdefault(topic, []).append(s)

    for topic, group in by_topic.items():
        periods = {s.get("period") for s in group if s.get("period")}
        if len(periods) > 1:
            group_sorted = sorted(group, key=lambda s: s.get("period") or "")
            conflicts.append(
                Conflict(
                    topic=topic,
                    source_a=group_sorted[0].get("title", "Source A"),
                    source_b=group_sorted[-1].get("title", "Source B"),
                    detail=f"Disagreement on period/date for topic '{topic}': {periods}",
                )
            )
    return conflicts
