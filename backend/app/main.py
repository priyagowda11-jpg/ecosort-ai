from fastapi.middleware.cors import CORSMiddleware
import io, logging, os, threading, uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
from sqlalchemy import DateTime, Float, Index, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from .classifier import CATEGORY_IDS, decide

log = logging.getLogger("ecosort")
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./ecosort.db")
MAX_BYTES = int(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024
ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")


class Base(DeclarativeBase):
    pass


class Scan(Base):  # schema unchanged so the existing local database keeps working
    __tablename__ = "scans"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    category: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(40))
    __table_args__ = (Index("ix_scans_category_time", "category", "created_at"),)


engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
state: dict = {"clf": None, "status": "loading", "error": None, "version": None}


def _load():
    try:
        from .classifier import load_classifier

        c = load_classifier()
        state.update(clf=c, version=c.version, status="ready")
    except Exception as e:
        log.exception("model load failed")
        state.update(
            status="error",
            error="Could not load or download the model. Check the internet connection (first run only) and restart.",
        )


@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    if os.getenv("ECOSORT_SKIP_MODEL") == "1":
        state["status"] = "error"
    else:
        threading.Thread(target=_load, daemon=True).start()  # server starts immediately
    yield


app = FastAPI(title="EcoSort AI", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ecosort-ai-lime.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Prediction(BaseModel):
    scan_id: str
    category: str
    model_version: str


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_ready": state["clf"] is not None,
        "model_status": state["status"],
        "model_version": state["version"],
    }


CATEGORIES = [
    (
        "wet",
        "Food scraps, vegetable peels, fruit waste and other biodegradable kitchen waste.",
    ),
    ("dry", "Clean paper, cardboard, packaging and other dry household waste."),
    ("plastic", "Plastic bottles, bags, wrappers and plastic containers."),
    ("metal", "Aluminium cans, steel cans and other metal objects."),
    (
        "reusable",
        "Usable items such as intact containers, clothes and household objects.",
    ),
    (
        "non_recyclable",
        "Contaminated packaging, sanitary waste and items that ordinary household recycling cannot take.",
    ),
]


@app.get("/api/categories")
def categories():
    return [{"id": i, "description": d} for i, d in CATEGORIES]


@app.post("/api/predict", response_model=Prediction)
async def predict(file: UploadFile = File(...)):
    clf = state["clf"]
    if clf is None:
        raise HTTPException(
            503,
            state["error"] or "The AI model is still loading. Please wait a moment.",
        )
    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Image too large.")
    try:
        img = Image.open(io.BytesIO(data))
        if img.format not in {"JPEG", "PNG", "WEBP"}:
            raise HTTPException(415, "Use JPG, PNG or WEBP.")
        img = img.convert("RGB")
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(400, "Could not read this image.")
    try:
        scores = await run_in_threadpool(clf.scores, img)
    except Exception:
        log.exception("inference failed")
        raise HTTPException(500, "Prediction failed.")
    cat = decide(scores)
    if cat is None:
        raise HTTPException(422, "Could not identify the item clearly.")
    sid = str(uuid.uuid4())
    with Session(engine) as s:
        s.add(
            Scan(
                id=sid,
                created_at=datetime.now(timezone.utc),
                category=cat,
                confidence=scores[cat],
                model_version=state["version"],
            )
        )
        s.commit()
    return Prediction(scan_id=sid, category=cat, model_version=state["version"])


def _day(v, end=False):
    if not v:
        return None
    try:
        d = datetime.strptime(v, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Dates must be YYYY-MM-DD.")
    return d + timedelta(days=1) if end else d


def _where(
    start, end, category
):  # rows saved under the old six classes stay in the DB but are hidden
    c = [Scan.category.in_(CATEGORY_IDS)]
    if st := _day(start):
        c.append(Scan.created_at >= st)
    if en := _day(end, True):
        c.append(Scan.created_at < en)
    if category:
        c.append(Scan.category == category)
    return c


@app.get("/api/analytics/summary")
def summary(
    start: Optional[str] = None,
    end: Optional[str] = None,
    category: Optional[str] = None,
):
    q = (
        select(Scan.category, func.count())
        .where(*_where(start, end, category))
        .group_by(Scan.category)
    )
    with Session(engine) as s:
        rows = s.execute(q).all()
    return {"total": sum(n for _, n in rows), "by_category": {c: n for c, n in rows}}


@app.get("/api/analytics/timeline")
def timeline(
    start: Optional[str] = None,
    end: Optional[str] = None,
    category: Optional[str] = None,
):
    day = func.date(Scan.created_at)
    q = (
        select(day, func.count())
        .where(*_where(start, end, category))
        .group_by(day)
        .order_by(day)
    )
    with Session(engine) as s:
        return [{"date": d, "count": n} for d, n in s.execute(q)]


@app.get("/api/history")
def history(
    limit: int = Query(20, le=100),
    offset: int = 0,
    category: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    q = (
        select(Scan)
        .where(*_where(start, end, category))
        .order_by(Scan.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    with Session(engine) as s:
        return [
            {
                "id": r.id,
                "created_at": r.created_at,
                "category": r.category,
                "model_version": r.model_version,
            }
            for r in s.scalars(q)
        ]
