"""
Generates the final PDF report using reportlab. Real, working code — only
needs `reportlab` installed, no network or model access required.
"""
from __future__ import annotations

import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DISCLAIMER = (
    "AI-assisted analysis. Historical interpretations and reconstructed text "
    "require verification by a qualified expert. Confidence values are model "
    "scores, not calibrated statistical probabilities unless stated otherwise."
)


def generate_report(analysis_id: str, data: dict, output_path: str) -> str:
    """
    `data` is expected to contain keys: original_image_path, enhanced_image_path,
    script, ocr, reconstruction, translation, historical_context, entities,
    sources, verification.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=18)
    h2 = styles["Heading2"]
    body = styles["BodyText"]

    story = []
    story.append(Paragraph("EPIGRAPH-AI — Inscription Analysis Report", title_style))
    story.append(Paragraph(f"Analysis ID: {analysis_id}", body))
    story.append(Spacer(1, 12))

    for img_key, label in [("original_image_path", "Original Image"), ("enhanced_image_path", "Enhanced Image")]:
        path = data.get(img_key)
        if path and os.path.exists(path):
            story.append(Paragraph(label, h2))
            story.append(Image(path, width=10 * cm, height=7 * cm, kind="proportional"))
            story.append(Spacer(1, 10))

    def section(title: str, content: str):
        story.append(Paragraph(title, h2))
        story.append(Paragraph(content or "N/A", body))
        story.append(Spacer(1, 8))

    script = data.get("script") or {}
    section(
        "Script Identification",
        f"Detected: {script.get('script', 'N/A')} (confidence: {script.get('confidence', 'N/A')}) "
        f"— provider: {script.get('provider', 'N/A')}",
    )

    ocr = data.get("ocr") or {}
    section("OCR Transcription (Observed Text)", ocr.get("text", "N/A"))

    recon = data.get("reconstruction") or {}
    candidates_text = "; ".join(
        f"{c.get('text')} ({c.get('confidence')})" for c in recon.get("candidates", [])
    ) or "No reconstruction candidates."
    section("AI-Assisted Reconstruction", candidates_text)

    translation = data.get("translation") or {}
    section(
        "Translation",
        f"Modern Tamil: {translation.get('modern_tamil', 'N/A')}\nEnglish: {translation.get('english', 'N/A')}",
    )

    section("Historical Context", data.get("historical_context", "No supporting historical source found."))

    entities = data.get("entities") or []
    section(
        "Extracted Entities",
        ", ".join(f"{e.get('name')} ({e.get('type')})" for e in entities) or "None extracted.",
    )

    sources = data.get("sources") or []
    if sources:
        table_data = [["Title", "Author", "Year", "Relevance"]]
        for s in sources:
            table_data.append([s.get("title", ""), s.get("author", ""), s.get("year", ""), str(s.get("relevance_score", ""))])
        t = Table(table_data, hAlign="LEFT")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(Paragraph("Sources / Evidence", h2))
        story.append(t)
        story.append(Spacer(1, 8))
    else:
        section("Sources / Evidence", "No supporting historical source found.")

    verification = data.get("verification") or {}
    section(
        "Verification Status",
        f"Overall confidence: {verification.get('overall_confidence', 'N/A')} | "
        f"Requires human review: {verification.get('requires_human_review', 'N/A')} | "
        f"Conflicts detected: {len(verification.get('conflicts', []))}",
    )

    section("Limitations", "OCR may contain errors. Historical scripts may be ambiguous. "
            "Reconstruction is probabilistic. Translation can be uncertain. Historical "
            "sources can disagree. AI-generated interpretations require expert validation.")

    story.append(Spacer(1, 16))
    story.append(Paragraph(DISCLAIMER, ParagraphStyle("Disclaimer", parent=body, textColor=colors.red)))

    doc.build(story)
    return output_path
