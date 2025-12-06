"""
Thumbnail generation service.
Single Responsibility: Only handles thumbnail generation logic.
Open/Closed: Can extend generation strategies without modifying core logic.
Uses CloudFlare R2 or local storage based on configuration.
"""

import sys
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator
from uuid import UUID, uuid4
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.thumbnail_generator import ThumbnailGenerator
from backend.services.sse import SSEService
from backend.services.storage_service import storage_service
from backend.models.db_models import MediaFile


class ThumbnailService:
    """Service for generating thumbnails with cloud storage support."""
    
    def __init__(
        self,
        model: str = "gemini-3-pro-image-preview",
        aspect_ratio: str = "16:9"
    ):
        self.model = model
        self.aspect_ratio = aspect_ratio
    
    def _create_generator(self, resolution: str, output_dir: str) -> ThumbnailGenerator:
        """Create a new ThumbnailGenerator instance."""
        return ThumbnailGenerator(
            model=self.model,
            output_dir=output_dir,
            aspect_ratio=self.aspect_ratio,
            resolution=resolution
        )
    
    def _generate_filename(self, topic: str, index: int) -> str:
        """Generate a unique filename for a thumbnail."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_topic = topic.replace(' ', '_')[:30]
        return f"thumbnail_{clean_topic}_{timestamp}_v{index+1}"
    
    def _build_prompt(self, topic: str) -> str:
        """Build the prompt for thumbnail generation."""
        return f"""Create a highly engaging, professional YouTube thumbnail for this video:

VIDEO TITLE: "{topic}"

Requirements:
- Bold, attention-grabbing design
- Clear visual hierarchy
- High contrast colors
- Professional quality
- Would make viewers stop scrolling and click
"""
    
    def generate_single(
        self,
        topic: str,
        index: int,
        resolution: str,
        output_dir: str,
        face_path: Optional[Path] = None,
        face_mode: str = "auto",
        face_style: str = "realistic",
        use_reference_images: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a single thumbnail synchronously to a temp directory.
        
        Args:
            topic: Video topic/title
            index: Thumbnail index (0-based)
            resolution: Resolution (1K, 2K, 4K)
            output_dir: Directory to save generated thumbnail
            face_path: Path to face image (optional)
            face_mode: Face placement mode
            face_style: Face rendering style
            use_reference_images: Whether to use reference images
            
        Returns:
            Dict with generation result
        """
        generator = self._create_generator(resolution, output_dir)
        filename = self._generate_filename(topic, index)
        
        if face_path and face_path.exists():
            result = generator.generate_thumbnail_with_face(
                video_title=topic,
                face_image_path=str(face_path),
                face_mode=face_mode,
                face_style=face_style,
                filename=filename,
                resolution=resolution
            )
        elif use_reference_images:
            thumbnail_dir = Path("thumbnails")
            reference_images = []
            if thumbnail_dir.exists():
                reference_images = [str(img) for img in thumbnail_dir.glob("*.jpg")][:5]
            
            if reference_images:
                result = generator.generate_thumbnail_with_reference(
                    reference_images=reference_images,
                    video_title=topic,
                    filename=filename,
                    resolution=resolution
                )
            else:
                prompt = self._build_prompt(topic)
                result = generator.generate_thumbnail(prompt=prompt, filename=filename)
        else:
            prompt = self._build_prompt(topic)
            result = generator.generate_thumbnail(prompt=prompt, filename=filename)
        
        result['index'] = index
        result['filename'] = filename
        return result
    
    async def generate_single_async(
        self,
        topic: str,
        index: int,
        resolution: str,
        output_dir: str,
        face_path: Optional[Path] = None,
        face_mode: str = "auto",
        face_style: str = "realistic",
        use_reference_images: bool = False
    ) -> Dict[str, Any]:
        """Generate a single thumbnail asynchronously."""
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self.generate_single(
                    topic=topic,
                    index=index,
                    resolution=resolution,
                    output_dir=output_dir,
                    face_path=face_path,
                    face_mode=face_mode,
                    face_style=face_style,
                    use_reference_images=use_reference_images
                )
            )
        
        return result
    
    async def generate_and_store(
        self,
        topic: str,
        index: int,
        resolution: str,
        user_id: UUID,
        db: AsyncSession,
        face_path: Optional[Path] = None,
        face_mode: str = "auto",
        face_style: str = "realistic",
        use_reference_images: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a thumbnail and store it in cloud storage with DB tracking.
        
        Args:
            topic: Video topic/title
            index: Thumbnail index
            resolution: Resolution (1K, 2K, 4K)
            user_id: User's UUID for storage organization
            db: Database session for MediaFile record
            face_path: Optional face image path
            face_mode: Face placement mode
            face_style: Face rendering style
            use_reference_images: Whether to use reference images
            
        Returns:
            Dict with storage URL and metadata
        """
        # Use temp directory for generation
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await self.generate_single_async(
                topic=topic,
                index=index,
                resolution=resolution,
                output_dir=temp_dir,
                face_path=face_path,
                face_mode=face_mode,
                face_style=face_style,
                use_reference_images=use_reference_images
            )
            
            if not result.get('success') or not result.get('filepath'):
                return result
            
            # Get the generated file
            generated_path = Path(result['filepath'])
            if not generated_path.exists():
                return {
                    'success': False,
                    'error': 'Generated file not found',
                    'index': index
                }
            
            # Generate storage key
            filename = result.get('filename', f"thumbnail_{uuid4().hex[:8]}")
            storage_key = storage_service.generate_key(
                file_type="thumbnails",
                user_id=str(user_id),
                filename=filename,
                extension="png"
            )
            
            # Upload to storage
            storage_info = await storage_service.upload_from_path(
                local_path=generated_path,
                key=storage_key,
                content_type="image/png",
            )
            
            # Get file size
            file_size = generated_path.stat().st_size
        
        # Create MediaFile record
        media_file = MediaFile(
            user_id=user_id,
            file_type="thumbnail",
            storage_type=storage_info["storage_type"],
            storage_key=storage_info["storage_key"],
            storage_url=storage_info["storage_url"],
            original_filename=f"{filename}.png",
            file_size=file_size,
            mime_type="image/png",
            file_metadata={
                "topic": topic,
                "index": index,
                "resolution": resolution,
                "width": result.get('width'),
                "height": result.get('height'),
                "model": result.get('model'),
            }
        )
        db.add(media_file)
        await db.commit()
        await db.refresh(media_file)
        
        return {
            'success': True,
            'url': storage_info["storage_url"],
            'filepath': storage_info["storage_url"],
            'storage_type': storage_info["storage_type"],
            'media_file_id': str(media_file.id),
            'index': index,
            'width': result.get('width'),
            'height': result.get('height'),
            'model': result.get('model'),
        }
    
    def generate_batch(
        self,
        topic: str,
        num_thumbnails: int,
        resolution: str,
        face_path: Optional[Path] = None,
        face_mode: str = "auto",
        face_style: str = "realistic",
        use_reference_images: bool = False
    ) -> Dict[str, Any]:
        """
        Generate multiple thumbnails sequentially (legacy - no storage).
        For backward compatibility with existing code.
        
        Returns:
            Dict with success status, thumbnails list, and count
        """
        from backend.core.config import THUMBNAILS_DIR
        
        results = []
        
        for i in range(num_thumbnails):
            result = self.generate_single(
                topic=topic,
                index=i,
                resolution=resolution,
                output_dir=str(THUMBNAILS_DIR),
                face_path=face_path,
                face_mode=face_mode,
                face_style=face_style,
                use_reference_images=use_reference_images
            )
            results.append(result)
        
        successful = [r for r in results if r.get('success')]
        
        return {
            "success": len(successful) > 0,
            "thumbnails": results,
            "successful_count": len(successful)
        }
    
    async def generate_batch_with_storage(
        self,
        topic: str,
        num_thumbnails: int,
        resolution: str,
        user_id: UUID,
        db: AsyncSession,
        face_path: Optional[Path] = None,
        face_mode: str = "auto",
        face_style: str = "realistic",
        use_reference_images: bool = False
    ) -> Dict[str, Any]:
        """
        Generate multiple thumbnails with storage and DB tracking.
        
        Returns:
            Dict with success status, thumbnails list, and count
        """
        results = []
        
        for i in range(num_thumbnails):
            result = await self.generate_and_store(
                topic=topic,
                index=i,
                resolution=resolution,
                user_id=user_id,
                db=db,
                face_path=face_path,
                face_mode=face_mode,
                face_style=face_style,
                use_reference_images=use_reference_images
            )
            results.append(result)
        
        successful = [r for r in results if r.get('success')]
        
        return {
            "success": len(successful) > 0,
            "thumbnails": results,
            "successful_count": len(successful)
        }
    
    async def generate_parallel_stream(
        self,
        topic: str,
        num_thumbnails: int,
        resolution: str,
        face_path: Optional[Path] = None,
        face_mode: str = "auto",
        face_style: str = "realistic",
        use_reference_images: bool = False,
        user_id: Optional[UUID] = None,
        db: Optional[AsyncSession] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate thumbnails in parallel and yield SSE events as each completes.
        
        If user_id and db are provided, thumbnails are stored with MediaFile tracking.
        Otherwise, generates to local THUMBNAILS_DIR (legacy behavior).
        
        Yields:
            SSE formatted strings for progress updates
        """
        from backend.core.config import THUMBNAILS_DIR
        
        yield SSEService.progress(
            SSEService.STEP_THUMBNAILS,
            "Starting thumbnail generation...",
            {"current": 0, "total": num_thumbnails}
        )
        
        # Determine if we're using storage or legacy local mode
        use_storage = user_id is not None and db is not None
        
        if use_storage:
            # Create tasks with storage
            tasks = [
                asyncio.create_task(self.generate_and_store(
                    topic=topic,
                    index=i,
                    resolution=resolution,
                    user_id=user_id,
                    db=db,
                    face_path=face_path,
                    face_mode=face_mode,
                    face_style=face_style,
                    use_reference_images=use_reference_images
                ))
                for i in range(num_thumbnails)
            ]
        else:
            # Legacy: generate to temp then move to THUMBNAILS_DIR
            tasks = [
                asyncio.create_task(self.generate_single_async(
                    topic=topic,
                    index=i,
                    resolution=resolution,
                    output_dir=str(THUMBNAILS_DIR),
                    face_path=face_path,
                    face_mode=face_mode,
                    face_style=face_style,
                    use_reference_images=use_reference_images
                ))
                for i in range(num_thumbnails)
            ]
        
        completed = 0
        thumbnail_urls = []
        
        # Process results as they complete
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                completed += 1
                
                if result.get('success'):
                    if use_storage:
                        url = result.get('url')
                    else:
                        url = f"/thumbnails/{Path(result['filepath']).name}"
                    
                    thumbnail_urls.append({
                        "url": url,
                        "filepath": result.get('filepath'),
                        "original_index": result.get('index', 0)
                    })
                    
                    yield SSEService.thumbnail(
                        index=completed,
                        url=url,
                        filepath=result.get('filepath'),
                        current=completed,
                        total=num_thumbnails
                    )
                else:
                    yield SSEService.progress(
                        SSEService.STEP_THUMBNAILS,
                        f"Thumbnail {completed} generation failed",
                        {
                            "current": completed,
                            "total": num_thumbnails,
                            "error": result.get('error', 'Unknown error')
                        }
                    )
                    
            except Exception as e:
                completed += 1
                yield SSEService.error(
                    SSEService.STEP_THUMBNAILS,
                    f"Thumbnail generation error: {str(e)}",
                    str(e)
                )
