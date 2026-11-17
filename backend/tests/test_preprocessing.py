import os

import cv2
import numpy as np
import pytest

from app.vision.preprocessing import preprocess_image


@pytest.fixture
def sample_image(tmp_path):
    path = tmp_path / "sample.jpg"
    img = np.full((300, 400, 3), 200, dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (350, 250), (30, 30, 30), 4)
    cv2.imwrite(str(path), img)
    return str(path)


def test_preprocess_creates_output_files(sample_image, tmp_path):
    out_path = str(tmp_path / "processed.jpg")
    result = preprocess_image(sample_image, out_path)

    assert os.path.exists(result.processed_path)
    assert os.path.exists(result.metadata["binarized_variant_path"])
    assert "resize" in result.steps_applied
    assert "clahe_contrast" in result.steps_applied


def test_preprocess_rejects_invalid_image(tmp_path):
    bad_path = tmp_path / "not_an_image.txt"
    bad_path.write_text("this is not an image")

    with pytest.raises(ValueError):
        preprocess_image(str(bad_path), str(tmp_path / "out.jpg"))
