"""
Unified Image Generator Factory
Provides a single interface to switch between Gemini and Seedream providers.

Configuration via .env:
    IMAGE_PROVIDER=gemini    # Use Google Gemini
    IMAGE_PROVIDER=seedream  # Use BytePlus Seedream
    ENHANCE_PROMPTS=true     # Auto-enhance prompts for thumbnails (default: true)
"""

import os
from typing import Optional, Dict, List, Protocol, runtime_checkable
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


def should_enhance_prompts() -> bool:
    """Check if prompt enhancement is enabled."""
    return os.getenv("ENHANCE_PROMPTS", "true").lower() in ("true", "1", "yes")


@runtime_checkable
class ImageGeneratorProtocol(Protocol):
    """Protocol defining the interface for image generators."""
    
    def generate_thumbnail(
        self,
        prompt: str,
        filename: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Dict: ...
    
    def generate_thumbnail_with_face(
        self,
        video_title: str,
        face_image_path: str,
        face_mode: str = "auto",
        face_style: str = "realistic",
        reference_images: Optional[List[str]] = None,
        filename: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Dict: ...


class ImageGeneratorFactory:
    """
    Factory class for creating image generators based on configuration.
    
    Usage:
        generator = ImageGeneratorFactory.create()
        result = generator.generate_thumbnail("A beautiful sunset")
    """
    
    PROVIDERS = ["gemini", "seedream"]
    
    @staticmethod
    def get_provider() -> str:
        """Get the configured image provider from environment."""
        provider = os.getenv("IMAGE_PROVIDER", "gemini").lower()
        if provider not in ImageGeneratorFactory.PROVIDERS:
            print(f"⚠️ Unknown provider '{provider}', defaulting to 'gemini'")
            return "gemini"
        return provider
    
    @staticmethod
    def create(
        provider: Optional[str] = None,
        output_dir: str = "generated_thumbnails",
        resolution: str = "2K",
        **kwargs
    ) -> "UnifiedImageGenerator":
        """
        Create an image generator based on the configured provider.
        
        Args:
            provider: Override the configured provider ("gemini" or "seedream")
            output_dir: Directory to save generated images
            resolution: Default resolution ("1K", "2K", "4K")
            **kwargs: Additional provider-specific arguments
            
        Returns:
            UnifiedImageGenerator wrapping the appropriate provider
        """
        provider = provider or ImageGeneratorFactory.get_provider()
        
        print(f"🖼️ Creating image generator with provider: {provider}")
        
        if provider == "seedream":
            return UnifiedImageGenerator(
                provider="seedream",
                output_dir=output_dir,
                resolution=resolution,
                **kwargs
            )
        else:
            return UnifiedImageGenerator(
                provider="gemini",
                output_dir=output_dir,
                resolution=resolution,
                **kwargs
            )
    
    @staticmethod
    def is_provider_available(provider: str) -> bool:
        """Check if a provider is properly configured."""
        if provider == "gemini":
            return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
        elif provider == "seedream":
            return bool(os.getenv("ARK_API_KEY"))
        return False


class UnifiedImageGenerator:
    """
    Unified image generator that wraps both Gemini and Seedream providers.
    Provides a consistent interface regardless of the underlying provider.
    """
    
    def __init__(
        self,
        provider: str = "gemini",
        output_dir: str = "generated_thumbnails",
        resolution: str = "2K",
        aspect_ratio: str = "16:9",
        **kwargs
    ):
        """
        Initialize the unified image generator.
        
        Args:
            provider: "gemini" or "seedream"
            output_dir: Directory to save generated images
            resolution: Default resolution ("1K", "2K", "4K")
            aspect_ratio: Default aspect ratio
        """
        self.provider = provider
        self.output_dir = output_dir
        self.resolution = resolution
        self.aspect_ratio = aspect_ratio
        self._generator = None
        
        self._init_generator(**kwargs)
    
    def _init_generator(self, **kwargs):
        """Initialize the underlying provider generator."""
        if self.provider == "seedream":
            # Try both import styles for flexibility
            try:
                from src.seedream_generator import SeedreamGenerator
            except ModuleNotFoundError:
                from seedream_generator import SeedreamGenerator
            
            model = kwargs.get('model') or os.getenv('ARK_MODEL_ID') or 'seedream-4-0-250828'
            self._generator = SeedreamGenerator(
                model=model,
                output_dir=self.output_dir,
                size=self.resolution,
                watermark=kwargs.get('watermark', False)
            )
            print(f"✅ Initialized Seedream generator (model: {model})")
            
        else:  # gemini
            try:
                from src.thumbnail_generator import ThumbnailGenerator
            except ModuleNotFoundError:
                from thumbnail_generator import ThumbnailGenerator
            
            model = kwargs.get('model') or 'gemini-3-pro-image-preview'
            self._generator = ThumbnailGenerator(
                model=model,
                output_dir=self.output_dir,
                aspect_ratio=self.aspect_ratio,
                resolution=self.resolution
            )
            print(f"✅ Initialized Gemini generator (model: {model})")
    
    def generate_thumbnail(
        self,
        prompt: str,
        filename: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        enhance_prompt: Optional[bool] = None,
        text_overlay: Optional[str] = None
    ) -> Dict:
        """
        Generate a thumbnail image from a text prompt.
        
        Args:
            prompt: Text description of the image (will be enhanced if enabled)
            filename: Optional custom filename
            aspect_ratio: Override default aspect ratio
            resolution: Override default resolution
            enhance_prompt: Override ENHANCE_PROMPTS setting (None = use env setting)
            text_overlay: Specific text to show on thumbnail
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        # Determine if we should enhance the prompt
        do_enhance = enhance_prompt if enhance_prompt is not None else should_enhance_prompts()
        
        final_prompt = prompt
        if do_enhance:
            try:
                from prompt_enhancer import enhance_for_seedream, enhance_prompt as enhance_fn
                if self.provider == "seedream":
                    final_prompt = enhance_for_seedream(prompt, text_overlay)
                else:
                    final_prompt = enhance_fn(prompt, text_content=text_overlay)
                print(f"📝 Enhanced prompt: {final_prompt[:100]}...")
            except ImportError:
                print("⚠️ Prompt enhancer not available, using original prompt")
            except Exception as e:
                print(f"⚠️ Prompt enhancement failed: {e}, using original prompt")
        
        if self.provider == "seedream":
            # Seedream uses 'size' instead of 'resolution'
            return self._generator.generate_image(
                prompt=final_prompt,
                filename=filename,
                size=resolution or self.resolution
            )
        else:
            return self._generator.generate_thumbnail(
                prompt=final_prompt,
                filename=filename,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
    
    def generate_thumbnail_with_face(
        self,
        video_title: str,
        face_image_path: str,
        face_mode: str = "auto",
        face_style: str = "realistic",
        reference_images: Optional[List[str]] = None,
        filename: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Dict:
        """
        Generate a thumbnail with a face image integrated.
        
        Args:
            video_title: The video title/prompt for context
            face_image_path: Path to the face image
            face_mode: Face placement mode
            face_style: Face rendering style
            reference_images: Optional reference images
            filename: Optional custom filename
            aspect_ratio: Override aspect ratio
            resolution: Override resolution
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        if self.provider == "seedream":
            # Seedream uses generate_with_face
            return self._generator.generate_with_face(
                face_image=face_image_path,
                prompt=video_title,
                filename=filename,
                size=resolution or self.resolution
            )
        else:
            return self._generator.generate_thumbnail_with_face(
                video_title=video_title,
                face_image_path=face_image_path,
                face_mode=face_mode,
                face_style=face_style,
                reference_images=reference_images,
                filename=filename,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
    
    def generate_thumbnail_with_reference(
        self,
        reference_images: List[str],
        video_title: str,
        filename: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Dict:
        """
        Generate a thumbnail using reference images.
        
        Args:
            reference_images: List of reference image paths
            video_title: The video title/prompt
            filename: Optional custom filename
            aspect_ratio: Override aspect ratio
            resolution: Override resolution
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        if self.provider == "seedream":
            return self._generator.generate_with_reference(
                reference_images=reference_images,
                prompt=video_title,
                filename=filename,
                size=resolution or self.resolution
            )
        else:
            return self._generator.generate_thumbnail_with_reference(
                reference_images=reference_images,
                video_title=video_title,
                filename=filename,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
    
    def edit_image(
        self,
        reference_image: str,
        edit_instruction: str,
        filename: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Dict:
        """
        Edit an existing image with text instructions.
        
        Args:
            reference_image: Path to image to edit
            edit_instruction: Description of changes
            filename: Optional custom filename
            resolution: Override resolution
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        if self.provider == "seedream":
            return self._generator.edit_image(
                reference_image=reference_image,
                edit_instruction=edit_instruction,
                filename=filename,
                size=resolution or self.resolution
            )
        else:
            # Gemini doesn't have a direct edit method, use generate with reference
            return self._generator.generate_thumbnail_with_reference(
                reference_images=[reference_image],
                video_title=edit_instruction,
                filename=filename,
                resolution=resolution
            )
    
    def get_provider_info(self) -> Dict:
        """Get information about the current provider."""
        return {
            "provider": self.provider,
            "resolution": self.resolution,
            "aspect_ratio": self.aspect_ratio,
            "output_dir": self.output_dir,
            "model": getattr(self._generator, 'model', 'unknown')
        }


# Convenience functions
def create_image_generator(**kwargs) -> UnifiedImageGenerator:
    """Create an image generator with the configured provider."""
    return ImageGeneratorFactory.create(**kwargs)


def get_current_provider() -> str:
    """Get the currently configured image provider."""
    return ImageGeneratorFactory.get_provider()


# CLI Testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test unified image generator")
    parser.add_argument("prompt", type=str, help="Image prompt")
    parser.add_argument("--provider", "-p", type=str, choices=["gemini", "seedream"], 
                       help="Override provider")
    parser.add_argument("--output", "-o", type=str, help="Output filename")
    parser.add_argument("--resolution", "-r", type=str, default="2K", help="Resolution")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🖼️ UNIFIED IMAGE GENERATOR TEST")
    print("="*80)
    print(f"Configured Provider: {get_current_provider()}")
    print(f"Override Provider: {args.provider or 'None'}")
    print(f"Prompt: {args.prompt}")
    print(f"Resolution: {args.resolution}")
    print("="*80 + "\n")
    
    generator = create_image_generator(
        provider=args.provider,
        resolution=args.resolution
    )
    
    print(f"\nProvider Info: {generator.get_provider_info()}\n")
    
    result = generator.generate_thumbnail(
        prompt=args.prompt,
        filename=args.output
    )
    
    if result.get('success'):
        print("\n" + "="*80)
        print("🎉 SUCCESS!")
        print(f"Image saved to: {result.get('filepath')}")
        print("="*80 + "\n")
    else:
        print("\n" + "="*80)
        print(f"❌ FAILED: {result.get('error')}")
        print("="*80 + "\n")

