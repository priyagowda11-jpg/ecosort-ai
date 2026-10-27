import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import main
from app.main import Scan

def test_categories_fixed_order():
    with TestClient(main.app) as c:
        assert [x["id"] for x in c.get("/api/categories").json()] == ["wet", "dry", "plastic", "metal", "reusable", "non_recyclable"]

def test_analytics_counts_and_filters():
    with TestClient(main.app) as c:
        with Session(main.engine) as s:
            for cat, day in [("plastic", 1), ("plastic", 2), ("dry", 2)]:
                s.add(Scan(id=str(uuid.uuid4()), created_at=datetime(2026, 1, day), category=cat, confidence=.9, model_version="t"))
            s.commit()
        assert c.get("/api/analytics/summary").json() == {"total": 3, "by_category": {"plastic": 2, "dry": 1}}
        assert c.get("/api/analytics/summary?category=glass").json()["total"] == 2
        assert c.get("/api/analytics/summary?start=2026-01-02").json()["total"] == 2
        assert c.get("/api/analytics/summary?start=bad").status_code == 400
        assert [r["count"] for r in c.get("/api/analytics/timeline").json()] == [1, 2]
        assert len(c.get("/api/history?category=paper").json()) == 1

from app.classifier import decide
def test_decide_rules():
    base = dict(wet=0.02, dry=0.05, plastic=0.05, metal=0.02, reusable=0.05, non_recyclable=0.02)
    assert decide({**base, "plastic": 0.6}) == "plastic"
    assert decide({**base, "reusable": 0.4, "plastic": 0.35}) == "plastic"      # bottle is plastic, not reusable
    assert decide({**base, "reusable": 0.6}) == "reusable"
    assert decide({**base, "dry": 0.4, "non_recyclable": 0.35}) == "non_recyclable"
    assert decide(dict.fromkeys(base, 1 / 6)) is None                            # unclear -> no guess
