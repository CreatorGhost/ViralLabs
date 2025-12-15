#!/usr/bin/env python3
"""
YouTube Automation Stack - FastAPI Backend
Main application entry point with clean router-based architecture.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration and routers
from backend.core.config import THUMBNAILS_DIR, FRONTEND_DIR, BASE_DIR
from backend.core.database import init_db, close_db
from backend.routers import (
    auth_router,
    health_router,
    session_router,
    script_router,
    thumbnail_router,
    face_router,
    search_router,
    audio_router,
    image_router,
    payment_router,
)
from backend.routers.script import regenerate_router


# ===== Lifespan =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 YouTube Automation API starting...")
    print("📁 Thumbnails directory:", THUMBNAILS_DIR)
    print("📁 Frontend directory:", FRONTEND_DIR)
    print("🗄️ Initializing database...")
    await init_db()
    print("✅ Database initialized")
    yield
    print("🗄️ Closing database connections...")
    await close_db()
    print("👋 YouTube Automation API shutting down...")


# ===== FastAPI App =====
app = FastAPI(
    title="YouTube Automation API",
    description="Generate YouTube scripts and thumbnails with AI",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for thumbnails (legacy)
app.mount("/thumbnails", StaticFiles(directory=str(THUMBNAILS_DIR)), name="thumbnails")

# Mount uploads directory for local storage mode
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Serve frontend static files in production
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="frontend-assets")


# ===== Register Routers =====
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(session_router)
app.include_router(script_router)
app.include_router(regenerate_router)
app.include_router(thumbnail_router)
app.include_router(face_router)
app.include_router(search_router)
app.include_router(audio_router)
app.include_router(image_router)
app.include_router(payment_router)


# ===== Frontend Serving (Production) =====
@app.get("/")
async def serve_frontend_root():
    """Serve the frontend index.html."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "YouTube Automation API", "docs": "/docs", "version": "2.0.0"}


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend static files or fallback to index.html for SPA routing."""
    # Skip API routes - these are handled by routers
    api_prefixes = (
        "auth", "generate", "regenerate", "upload", "uploads", "face",
        "session", "health", "docs", "openapi", "redoc", "search", "audio", "image", "payment"
    )
    # Special handling for thumbnail routes (but not /thumbnails static files)
    if full_path.startswith("thumbnail/") or full_path.startswith(api_prefixes):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Try to serve the static file
    file_path = FRONTEND_DIR / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # Fallback to index.html for SPA routing
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
