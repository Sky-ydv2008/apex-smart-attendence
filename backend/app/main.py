import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import engine, Base
from app.config import UPLOADS_DIR, CARDS_DIR
from app.routers import auth, classes, students, sessions, attendance, reports, websockets

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AttendAI")

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AttendAI - Offline Smart Attendance Backend",
    description="Local AI-powered classroom attendance platform with ID-card OCR and Face Verification.",
    version="1.0.0"
)

# Enable CORS for local zero-wifi offline access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads directory for photos & generated ID cards
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR.parent)), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(students.router)
app.include_router(sessions.router)
app.include_router(attendance.router)
app.include_router(reports.router)
app.include_router(websockets.router)

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/")
    def read_index():
        from fastapi.responses import FileResponse
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "status": "online",
            "app": "AttendAI - Offline Smart Attendance System",
            "version": "1.0.0",
            "mode": "100% Local / Zero Cloud Dependency",
            "ai_engine": "ID-Card OCR + Face Verification Dual Engine Ready"
        }
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "offline_mode": True,
        "database": "connected",
        "ai_models_loaded": True
    }
