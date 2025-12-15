"""
Full workflow endpoints (including streaming).
Single Responsibility: Only handles workflow orchestration routes.
"""

import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.session import session_manager
from backend.core.database import get_db
from backend.core.dependencies import get_premium_user
from backend.models.db_models import User, MediaFile
from backend.services.sse import SSEService
from backend.services.workflow_service import WorkflowStreamService
from backend.services.thumbnail_service import ThumbnailService
from backend.services.storage_service import storage_service
from backend.models.schemas import (
    ThumbnailResponse,
    FullWorkflowRequest,
    FullWorkflowResponse,
    ScriptResponse,
)
from src.script_generator import generate_youtube_script

router = APIRouter(prefix="/generate", tags=["Workflow"])

# Initialize services
workflow_service = WorkflowStreamService(session_manager)

# Temp directory for downloaded faces (persists across requests)
_workflow_face_temp_dir = tempfile.mkdtemp(prefix="workflow_faces_")


@router.post("/full-workflow", response_model=FullWorkflowResponse)
async def full_workflow(
    request: FullWorkflowRequest,
    session_id: str = "default",
    current_user: User = Depends(get_premium_user),
    db: AsyncSession = Depends(get_db),
):
    """Run full workflow: generate script + thumbnails (non-streaming). Requires credits."""

    # Deduct 1 credit for the entire workflow
    current_user.credits -= 1
    current_user.is_premium = current_user.credits > 0
    await db.flush()
    print(f"💳 Deducted 1 credit for full workflow. User {current_user.email} now has {current_user.credits} credits remaining")

    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not set")
    
    if request.enable_thumbnails:
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            raise HTTPException(status_code=400, detail="GEMINI_API_KEY not set for thumbnails")
    
    try:
        # Generate script using service function directly (doesn't deduct credits - already done above)
        script_result = generate_youtube_script(
            topic=request.topic,
            model=request.model,
            refine_model=request.refine_model,
            max_videos=request.max_videos,
            top_n=request.top_n_videos,
            subscriber_threshold=request.subscriber_threshold,
            max_workers=request.max_workers
        )
        
        if not script_result:
            return FullWorkflowResponse(success=False, error="Script generation failed")
        
        # Store in session for regeneration
        session_manager.set_last_script(session_id, script_result)
        session_manager.set_research_data(session_id, {
            "original_query": script_result.get("original_query"),
            "refined_query": script_result.get("refined_query"),
            "combined_transcripts": script_result.get("combined_transcripts"),
            "videos_analyzed": script_result.get("videos_analyzed"),
            "metadata": script_result.get("metadata")
        })
        
        # Create script response
        script_response = ScriptResponse(
            success=True,
            script=script_result.get("script"),
            refined_query=script_result.get("refined_query"),
            original_query=script_result.get("original_query"),
            videos_analyzed=script_result.get("videos_analyzed"),
            stats=script_result.get("stats"),
            metadata=script_result.get("metadata"),
            combined_transcripts=script_result.get("combined_transcripts")
        )
        
        # Generate thumbnails if enabled (call service directly, not endpoint)
        thumbnail_response = None
        if request.enable_thumbnails:
            # Get face path from user's uploaded face if enabled
            face_path = None
            if request.include_face:
                face_query = select(MediaFile).where(
                    MediaFile.user_id == current_user.id,
                    MediaFile.file_type == "face"
                ).order_by(MediaFile.created_at.desc())
                result = await db.execute(face_query)
                face_file = result.scalar_one_or_none()
                
                if face_file:
                    if face_file.storage_type == "local":
                        face_path = Path(face_file.storage_key)
                    elif face_file.storage_type == "r2":
                        # Download R2 face to temp file
                        ext = Path(face_file.original_filename or "face.png").suffix or ".png"
                        temp_face_path = Path(_workflow_face_temp_dir) / f"face_{current_user.id}{ext}"
                        
                        downloaded = await storage_service.download_to_path(
                            storage_type="r2",
                            storage_key=face_file.storage_key,
                            local_path=temp_face_path
                        )
                        
                        if downloaded:
                            face_path = temp_face_path
            
            # Call thumbnail service directly (doesn't deduct credits)
            result = await ThumbnailService().generate_batch_with_storage(
                topic=request.topic,
                num_thumbnails=request.num_thumbnails,
                resolution=request.resolution,
                user_id=current_user.id,
                db=db,
                face_path=face_path,
                face_mode=request.face_mode,
                face_style=request.face_style,
                use_reference_images=request.use_reference_images,
                youtube_video_ids=None  # Could be enhanced to use search results
            )
            
            thumbnail_response = ThumbnailResponse(
                success=result.get("success", False),
                thumbnails=result.get("thumbnails"),
                successful_count=result.get("successful_count", 0)
            )
        
        return FullWorkflowResponse(
            success=script_response.success,
            script=script_response,
            thumbnails=thumbnail_response
        )
        
    except Exception as e:
        return FullWorkflowResponse(success=False, error=str(e))


@router.post("/full-workflow/stream")
async def full_workflow_stream(
    request: FullWorkflowRequest,
    session_id: str = "default",
    current_user: User = Depends(get_premium_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Run full workflow with real-time streaming via Server-Sent Events.
    Requires premium subscription.
    
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
            async def gemini_error_stream():
                yield SSEService.error(
                    SSEService.STEP_INITIALIZING,
                    "GEMINI_API_KEY not set",
                    "GEMINI_API_KEY or GOOGLE_API_KEY required for thumbnails"
                )
            return StreamingResponse(
                gemini_error_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
    
    # Deduct 1 credit for the streaming workflow (image generation)
    if request.enable_thumbnails:
        current_user.credits -= 1
        current_user.is_premium = current_user.credits > 0
        await db.flush()
        print(f"💳 Deducted 1 credit for streaming workflow. User {current_user.email} now has {current_user.credits} credits remaining")

    # ===== REQUEST PARAMETERS LOGGING =====
    print("\n" + "=" * 70)
    print("🚀 STREAMING WORKFLOW REQUEST")
    print("=" * 70)
    print(f"📋 Topic: {request.topic}")
    print(f"🎬 Enable thumbnails: {'✅ YES' if request.enable_thumbnails else '❌ NO'}")
    print(f"👤 Include face: {'✅ YES' if request.include_face else '❌ NO'}")
    print(f"🖼️ Use reference images: {'✅ YES' if request.use_reference_images else '❌ NO'}")
    print(f"🔢 Num thumbnails: {request.num_thumbnails}")
    print(f"👤 Current user: {current_user.id}")
    print("=" * 70)
    
    # Download face from R2 if needed for thumbnail generation
    face_path = None
    if request.enable_thumbnails and request.include_face:
        face_query = select(MediaFile).where(
            MediaFile.user_id == current_user.id,
            MediaFile.file_type == "face"
        ).order_by(MediaFile.created_at.desc())
        result = await db.execute(face_query)
        face_file = result.scalar_one_or_none()
        
        if face_file:
            if face_file.storage_type == "local":
                face_path = Path(face_file.storage_key)
            elif face_file.storage_type == "r2":
                # Download R2 face to temp file
                ext = Path(face_file.original_filename or "face.png").suffix or ".png"
                temp_face_path = Path(_workflow_face_temp_dir) / f"face_{current_user.id}{ext}"
                
                print("📥 Downloading face from R2 for streaming workflow...")
                downloaded = await storage_service.download_to_path(
                    storage_type="r2",
                    storage_key=face_file.storage_key,
                    local_path=temp_face_path
                )
                
                if downloaded:
                    face_path = temp_face_path
                    print(f"✅ Face downloaded to: {temp_face_path}")
                else:
                    print("⚠️ Failed to download face from R2")
    
    return StreamingResponse(
        workflow_service.generate_stream(request, session_id, user=current_user, db=db, face_path=face_path),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )





