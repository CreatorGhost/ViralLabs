"""
Script generation endpoints.
Single Responsibility: Only handles script generation/regeneration routes.
"""

import os
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.script_generator import generate_youtube_script, regenerate_script_only
from backend.core.session import session_manager
from backend.models.schemas import (
    ScriptGenerateRequest,
    ScriptRegenerateRequest,
    ScriptResponse,
)

router = APIRouter(prefix="/generate", tags=["Script"])
regenerate_router = APIRouter(prefix="/regenerate", tags=["Script"])


@router.post("/script", response_model=ScriptResponse)
async def generate_script(request: ScriptGenerateRequest, session_id: str = "default"):
    """Generate a YouTube script from a topic."""
    
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not set")
    
    try:
        result = generate_youtube_script(
            topic=request.topic,
            model=request.model,
            refine_model=request.refine_model,
            max_videos=request.max_videos,
            top_n=request.top_n_videos,
            subscriber_threshold=request.subscriber_threshold,
            max_workers=request.max_workers
        )
        
        if not result:
            return ScriptResponse(success=False, error="Script generation failed")
        
        # Store in session for regeneration
        session_manager.set_last_script(session_id, result)
        session_manager.set_research_data(session_id, {
            "original_query": result.get("original_query"),
            "refined_query": result.get("refined_query"),
            "combined_transcripts": result.get("combined_transcripts"),
            "videos_analyzed": result.get("videos_analyzed"),
            "metadata": result.get("metadata")
        })
        
        return ScriptResponse(
            success=True,
            script=result.get("script"),
            refined_query=result.get("refined_query"),
            original_query=result.get("original_query"),
            videos_analyzed=result.get("videos_analyzed"),
            stats=result.get("stats"),
            metadata=result.get("metadata"),
            combined_transcripts=result.get("combined_transcripts")
        )
        
    except Exception as e:
        return ScriptResponse(success=False, error=str(e))


@regenerate_router.post("/script", response_model=ScriptResponse)
async def regenerate_script(request: ScriptRegenerateRequest, session_id: str = "default"):
    """Regenerate script using existing transcripts."""
    
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not set")
    
    try:
        result = regenerate_script_only(
            original_query=request.original_query,
            refined_query=request.refined_query,
            combined_transcripts=request.combined_transcripts,
            video_count=request.video_count,
            model=request.model,
            temperature=request.temperature
        )
        
        if not result:
            return ScriptResponse(success=False, error="Script regeneration failed")
        
        # Update session
        session_manager.set_last_script(session_id, result)
        
        return ScriptResponse(
            success=True,
            script=result.get("script"),
            refined_query=result.get("refined_query"),
            original_query=result.get("original_query"),
            videos_analyzed=result.get("videos_analyzed"),
            stats=result.get("stats")
        )
        
    except Exception as e:
        return ScriptResponse(success=False, error=str(e))


@regenerate_router.post("/script-from-session", response_model=ScriptResponse)
async def regenerate_script_from_session(
    model: str = "gpt-5.1",
    temperature: float = 0.7,
    session_id: str = "default"
):
    """Regenerate script using session's stored transcripts."""
    
    session = session_manager.get_or_create(session_id)
    research_data = session.get("research_data")
    
    if not research_data or not research_data.get("combined_transcripts"):
        raise HTTPException(
            status_code=400, 
            detail="No previous generation found. Run full workflow first."
        )
    
    request = ScriptRegenerateRequest(
        original_query=research_data["original_query"],
        refined_query=research_data["refined_query"],
        combined_transcripts=research_data["combined_transcripts"],
        video_count=research_data["videos_analyzed"],
        model=model,
        temperature=temperature
    )
    
    return await regenerate_script(request, session_id)




