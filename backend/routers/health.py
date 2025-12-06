"""
Health check endpoint.
Single Responsibility: Only handles health/status checks.
"""

import os
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Check API health and verify API keys are configured."""
    return {
        "status": "healthy",
        "openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "gemini_key": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
        "youtube_key": bool(os.getenv("YOUTUBE_API_KEY"))
    }


