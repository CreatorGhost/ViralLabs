"""
Full workflow endpoints (including streaming).
Single Responsibility: Only handles workflow orchestration routes.
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.core.session import session_manager
from backend.services.sse import SSEService
from backend.services.workflow_service import WorkflowStreamService
from backend.services.thumbnail_service import ThumbnailService
from backend.models.schemas import (
    ScriptGenerateRequest,
    ThumbnailGenerateRequest,
    FullWorkflowRequest,
    FullWorkflowResponse,
)
from backend.routers.script import generate_script
from backend.routers.thumbnail import generate_thumbnails

router = APIRouter(prefix="/generate", tags=["Workflow"])

# Initialize services
workflow_service = WorkflowStreamService(session_manager)


@router.post("/full-workflow", response_model=FullWorkflowResponse)
async def full_workflow(request: FullWorkflowRequest, session_id: str = "default"):
    """Run full workflow: generate script + thumbnails (non-streaming)."""
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not set")
    
    if request.enable_thumbnails:
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            raise HTTPException(status_code=400, detail="GEMINI_API_KEY not set for thumbnails")
    
    try:
        # Generate script
        script_request = ScriptGenerateRequest(
            topic=request.topic,
            model=request.model,
            refine_model=request.refine_model,
            temperature=request.temperature,
            max_videos=request.max_videos,
            top_n_videos=request.top_n_videos,
            subscriber_threshold=request.subscriber_threshold,
            max_workers=request.max_workers
        )
        script_response = await generate_script(script_request, session_id)
        
        # Generate thumbnails if enabled
        thumbnail_response = None
        if request.enable_thumbnails:
            thumbnail_request = ThumbnailGenerateRequest(
                topic=request.topic,
                num_thumbnails=request.num_thumbnails,
                resolution=request.resolution,
                use_reference_images=request.use_reference_images,
                include_face=request.include_face,
                face_mode=request.face_mode,
                face_style=request.face_style
            )
            thumbnail_response = await generate_thumbnails(thumbnail_request, session_id)
        
        return FullWorkflowResponse(
            success=script_response.success,
            script=script_response,
            thumbnails=thumbnail_response
        )
        
    except Exception as e:
        return FullWorkflowResponse(success=False, error=str(e))


@router.post("/full-workflow/stream")
async def full_workflow_stream(request: FullWorkflowRequest, session_id: str = "default"):
    """
    Run full workflow with real-time streaming via Server-Sent Events.
    
    Returns a stream of SSE events for:
    - Progress updates (query refinement, video search, ranking, transcripts)
    - Script chunks (word by word as generated)
    - Thumbnail completions (as each thumbnail finishes)
    - Final completion event
    
    Event types:
    - progress: General progress updates with step info
    - script_chunk: Individual script tokens/words
    - thumbnail: Completed thumbnail with URL
    - complete: Final event with all results
    - error: Error event if something fails
    """
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        async def error_stream():
            yield SSEService.error(
                SSEService.STEP_INITIALIZING,
                "OPENAI_API_KEY not set",
                "OPENAI_API_KEY environment variable is required"
            )
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    if request.enable_thumbnails:
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            async def error_stream():
                yield SSEService.error(
                    SSEService.STEP_INITIALIZING,
                    "GEMINI_API_KEY not set",
                    "GEMINI_API_KEY or GOOGLE_API_KEY required for thumbnails"
                )
            return StreamingResponse(
                error_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
    
    return StreamingResponse(
        workflow_service.generate_stream(request, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


