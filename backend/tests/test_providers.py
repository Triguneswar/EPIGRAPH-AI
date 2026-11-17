from app.ai.script_classifier import DemoScriptClassifier, SUPPORTED_SCRIPTS
from app.reconstruction.providers import DemoReconstructionProvider
from app.ocr.providers import DemoOCRProvider


def test_demo_script_classifier_returns_valid_script(tmp_path):
    import cv2
    import numpy as np

    path = tmp_path / "img.jpg"
    cv2.imwrite(str(path), np.full((100, 100, 3), 128, dtype=np.uint8))

    result = DemoScriptClassifier().classify(str(path))
    assert result.script in SUPPORTED_SCRIPTS
    assert 0.0 <= result.confidence <= 1.0
    assert "demo" in result.provider.lower()


def test_demo_ocr_provider_labels_output_as_demo(tmp_path):
    import cv2
    import numpy as np

    path = tmp_path / "img.jpg"
    cv2.imwrite(str(path), np.full((100, 100, 3), 128, dtype=np.uint8))

    result = DemoOCRProvider().extract_text(str(path))
    assert result.confidence == 0.0
    assert "demo" in result.provider.lower()


def test_reconstruction_skips_clean_text():
    result = DemoReconstructionProvider().reconstruct("no uncertain spans here")
    assert result.candidates == []
    assert result.requires_expert_verification is False


def test_reconstruction_flags_uncertain_spans():
    result = DemoReconstructionProvider().reconstruct("ராஜ[?]ராஜன்")
    assert len(result.candidates) == 1
    assert result.requires_expert_verification is True
