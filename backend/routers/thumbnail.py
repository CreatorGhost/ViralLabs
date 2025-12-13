"""
Thumbnail generation endpoints.
Single Responsibility: Only handles thumbnail generation/regeneration routes.
Uses CloudFlare R2 or local storage based on configuration.

Supports configurable providers via IMAGE_PROVIDER env var:
- "gemini": Google Gemini 3 Pro Image
- "seedream": BytePlus Seedream 4.0/4.5
"""

import os
import tempfile
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
from src.image_factory import get_current_provider

router = APIRouter(tags=["Thumbnail"])
thumbnail_service = ThumbnailService()

# Temp directory for downloaded faces (persists across requests)
_face_temp_dir = tempfile.mkdtemp(prefix="faces_")


@router.post("/generate/thumbnails", response_model=ThumbnailResponse)
async def generate_thumbnails(
    request: ThumbnailGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate thumbnails for a video topic."""
    
    # Check API key based on configured provider
    provider = get_current_provider()
    if provider == "gemini":
        if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
            raise HTTPException(status_code=400, detail="GEMINI_API_KEY not set")
    elif provider == "seedream":
        if not os.getenv("ARK_API_KEY"):
            raise HTTPException(status_code=400, detail="ARK_API_KEY not set for Seedream")
    
    try:
        # ===== REQUEST PARAMETERS LOGGING =====
        print("\n" + "=" * 70)
        print("🎬 THUMBNAIL GENERATION REQUEST")
        print("=" * 70)
        print(f"📋 Topic: {request.topic}")
        print(f"🔢 Number of thumbnails: {request.num_thumbnails}")
        print(f"📐 Resolution: {request.resolution}")
        print(f"👤 Include face: {'✅ YES' if request.include_face else '❌ NO'}")
        print(f"🖼️ Use reference images: {'✅ YES' if request.use_reference_images else '❌ NO'}")
        if request.youtube_video_ids:
            print(f"📺 YouTube video IDs: {len(request.youtube_video_ids)} provided")
        print("=" * 70)
        
        # Get face path from user's uploaded face if enabled
        face_path = None
        if request.include_face:
            print(f"\n👤 Looking for user's face in database...")
            # Get user's current face from database
            face_query = select(MediaFile).where(
                MediaFile.user_id == current_user.id,
                MediaFile.file_type == "face"
            ).order_by(MediaFile.created_at.desc())
            result = await db.execute(face_query)
            face_file = result.scalar_one_or_none()
            
            if face_file:
                print(f"   ✅ Face found in database!")
                print(f"   📁 Storage type: {face_file.storage_type}")
                print(f"   🔑 Storage key: {face_file.storage_key}")
                
                if face_file.storage_type == "local":
                    face_path = Path(face_file.storage_key)
                    print(f"   📍 Using local path: {face_path}")
                elif face_file.storage_type == "r2":
                    # Download R2 face to temp file
                    ext = Path(face_file.original_filename or "face.png").suffix or ".png"
                    temp_face_path = Path(_face_temp_dir) / f"face_{current_user.id}{ext}"
                    
                    print(f"   📥 Downloading face from R2...")
                    downloaded = await storage_service.download_to_path(
                        storage_type="r2",
                        storage_key=face_file.storage_key,
                        local_path=temp_face_path
                    )
                    
                    if downloaded:
                        face_path = temp_face_path
                        print(f"   ✅ Face downloaded to: {temp_face_path}")
                    else:
                        print(f"   ❌ Failed to download face from R2!")
            else:
                print(f"   ⚠️ No face found in database for user {current_user.id}")
        
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
            use_reference_images=request.use_reference_images,
            youtube_video_ids=request.youtube_video_ids
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
        youtube_video_ids=request.youtube_video_ids,
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
    
    if not thumb:
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    if thumb.storage_type == "r2":
        return RedirectResponse(url=thumb.storage_url)

    return FileResponse(thumb.storage_key)


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
    
    if not thumb:
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    await storage_service.delete(thumb.storage_type, thumb.storage_key)
    await db.delete(thumb)
    await db.commit()
    return {"success": True, "message": f"Deleted {filename}"}


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
