import io
from fastapi.testclient import TestClient
from PIL import Image
from app import main

def png():
    b = io.BytesIO(); Image.new("RGB", (50, 50), "green").save(b, "PNG"); return b.getvalue()

def test_health():
    with TestClient(main.app) as c:
        assert c.get("/api/health").status_code == 200

def test_predict_503_without_model():
    with TestClient(main.app) as c:
        main.state["clf"] = None
        assert c.post("/api/predict", files={"file": ("a.png", png(), "image/png")}).status_code == 503

def test_summary_has_total():
    with TestClient(main.app) as c:
        assert "total" in c.get("/api/analytics/summary").json()
