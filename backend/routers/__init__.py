"""API routers for different domains."""

from .auth import router as auth_router
from .health import router as health_router
from .session import router as session_router
from .script import router as script_router
from .thumbnail import router as thumbnail_router
from .workflow import router as workflow_router
from .face import router as face_router
from .search import router as search_router
from .audio import router as audio_router
from .image import router as image_router

__all__ = [
    "auth_router",
    "health_router",
    "session_router",
    "script_router",
    "thumbnail_router",
    "workflow_router",
    "face_router",
    "search_router",
    "audio_router",
    "image_router",
]

