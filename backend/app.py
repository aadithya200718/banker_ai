"""
Face Verification API — FastAPI Application
=============================================
Production-grade app with MySQL, JWT auth, per-banker data isolation.
"""

import os
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base
from backend.routes.auth import router as auth_router
from backend.routes.verification import router as verification_router

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
)
logger = logging.getLogger("face_verify")


# ── Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Face Verification API ...")
    # Create all MySQL tables
    Base.metadata.create_all(bind=engine)
    logger.info("✅ MySQL tables created / verified")
    # Warm up ML models (optional — auth works without them)
    try:
        from backend.face_service import get_face_service
        get_face_service()
        from backend.variation_detector import get_variation_detector
        get_variation_detector()
        logger.info("✅ All services ready")
    except Exception as e:
        logger.warning("⚠️ ML models skipped (auth available): %s", str(e))
    yield
    logger.info("👋 Shutting down")


# ── App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Face Verification Assistant",
    description="Bank officer face verification with JWT auth & MySQL",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(verification_router)


# ── Serve Frontend (fallback for old HTML) ───────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the old HTML frontend as fallback (React runs on :5173)."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Frontend running on http://localhost:5173</h1>")


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    try:
        from backend.face_service import get_face_service
        face_svc = get_face_service()
        models_loaded = face_svc.is_ready
    except Exception:
        models_loaded = False
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "models_loaded": models_loaded,
        "version": "2.0.0",
        "database": "mysql",
    }
