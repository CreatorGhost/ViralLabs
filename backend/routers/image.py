"""
Simple Image generation endpoints.
Takes a prompt and generates images directly without complex video analysis.
Supports optional face integration and R2 storage.

Configurable providers via IMAGE_PROVIDER env var:
- "gemini": Google Gemini 3 Pro Image
- "seedream": BytePlus Seedream 4.0/4.5
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.config import THUMBNAILS_DIR
from backend.core.database import get_db
from backend.core.dependencies import get_current_user, get_premium_user
from backend.models.db_models import User, MediaFile
from backend.services.storage_service import storage_service
from src.image_factory import ImageGeneratorFactory, get_current_provider


router = APIRouter(prefix="/image", tags=["Image Generation"])


class ImageGenerateRequest(BaseModel):
    """Request model for simple image generation."""
    prompt: str = Field(..., description="The prompt for image generation")
    num_images: int = Field(default=1, ge=1, le=5, description="Number of images to generate (1-5)")
    resolution: str = Field(default="1K", description="Resolution: 1K (1280x720)")
    include_face: bool = Field(default=False, description="Include user's uploaded face")
    face_mode: str = Field(default="auto", description="Face placement: auto, center, left, right")
    face_style: str = Field(default="realistic", description="Face style: realistic, professional, cartoon")
    provider: Optional[str] = Field(default=None, description="Override provider: gemini or seedream")

    @field_validator('resolution')
    @classmethod
    def force_1k_resolution(cls, v: str) -> str:
        """Force all image generation to 1K resolution."""
        return "1K"


class GeneratedImage(BaseModel):
    """Single generated image info."""
    success: bool
    id: Optional[str] = None
    filepath: Optional[str] = None
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    error: Optional[str] = None


class ImageGenerateResponse(BaseModel):
    """Response model for image generation."""
    success: bool
    images: List[GeneratedImage] = []
    successful_count: int = 0
    error: Optional[str] = None


@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_images(
    request: ImageGenerateRequest,
    current_user: User = Depends(get_premium_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate images from a prompt.
    
    Simple endpoint that takes a prompt and generates the specified number of images.
    Optionally includes the user's uploaded face in the generation.
    Images are stored in R2 (or local) and tracked in the database.
    
    Provider can be configured via:
    - IMAGE_PROVIDER env var (default)
    - request.provider field (override per-request)
    """
    # Determine provider
    provider = request.provider or get_current_provider()
    
    # Validate provider has required API keys
    if provider == "gemini":
        if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
            raise HTTPException(status_code=400, detail="GEMINI_API_KEY not set")
    elif provider == "seedream":
        if not os.getenv("ARK_API_KEY"):
            raise HTTPException(status_code=400, detail="ARK_API_KEY not set for Seedream")
    
    # Deduct 1 credit per API call (regardless of num_images)
    current_user.credits -= 1
    current_user.is_premium = current_user.credits > 0
    await db.flush()
    print(f"💳 Deducted 1 credit for image generation. User {current_user.email} now has {current_user.credits} credits remaining")

    try:
        # Get user's face if requested
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
                # For R2, we'd need to download - skip for now
                # TODO: Download R2 face to temp file if needed
        
        results: List[GeneratedImage] = []
        successful_count = 0
        
        # Use temp directory for generation, then upload to storage
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create generator using factory - picks Gemini or Seedream based on config
            generator = ImageGeneratorFactory.create(
                provider=provider,
                output_dir=temp_dir,
                resolution=request.resolution
            )
            
            for i in range(request.num_images):
                try:
                    # Generate unique filename
                    image_id = uuid4().hex[:12]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    clean_prompt = request.prompt.replace(' ', '_')[:20]
                    filename = f"image_{clean_prompt}_{timestamp}_v{i+1}"
                    
                    # Generate image - with or without face
                    if face_path and face_path.exists():
                        result = generator.generate_thumbnail_with_face(
                            video_title=request.prompt,
                            face_image_path=str(face_path),
                            face_mode=request.face_mode,
                            face_style=request.face_style,
                            filename=filename,
                            resolution=request.resolution
                        )
                    else:
                        result = generator.generate_thumbnail(
                            prompt=request.prompt,
                            filename=filename,
                            resolution=request.resolution
                        )
                    
                    if result.get('success') and result.get('filepath'):
                        # Upload to storage
                        generated_path = Path(result['filepath'])
                        
                        if generated_path.exists():
                            storage_key = storage_service.generate_key(
                                file_type="images",
                                user_id=str(current_user.id),
                                filename=f"{filename}_{image_id}",
                                extension="png"
                            )
                            
                            storage_info = await storage_service.upload_from_path(
                                local_path=generated_path,
                                key=storage_key,
                                content_type="image/png",
                            )
                            
                            # Create MediaFile record
                            media_file = MediaFile(
                                user_id=current_user.id,
                                file_type="image",
                                storage_type=storage_info["storage_type"],
                                storage_key=storage_info["storage_key"],
                                storage_url=storage_info["storage_url"],
                                original_filename=f"{filename}.png",
                                file_size=generated_path.stat().st_size,
                                mime_type="image/png",
                                file_metadata={
                                    "prompt": request.prompt,
                                    "resolution": request.resolution,
                                    "provider": provider,
                                    "model": generator.get_provider_info().get('model'),
                                    "width": result.get('width'),
                                    "height": result.get('height'),
                                    "include_face": request.include_face,
                                    "face_mode": request.face_mode if request.include_face else None,
                                    "face_style": request.face_style if request.include_face else None,
                                }
                            )
                            db.add(media_file)
                            await db.flush()  # Get the ID
                            
                            results.append(GeneratedImage(
                                success=True,
                                id=str(media_file.id),
                                filepath=storage_info["storage_url"],
                                url=storage_info["storage_url"],
                                width=result.get('width'),
                                height=result.get('height')
                            ))
                            successful_count += 1
                        else:
                            results.append(GeneratedImage(
                                success=False,
                                error="Generated file not found"
                            ))
                    else:
                        results.append(GeneratedImage(
                            success=False,
                            error=result.get('error', 'Unknown error')
                        ))
                        
                except Exception as e:
                    results.append(GeneratedImage(
                        success=False,
                        error=str(e)
                    ))
        
        await db.commit()
        
        return ImageGenerateResponse(
            success=successful_count > 0,
            images=results,
            successful_count=successful_count
        )
        
    except Exception as e:
        await db.rollback()
        return ImageGenerateResponse(
            success=False,
            error=str(e)
        )


@router.get("/provider")
async def get_image_provider():
    """Get the currently configured image generation provider."""
    provider = get_current_provider()
    return {
        "provider": provider,
        "available": ImageGeneratorFactory.is_provider_available(provider),
        "options": ["gemini", "seedream"]
    }


@router.get("/list")
async def list_images(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all generated images for the current user."""
    query = select(MediaFile).where(
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "image"
    ).order_by(MediaFile.created_at.desc())
    
    result = await db.execute(query)
    images = result.scalars().all()
    
    return {
        "success": True,
        "count": len(images),
        "images": [
            {
                "id": str(img.id),
                "url": img.storage_url,
                "filename": img.original_filename,
                "created_at": img.created_at.isoformat() if img.created_at else None,
                "metadata": img.file_metadata,
            }
            for img in images
        ]
    }


@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a generated image."""
    try:
        image_uuid = UUID(image_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid image ID format")
    
    query = select(MediaFile).where(
        MediaFile.id == image_uuid,
        MediaFile.user_id == current_user.id,
        MediaFile.file_type == "image"
    )
    result = await db.execute(query)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete from storage
    await storage_service.delete(image.storage_type, image.storage_key)
    
    # Delete from database
    await db.delete(image)
    await db.commit()
    
    return {"success": True, "message": "Image deleted"}
