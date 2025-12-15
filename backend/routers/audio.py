"""
Audio generation endpoints.
Single Responsibility: Only handles audio generation routes.
Uses CloudFlare R2 or local storage based on configuration.
"""

import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.audio_genreator import (
    generate_audio,
    get_available_voices,
    get_available_personas,
)
from backend.core.config import AUDIO_DIR
from backend.core.database import get_db
from backend.core.dependencies import get_current_user, get_premium_user
from backend.models.db_models import User, MediaFile
from backend.models.schemas import (
    AudioGenerateRequest,
    AudioResponse,
    AudioOptionsResponse,
    PersonaInfo,
)
from backend.services.storage_service import storage_service

router = APIRouter(prefix="/audio", tags=["Audio"])


@router.get("/options", response_model=AudioOptionsResponse)
async def get_audio_options():
    """Get available voices and persona presets for audio generation."""
    personas_data = get_available_personas()
    personas = [PersonaInfo(**p) for p in personas_data]
    return AudioOptionsResponse(
        voices=get_available_voices(),
        personas=personas,
    )


@router.post("/generate", response_model=AudioResponse)
async def generate_audio_endpoint(
    request: AudioGenerateRequest,
    current_user: User = Depends(get_premium_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate audio from provided script text."""
    
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not set")
    
    if not request.script.strip():
        raise HTTPException(status_code=400, detail="Script cannot be empty")

    try:
        # Generate unique filename
        audio_id = uuid4().hex[:12]
        filename = request.filename or f"audio_{audio_id}"
        
        # Use a temp directory for initial generation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Generate audio to temp directory
            result = generate_audio(
                script=request.script,
                output_dir=temp_path,
                voice=request.voice,
                persona=request.persona,
                custom_instructions=request.custom_instructions,
                filename=filename,
            )
            
            if not result.get("success"):
                return AudioResponse(
                    success=False, 
                    error=result.get("error", "Audio generation failed")
                )
            
            # Get the generated file path
            generated_path = Path(result.get("filepath"))
            
            if not generated_path.exists():
                return AudioResponse(
                    success=False,
                    error="Generated audio file not found"
                )
            
            # Deduct 1 credit only after successful generation
            current_user.credits -= 1
            current_user.is_premium = current_user.credits > 0
            await db.flush()
            print(f"💳 Deducted 1 credit for audio generation. User {current_user.email} now has {current_user.credits} credits remaining")
            
            # Generate storage key
            storage_key = storage_service.generate_key(
                file_type="audio",
                user_id=str(current_user.id),
                filename=filename,
                extension="mp3"
            )
            
            # Upload to storage (local or R2)
            storage_info = await storage_service.upload_from_path(
                local_path=generated_path,
                key=storage_key,
                content_type="audio/mpeg",
            )
            
            # Get file size
            file_size = generated_path.stat().st_size
        
        # Create MediaFile record
        media_file = MediaFile(
            user_id=current_user.id,
            file_type="audio",
            storage_type=storage_info["storage_type"],
            storage_key=storage_info["storage_key"],
            storage_url=storage_info["storage_url"],
            original_filename=f"{filename}.mp3",
            file_size=file_size,
            mime_type="audio/mpeg",
            file_metadata={
                "voice": result.get("voice"),
                "persona": result.get("persona"),
                "persona_name": result.get("persona_name"),
                "model": result.get("model"),
                "script_length": result.get("script_length"),
                "chunks_processed": result.get("chunks_processed"),
            }
        )
        db.add(media_file)
        await db.commit()
        await db.refresh(media_file)
        
        return AudioResponse(
            success=True,
            filepath=storage_info["storage_url"],
            filename=f"{filename}.mp3",
            audio_url=storage_info["storage_url"],
            voice=result.get("voice"),
            persona=result.get("persona"),
            persona_name=result.get("persona_name"),
            model=result.get("model"),
            script_length=result.get("script_length"),
            chunks_processed=result.get("chunks_processed"),
        )
        
    except Exception as e:
        await db.rollback()
        return AudioResponse(success=False, error=str(e))


@router.get("/files/{filename}")
async def serve_audio_file(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Serve a generated audio file by filename."""
    
    # Find the file in database
    query = select(MediaFile).where(
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "audio",
        MediaFile.original_filename == filename
    )
    result = await db.execute(query)
    audio_file = result.scalar_one_or_none()
    
    if not audio_file:
        # Fallback to local AUDIO_DIR for backward compatibility
        file_path = AUDIO_DIR / filename
        if file_path.exists():
            return FileResponse(
                path=str(file_path),
                media_type="audio/mpeg",
                filename=filename,
            )
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # For R2, redirect to the public URL
    if audio_file.storage_type == "r2":
        return RedirectResponse(url=audio_file.storage_url)
    
    # For local, serve the file
    return FileResponse(
        path=audio_file.storage_key,
        media_type="audio/mpeg",
        filename=filename,
    )


@router.get("/file/{file_id}")
async def serve_audio_by_id(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Serve a generated audio file by MediaFile ID."""
    
    from uuid import UUID
    
    try:
        file_uuid = UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    query = select(MediaFile).where(
        MediaFile.id == file_uuid,
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "audio"
    )
    result = await db.execute(query)
    audio_file = result.scalar_one_or_none()
    
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # For R2, redirect to the public URL
    if audio_file.storage_type == "r2":
        return RedirectResponse(url=audio_file.storage_url)
    
    # For local, serve the file
    return FileResponse(
        path=audio_file.storage_key,
        media_type="audio/mpeg",
        filename=audio_file.original_filename,
    )


@router.get("/list")
async def list_audio_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all generated audio files for the current user."""
    try:
        query = select(MediaFile).where(
            MediaFile.user_id == current_user.id,
            MediaFile.file_type == "audio"
        ).order_by(MediaFile.created_at.desc())
        
        result = await db.execute(query)
        audio_files = result.scalars().all()
        
        files_list = []
        for f in audio_files:
            files_list.append({
                "id": str(f.id),
                "filename": f.original_filename,
                "url": f.storage_url,
                "size_bytes": f.file_size,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "metadata": f.file_metadata,
            })
        
        return {
            "success": True,
            "count": len(files_list),
            "files": files_list,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@router.delete("/files/{filename}")
async def delete_audio_file(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a generated audio file."""
    
    # Find the file in database
    query = select(MediaFile).where(
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "audio",
        MediaFile.original_filename == filename
    )
    result = await db.execute(query)
    audio_file = result.scalar_one_or_none()
    
    if not audio_file:
        # Fallback to local AUDIO_DIR for backward compatibility
        file_path = AUDIO_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return {"success": True, "message": f"Deleted {filename}"}
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Delete from storage
    await storage_service.delete(audio_file.storage_type, audio_file.storage_key)
    
    # Delete from database
    await db.delete(audio_file)
    await db.commit()
    
    return {"success": True, "message": f"Deleted {filename}"}


@router.delete("/file/{file_id}")
async def delete_audio_by_id(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a generated audio file by MediaFile ID."""
    
    from uuid import UUID
    
    try:
        file_uuid = UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    query = select(MediaFile).where(
        MediaFile.id == file_uuid,
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "audio"
    )
    result = await db.execute(query)
    audio_file = result.scalar_one_or_none()
    
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Delete from storage
    await storage_service.delete(audio_file.storage_type, audio_file.storage_key)
    
    # Delete from database
    await db.delete(audio_file)
    await db.commit()
    
    return {"success": True, "message": "Audio file deleted"}
