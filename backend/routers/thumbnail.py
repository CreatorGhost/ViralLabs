"""
Thumbnail generation endpoints.
Single Responsibility: Only handles thumbnail generation/regeneration routes.
Uses CloudFlare R2 or local storage based on configuration.
"""

import os
from datetime import datetime
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.config import THUMBNAILS_DIR
from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.db_models import User, MediaFile
from backend.services.thumbnail_service import ThumbnailService
from backend.services.storage_service import storage_service
from backend.models.schemas import (
    ThumbnailGenerateRequest,
    ThumbnailRegenerateRequest,
    ThumbnailResponse,
)

router = APIRouter(tags=["Thumbnail"])
thumbnail_service = ThumbnailService()


@router.post("/generate/thumbnails", response_model=ThumbnailResponse)
async def generate_thumbnails(
    request: ThumbnailGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate thumbnails for a video topic."""
    
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY not set")
    
    try:
        # Get face path from user's uploaded face if enabled
        face_path = None
        if request.include_face:
            # Get user's current face from database
            face_query = select(MediaFile).where(
                MediaFile.user_id == current_user.id,
                MediaFile.file_type == "face"
            ).order_by(MediaFile.created_at.desc())
            result = await db.execute(face_query)
            face_file = result.scalar_one_or_none()
            
            if face_file and face_file.storage_type == "local":
                face_path = Path(face_file.storage_key)
            # For R2 faces, we'd need to download first - skip for now
        
        # Generate with storage and DB tracking
        result = await thumbnail_service.generate_batch_with_storage(
            topic=request.topic,
            num_thumbnails=request.num_thumbnails,
            resolution=request.resolution,
            user_id=current_user.id,
            db=db,
            face_path=face_path,
            face_mode=request.face_mode,
            face_style=request.face_style,
            use_reference_images=request.use_reference_images
        )
        
        return ThumbnailResponse(
            success=result.get("success", False),
            thumbnails=result.get("thumbnails"),
            successful_count=result.get("successful_count", 0)
        )
        
    except Exception as e:
        return ThumbnailResponse(success=False, error=str(e))


@router.post("/regenerate/thumbnails", response_model=ThumbnailResponse)
async def regenerate_thumbnails(
    request: ThumbnailRegenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate thumbnails with new settings."""
    
    gen_request = ThumbnailGenerateRequest(
        topic=request.topic,
        num_thumbnails=request.num_thumbnails,
        resolution=request.resolution,
        use_reference_images=request.use_reference_images,
        include_face=request.include_face,
        face_mode=request.face_mode,
        face_style=request.face_style
    )
    
    return await generate_thumbnails(gen_request, current_user, db)


# NOTE: /thumbnail/list MUST be defined BEFORE /thumbnail/{filename}
# Otherwise {filename} will match "list" as a path parameter
@router.get("/thumbnail/list")
async def list_thumbnails(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all generated thumbnails for the current user."""
    
    query = select(MediaFile).where(
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "thumbnail"
    ).order_by(MediaFile.created_at.desc())
    
    result = await db.execute(query)
    thumbnails = result.scalars().all()
    
    thumbnail_list = []
    for t in thumbnails:
        thumbnail_list.append({
            "id": str(t.id),
            "filename": t.original_filename,
            "url": t.storage_url,
            "path": t.storage_url,
            "created": t.created_at.isoformat() if t.created_at else None,
            "metadata": t.file_metadata,
        })
    
    # Also include any legacy local thumbnails not in database
    for f in THUMBNAILS_DIR.glob("*.png"):
        # Check if already in the list
        filename = f.name
        if not any(t.get("filename") == filename for t in thumbnail_list):
            thumbnail_list.append({
                "filename": filename,
                "url": f"/thumbnails/{filename}",
                "path": f"/thumbnails/{filename}",
                "created": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "metadata": {"legacy": True}
            })
    
    return {"thumbnails": thumbnail_list}


@router.get("/thumbnail/{filename}")
async def get_thumbnail(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a generated thumbnail by filename."""
    
    # First check database
    query = select(MediaFile).where(
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "thumbnail",
        MediaFile.original_filename == filename
    )
    result = await db.execute(query)
    thumb = result.scalar_one_or_none()
    
    if thumb:
        if thumb.storage_type == "r2":
            return RedirectResponse(url=thumb.storage_url)
        return FileResponse(thumb.storage_key)
    
    # Fallback to legacy local storage
    filepath = THUMBNAILS_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    return FileResponse(filepath)


@router.get("/thumbnail/id/{thumbnail_id}")
async def get_thumbnail_by_id(
    thumbnail_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a thumbnail by its MediaFile ID."""
    
    try:
        thumb_uuid = UUID(thumbnail_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid thumbnail ID format")
    
    query = select(MediaFile).where(
        MediaFile.id == thumb_uuid,
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "thumbnail"
    )
    result = await db.execute(query)
    thumb = result.scalar_one_or_none()
    
    if not thumb:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    if thumb.storage_type == "r2":
        return RedirectResponse(url=thumb.storage_url)
    
    return FileResponse(thumb.storage_key)


@router.delete("/thumbnail/{filename}")
async def delete_thumbnail(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a thumbnail by filename."""
    
    # First check database
    query = select(MediaFile).where(
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "thumbnail",
        MediaFile.original_filename == filename
    )
    result = await db.execute(query)
    thumb = result.scalar_one_or_none()
    
    if thumb:
        await storage_service.delete(thumb.storage_type, thumb.storage_key)
        await db.delete(thumb)
        await db.commit()
        return {"success": True, "message": f"Deleted {filename}"}
    
    # Fallback to legacy local storage
    filepath = THUMBNAILS_DIR / filename
    if filepath.exists():
        filepath.unlink()
        return {"success": True, "message": f"Deleted {filename}"}
    
    raise HTTPException(status_code=404, detail="Thumbnail not found")


@router.delete("/thumbnail/id/{thumbnail_id}")
async def delete_thumbnail_by_id(
    thumbnail_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a thumbnail by its MediaFile ID."""
    
    try:
        thumb_uuid = UUID(thumbnail_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid thumbnail ID format")
    
    query = select(MediaFile).where(
        MediaFile.id == thumb_uuid,
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "thumbnail"
    )
    result = await db.execute(query)
    thumb = result.scalar_one_or_none()
    
    if not thumb:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    await storage_service.delete(thumb.storage_type, thumb.storage_key)
    await db.delete(thumb)
    await db.commit()
    
    return {"success": True, "message": "Thumbnail deleted"}
