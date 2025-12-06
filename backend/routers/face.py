"""
Face upload endpoints.
Single Responsibility: Only handles face image upload/management.
Uses CloudFlare R2 or local storage based on configuration.
"""

import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.core.config import FACE_DIR
from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.db_models import User, MediaFile, UserState
from backend.models.schemas import FaceUploadResponse
from backend.services.storage_service import storage_service

router = APIRouter(tags=["Face"])


@router.post("/upload/face", response_model=FaceUploadResponse)
async def upload_face(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a face image for thumbnail generation."""
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    try:
        # Generate unique face ID
        face_id = str(uuid.uuid4())
        
        # Determine file extension
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "png"
        filename = f"face_{face_id}"
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Generate storage key
        storage_key = storage_service.generate_key(
            file_type="faces",
            user_id=str(current_user.id),
            filename=filename,
            extension=file_ext
        )
        
        # Upload to storage (local or R2)
        storage_info = await storage_service.upload(
            file_data=content,
            key=storage_key,
            content_type=file.content_type,
        )
        
        # Delete old face if exists (both from storage and DB)
        old_face_query = select(MediaFile).where(
            MediaFile.user_id == current_user.id,
            MediaFile.file_type == "face"
        )
        result = await db.execute(old_face_query)
        old_faces = result.scalars().all()
        
        for old_face in old_faces:
            await storage_service.delete(old_face.storage_type, old_face.storage_key)
            await db.delete(old_face)
        
        # Create MediaFile record
        media_file = MediaFile(
            user_id=current_user.id,
            file_type="face",
            storage_type=storage_info["storage_type"],
            storage_key=storage_info["storage_key"],
            storage_url=storage_info["storage_url"],
            original_filename=file.filename,
            file_size=file_size,
            mime_type=file.content_type,
            file_metadata={"face_id": face_id}
        )
        db.add(media_file)
        
        # Update or create UserState with current face
        user_state_query = select(UserState).where(UserState.user_id == current_user.id)
        result = await db.execute(user_state_query)
        user_state = result.scalar_one_or_none()
        
        if user_state:
            user_state.current_face_id = media_file.id
        else:
            user_state = UserState(
                user_id=current_user.id,
                current_face_id=media_file.id
            )
            db.add(user_state)
        
        await db.commit()
        await db.refresh(media_file)
        
        return FaceUploadResponse(
            success=True,
            face_id=face_id,
            filepath=storage_info["storage_url"]
        )
        
    except Exception as e:
        await db.rollback()
        return FaceUploadResponse(success=False, error=str(e))


@router.delete("/upload/face")
async def delete_face(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete the uploaded face image."""
    
    # Find user's face files
    query = select(MediaFile).where(
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "face"
    )
    result = await db.execute(query)
    faces = result.scalars().all()
    
    for face in faces:
        await storage_service.delete(face.storage_type, face.storage_key)
        await db.delete(face)
    
    # Clear current_face_id in UserState
    user_state_query = select(UserState).where(UserState.user_id == current_user.id)
    result = await db.execute(user_state_query)
    user_state = result.scalar_one_or_none()
    
    if user_state:
        user_state.current_face_id = None
    
    await db.commit()
    
    return {"success": True, "message": "Face deleted"}


@router.get("/face/me")
async def get_my_face(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's face image."""
    
    query = select(MediaFile).where(
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "face"
    ).order_by(MediaFile.created_at.desc())
    
    result = await db.execute(query)
    face = result.scalar_one_or_none()
    
    if not face:
        raise HTTPException(status_code=404, detail="No face uploaded")
    
    # For R2, redirect to the public URL
    if face.storage_type == "r2":
        return RedirectResponse(url=face.storage_url)
    
    # For local, serve the file
    return FileResponse(face.storage_key)


@router.get("/face/{face_id}")
async def get_face_by_id(
    face_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific face image by ID (must belong to current user)."""
    
    try:
        face_uuid = uuid.UUID(face_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid face ID format")
    
    query = select(MediaFile).where(
        MediaFile.id == face_uuid,
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "face"
    )
    
    result = await db.execute(query)
    face = result.scalar_one_or_none()
    
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    
    # For R2, redirect to the public URL
    if face.storage_type == "r2":
        return RedirectResponse(url=face.storage_url)
    
    # For local, serve the file
    return FileResponse(face.storage_key)
