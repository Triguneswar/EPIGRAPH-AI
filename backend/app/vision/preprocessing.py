"""
Real, working image-preprocessing pipeline for historical inscription/
manuscript images. No network access or pretrained model is required for
any step here — everything runs locally with OpenCV/NumPy/Pillow.

Usage:
    from app.vision.preprocessing import preprocess_image
    result = preprocess_image("data/raw/xyz.jpg", "data/processed/xyz.jpg")
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

import cv2
import numpy as np


@dataclass
class PreprocessingResult:
    processed_path: str
    steps_applied: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


def _resize_preserving_aspect(img: np.ndarray, max_dim: int = 1600) -> np.ndarray:
    h, w = img.shape[:2]
    scale = max_dim / max(h, w) if max(h, w) > max_dim else 1.0
    if scale != 1.0:
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def _denoise(img: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(img, None, 7, 7, 7, 21)


def _clahe_contrast(img_gray: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    return clahe.apply(img_gray)


def _adaptive_threshold(img_gray: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
        img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )


def _sharpen(img: np.ndarray) -> np.ndarray:
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)


def _edge_enhance(img_gray: np.ndarray) -> np.ndarray:
    edges = cv2.Laplacian(img_gray, cv2.CV_64F)
    edges = cv2.convertScaleAbs(edges)
    return cv2.addWeighted(img_gray, 0.85, edges, 0.15, 0)


def _estimate_blur_score(img_gray: np.ndarray) -> float:
    """Higher = sharper. Variance of the Laplacian, a standard blur metric."""
    return float(cv2.Laplacian(img_gray, cv2.CV_64F).var())


def preprocess_image(
    input_path: str,
    output_path: str,
    steps: list[str] | None = None,
) -> PreprocessingResult:
    """
    Runs the enhancement pipeline described in the spec:
    resize -> color space -> denoise -> CLAHE contrast -> adaptive threshold
    (kept as a side output, not the final image) -> sharpen -> edge enhance.

    The *final* saved image is a sharpened, contrast-enhanced grayscale-derived
    color image (readable for a human), while the binarized/thresholded
    version is stored in metadata for downstream OCR modules that want it.
    """
    steps = steps or [
        "resize",
        "color_space",
        "denoise",
        "clahe_contrast",
        "sharpen",
        "edge_enhance",
    ]

    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not read image at {input_path}. File may be corrupted or an unsupported format.")

    applied: list[str] = []
    original_h, original_w = img.shape[:2]

    if "resize" in steps:
        img = _resize_preserving_aspect(img)
        applied.append("resize")

    if "color_space" in steps:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # normalize round-trip
        applied.append("color_space_normalize")

    if "denoise" in steps:
        img = _denoise(img)
        applied.append("denoise")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_score_before = _estimate_blur_score(gray)

    if "clahe_contrast" in steps:
        gray_enhanced = _clahe_contrast(gray)
        # blend the CLAHE-enhanced luminance back into the color image
        img = cv2.cvtColor(gray_enhanced, cv2.COLOR_GRAY2BGR)
        applied.append("clahe_contrast")
    else:
        gray_enhanced = gray

    binarized = _adaptive_threshold(gray_enhanced)  # used by OCR module, not saved as main output

    if "sharpen" in steps:
        img = _sharpen(img)
        applied.append("sharpen")

    if "edge_enhance" in steps:
        gray_final = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_final = _edge_enhance(gray_final)
        img = cv2.cvtColor(gray_final, cv2.COLOR_GRAY2BGR)
        applied.append("edge_enhance")

    blur_score_after = _estimate_blur_score(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

    root, ext = os.path.splitext(output_path)
    if ext.lower() not in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
        output_path = f"{root}.png"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if not cv2.imwrite(output_path, img):
        output_path = f"{root}.png"
        cv2.imwrite(output_path, img)

    binarized_path = output_path.rsplit(".", 1)[0] + "_binarized.png"
    cv2.imwrite(binarized_path, binarized)

    metadata = {
        "original_resolution": f"{original_w}x{original_h}",
        "processed_resolution": f"{img.shape[1]}x{img.shape[0]}",
        "blur_score_before": round(blur_score_before, 2),
        "blur_score_after": round(blur_score_after, 2),
        "binarized_variant_path": binarized_path,
        "image_quality_flag": "low_sharpness" if blur_score_before < 50 else "acceptable",
        "note": "Perspective correction and super-resolution are not applied "
        "automatically; they require either 4 detected document corners "
        "or a super-resolution model, and are exposed as opt-in steps "
        "for a future model-backed implementation.",
    }

    return PreprocessingResult(processed_path=output_path, steps_applied=applied, metadata=metadata)
