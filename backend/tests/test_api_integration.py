import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def create_test_image_bytes(format="PNG"):
    img = Image.new("RGB", (200, 100), color=(200, 150, 100))
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf.getvalue()


def test_health_and_root():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"

    root_resp = client.get("/")
    assert root_resp.status_code == 200
    assert "EPIGRAPH-AI" in root_resp.json()["app"]


def test_auth_and_full_pipeline():
    # 1. Register
    email = "integration_test@example.com"
    password = "SecurePassword123!"
    reg_resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": "Test Runner"},
    )
    assert reg_resp.status_code in [201, 409]

    # 2. Login
    login_resp = client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. /auth/me
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == email

    # 4. Upload invalid file
    bad_upload = client.post(
        "/api/analyses",
        headers=headers,
        files={"file": ("test.txt", b"plain text", "text/plain")},
    )
    assert bad_upload.status_code == 415

    # 5. Upload valid PNG image
    img_bytes = create_test_image_bytes("PNG")
    upload_resp = client.post(
        "/api/analyses",
        headers=headers,
        files={"file": ("test_inscription.png", img_bytes, "image/png")},
    )
    assert upload_resp.status_code == 201
    analysis_id = upload_resp.json()["id"]

    # 6. List analyses
    list_resp = client.get("/api/analyses", headers=headers)
    assert list_resp.status_code == 200
    assert any(a["id"] == analysis_id for a in list_resp.json())

    # 7. Preprocess
    prep_resp = client.post(f"/api/analyses/{analysis_id}/preprocess", headers=headers)
    assert prep_resp.status_code == 200
    assert "steps_applied" in prep_resp.json()

    # 8. Script detection
    script_resp = client.post(f"/api/analyses/{analysis_id}/script", headers=headers)
    assert script_resp.status_code == 200
    assert "script" in script_resp.json()

    # 9. OCR
    ocr_resp = client.post(f"/api/analyses/{analysis_id}/ocr", headers=headers)
    assert ocr_resp.status_code == 200
    assert "text" in ocr_resp.json()

    # 10. Reconstruction
    rec_resp = client.post(f"/api/analyses/{analysis_id}/reconstruct", headers=headers)
    assert rec_resp.status_code == 200
    assert "observed_text" in rec_resp.json()

    # 11. Get analysis details
    get_resp = client.get(f"/api/analyses/{analysis_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "TRANSLATION"

    # 12. Delete analysis
    del_resp = client.delete(f"/api/analyses/{analysis_id}", headers=headers)
    assert del_resp.status_code == 204

    # 13. Confirm deleted
    assert client.get(f"/api/analyses/{analysis_id}", headers=headers).status_code == 404

