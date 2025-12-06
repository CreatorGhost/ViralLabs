"""
Thumbnail Generator using Google Gemini 3 Pro Image
Generates actual thumbnail images from text prompts
"""

import os
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime
from google import genai
from PIL import Image


class ThumbnailGenerator:
    """Generates YouTube thumbnails using Gemini 3 Pro Image (Nano Banana Pro)."""
    
    def __init__(
        self,
        model: str = "gemini-3-pro-image-preview",
        output_dir: str = "generated_thumbnails",
        aspect_ratio: str = "16:9",
        resolution: str = "2K"
    ):
        """
        Initialize the thumbnail generator.
        
        Args:
            model: Gemini image model to use (gemini-3-pro-image-preview or gemini-2.5-flash-image)
            output_dir: Directory to save generated thumbnails
            aspect_ratio: Aspect ratio for thumbnail (16:9, 9:16, 1:1, 4:3, 3:4, etc.)
            resolution: Resolution quality ("1K", "2K", "4K") - only for gemini-3-pro-image-preview
        """
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.aspect_ratio = aspect_ratio
        self.resolution = resolution
        
        # Initialize Gemini client
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set. "
                "Get your API key from: https://ai.google.dev/"
            )
        
        self.client = genai.Client(api_key=api_key)
    
    def generate_thumbnail(
        self,
        prompt: str,
        filename: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Dict:
        """
        Generate a thumbnail image from a text prompt.
        
        Args:
            prompt: Text description of the thumbnail to generate
            filename: Optional custom filename (without extension)
            aspect_ratio: Override default aspect ratio (16:9, 9:16, 1:1, etc.)
            resolution: Override default resolution ("1K", "2K", "4K")
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        print("\n" + "="*80)
        print("🎨 GENERATING THUMBNAIL WITH GEMINI 3 PRO IMAGE")
        print("="*80)
        print(f"Model: {self.model}")
        print(f"Aspect Ratio: {aspect_ratio or self.aspect_ratio}")
        if self.model == "gemini-3-pro-image-preview":
            print(f"Resolution: {resolution or self.resolution}")
        print("="*80 + "\n")
        
        print("📝 Prompt:")
        print(f"   {prompt[:200]}..." if len(prompt) > 200 else f"   {prompt}")
        print()
        
        try:
            # Prepare generation config
            config_dict = {
                "response_modalities": ["IMAGE"],
            }
            
            # Use the prompt as-is without adding resolution text
            # (Gemini will automatically generate at specified resolution based on config)
            enhanced_prompt = prompt
            
            # Store for later use
            aspect_ratio_to_use = aspect_ratio or self.aspect_ratio
            resolution_to_use = resolution or self.resolution
            
            print("⏳ Generating image (this may take 10-30 seconds)...\n")
            
            # Generate content
            response = self.client.models.generate_content(
                model=self.model,
                contents=enhanced_prompt,
                config=config_dict
            )
            
            # Extract and save the generated image
            image_saved = False
            output_filepath = None
            
            for part in response.parts:
                if part.text:
                    print(f"📋 Model Response: {part.text}\n")
                
                elif part.inline_data:
                    # Generate filename
                    if filename:
                        clean_filename = filename
                    else:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        clean_filename = f"thumbnail_{timestamp}"
                    
                    output_filepath = self.output_dir / f"{clean_filename}.png"
                    
                    # Save the image using PIL
                    image_data = part.inline_data.data
                    with open(output_filepath, 'wb') as f:
                        f.write(image_data)
                    
                    # Verify with PIL
                    img = Image.open(output_filepath)
                    width, height = img.size
                    
                    print("✅ Thumbnail generated successfully!")
                    print(f"   📁 Saved to: {output_filepath}")
                    print(f"   📐 Size: {width}x{height} pixels")
                    print(f"   📊 Aspect Ratio: {aspect_ratio_to_use}")
                    if self.model == "gemini-3-pro-image-preview":
                        print(f"   🎯 Resolution: {resolution_to_use}")
                    print()
                    
                    image_saved = True
            
            if not image_saved:
                return {
                    'success': False,
                    'error': 'No image data in response',
                    'filepath': None
                }
            
            return {
                'success': True,
                'filepath': str(output_filepath),
                'width': width,
                'height': height,
                'aspect_ratio': aspect_ratio_to_use,
                'resolution': resolution_to_use if self.model == "gemini-3-pro-image-preview" else None,
                'model': self.model,
                'prompt': prompt
            }
            
        except Exception as e:
            print(f"❌ Error generating thumbnail: {str(e)}\n")
            return {
                'success': False,
                'error': str(e),
                'filepath': None
            }
    
    def generate_thumbnail_with_reference(
        self,
        reference_images: List[str],
        video_title: str,
        filename: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Dict:
        """
        Generate a thumbnail using reference images as inspiration.
        
        Args:
            reference_images: List of file paths to reference thumbnail images
            video_title: The video title for context
            filename: Optional custom filename (without extension)
            aspect_ratio: Override default aspect ratio (16:9, 9:16, 1:1, etc.)
            resolution: Override default resolution ("1K", "2K", "4K")
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        print("\n" + "="*80)
        print("🎨 GENERATING THUMBNAIL WITH REFERENCE IMAGES")
        print("="*80)
        print(f"Model: {self.model}")
        print(f"Reference Images: {len(reference_images)}")
        print(f"Video Title: {video_title}")
        print(f"Aspect Ratio: {aspect_ratio or self.aspect_ratio}")
        if self.model == "gemini-3-pro-image-preview":
            print(f"Resolution: {resolution or self.resolution}")
        print("="*80 + "\n")
        
        try:
            # Prepare generation config
            config_dict = {
                "response_modalities": ["IMAGE"],
            }
            
            # Simple, direct prompt - let the images do the talking
            simple_prompt = f"""I'm showing you several successful YouTube thumbnails. 

Analyze these thumbnail images carefully and create a NEW, UNIQUE, and highly attractive YouTube thumbnail for this video:

VIDEO TITLE: "{video_title}"

Study the reference thumbnails and notice:
- What makes them eye-catching and clickable
- Color schemes and contrast
- Text placement and readability  
- Visual composition and focal points
- Professional quality and style

Now create an ORIGINAL thumbnail for my video that captures the same level of engagement and quality. Make it unique and perfectly suited for the video title above. Make sure it would make someone stop scrolling and click!"""
            
            print("📝 Prompt:")
            print(f"   Analyze reference images and create unique thumbnail for: '{video_title}'")
            print()
            
            # Load reference images using PIL
            contents = []
            
            print(f"📸 Loading {len(reference_images)} reference images...\n")
            for idx, img_path in enumerate(reference_images, 1):
                try:
                    img_path_obj = Path(img_path)
                    if img_path_obj.exists():
                        # Load image with PIL
                        pil_image = Image.open(img_path_obj)
                        contents.append(pil_image)
                        print(f"   ✓ Loaded reference {idx}: {img_path_obj.name}")
                    else:
                        print(f"   ✗ Reference {idx} not found: {img_path}")
                except Exception as e:
                    print(f"   ✗ Error loading reference {idx}: {str(e)}")
            
            # Add prompt AFTER images
            contents.append(simple_prompt)
            
            print()
            
            # Store for later use
            aspect_ratio_to_use = aspect_ratio or self.aspect_ratio
            resolution_to_use = resolution or self.resolution
            
            print("⏳ Generating thumbnail with references (this may take 15-40 seconds)...\n")
            
            # Generate content with references
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config_dict
            )
            
            # Extract and save the generated image
            image_saved = False
            output_filepath = None
            
            for part in response.parts:
                if part.text:
                    print(f"📋 Model Response: {part.text}\n")
                
                elif part.inline_data:
                    # Generate filename
                    if filename:
                        clean_filename = filename
                    else:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        clean_filename = f"thumbnail_ref_{timestamp}"
                    
                    output_filepath = self.output_dir / f"{clean_filename}.png"
                    
                    # Save the image using PIL
                    image_data = part.inline_data.data
                    with open(output_filepath, 'wb') as f:
                        f.write(image_data)
                    
                    # Verify with PIL
                    img = Image.open(output_filepath)
                    width, height = img.size
                    
                    print("✅ Thumbnail generated successfully with references!")
                    print(f"   📁 Saved to: {output_filepath}")
                    print(f"   📐 Size: {width}x{height} pixels")
                    print(f"   📊 Aspect Ratio: {aspect_ratio_to_use}")
                    if self.model == "gemini-3-pro-image-preview":
                        print(f"   🎯 Resolution: {resolution_to_use}")
                    print(f"   🖼️  References Used: {len(reference_images)}")
                    print()
                    
                    image_saved = True
            
            if not image_saved:
                return {
                    'success': False,
                    'error': 'No image data in response',
                    'filepath': None
                }
            
            return {
                'success': True,
                'filepath': str(output_filepath),
                'width': width,
                'height': height,
                'aspect_ratio': aspect_ratio_to_use,
                'resolution': resolution_to_use if self.model == "gemini-3-pro-image-preview" else None,
                'model': self.model,
                'references_used': len(reference_images),
                'video_title': video_title
            }
            
        except Exception as e:
            print(f"❌ Error generating thumbnail with references: {str(e)}\n")
            return {
                'success': False,
                'error': str(e),
                'filepath': None
            }
    
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
            video_title: The video title for context
            face_image_path: Path to the face image to integrate
            face_mode: Placement mode - "auto", "center", "left", "right"
            face_style: Style - "realistic", "professional", "cartoon"
            reference_images: Optional list of reference thumbnail paths
            filename: Optional custom filename (without extension)
            aspect_ratio: Override default aspect ratio
            resolution: Override default resolution
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        print("\n" + "="*80)
        print("🎨 GENERATING THUMBNAIL WITH FACE INTEGRATION")
        print("="*80)
        print(f"Model: {self.model}")
        print(f"Video Title: {video_title}")
        print(f"Face Image: {face_image_path}")
        print(f"Face Mode: {face_mode}")
        print(f"Face Style: {face_style}")
        print(f"Aspect Ratio: {aspect_ratio or self.aspect_ratio}")
        if self.model == "gemini-3-pro-image-preview":
            print(f"Resolution: {resolution or self.resolution}")
        print("="*80 + "\n")
        
        try:
            # Prepare generation config
            config_dict = {
                "response_modalities": ["IMAGE"],
            }
            
            # Build face placement instructions
            placement_instructions = {
                "auto": "Position the face naturally where it creates the most visual impact and engagement",
                "center": "Place the face prominently in the center of the thumbnail",
                "left": "Position the face on the left side of the thumbnail",
                "right": "Position the face on the right side of the thumbnail"
            }
            
            style_instructions = {
                "realistic": "Keep the face looking natural and realistic, as if photographed",
                "professional": "Style the face to look polished and professional, suitable for business content",
                "cartoon": "Transform the face into an appealing cartoon/illustrated style"
            }
            
            # Build the prompt
            face_prompt = f"""Create a highly engaging YouTube thumbnail for this video:

VIDEO TITLE: "{video_title}"

IMPORTANT: I'm providing a face image that MUST be integrated into the thumbnail.

FACE INTEGRATION REQUIREMENTS:
- {placement_instructions.get(face_mode, placement_instructions['auto'])}
- {style_instructions.get(face_style, style_instructions['realistic'])}
- The face should be a key visual element that draws attention
- Ensure the face is well-lit and clearly visible
- Make the expression engaging and relevant to the video topic

THUMBNAIL REQUIREMENTS:
- Bold, eye-catching design that would make viewers stop scrolling
- High contrast colors and clear visual hierarchy
- Professional quality suitable for YouTube
- 16:9 aspect ratio optimized for YouTube thumbnails
- Text overlay if appropriate (keep it minimal and impactful)

Create a thumbnail that combines the provided face with compelling visuals for maximum click-through rate!"""

            # Load face image
            contents = []
            
            print(f"📸 Loading face image...\n")
            face_path_obj = Path(face_image_path)
            if face_path_obj.exists():
                face_image = Image.open(face_path_obj)
                contents.append(face_image)
                print(f"   ✓ Loaded face image: {face_path_obj.name}")
            else:
                print(f"   ✗ Face image not found: {face_image_path}")
                return {
                    'success': False,
                    'error': f'Face image not found: {face_image_path}',
                    'filepath': None
                }
            
            # Load reference images if provided
            if reference_images:
                print(f"\n📸 Loading {len(reference_images)} reference images...\n")
                for idx, img_path in enumerate(reference_images, 1):
                    try:
                        img_path_obj = Path(img_path)
                        if img_path_obj.exists():
                            pil_image = Image.open(img_path_obj)
                            contents.append(pil_image)
                            print(f"   ✓ Loaded reference {idx}: {img_path_obj.name}")
                        else:
                            print(f"   ✗ Reference {idx} not found: {img_path}")
                    except Exception as e:
                        print(f"   ✗ Error loading reference {idx}: {str(e)}")
            
            # Add prompt after images
            contents.append(face_prompt)
            
            print()
            
            # Store for later use
            aspect_ratio_to_use = aspect_ratio or self.aspect_ratio
            resolution_to_use = resolution or self.resolution
            
            print("⏳ Generating thumbnail with face (this may take 15-40 seconds)...\n")
            
            # Generate content
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config_dict
            )
            
            # Extract and save the generated image
            image_saved = False
            output_filepath = None
            
            for part in response.parts:
                if part.text:
                    print(f"📋 Model Response: {part.text}\n")
                
                elif part.inline_data:
                    # Generate filename
                    if filename:
                        clean_filename = filename
                    else:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        clean_filename = f"thumbnail_face_{timestamp}"
                    
                    output_filepath = self.output_dir / f"{clean_filename}.png"
                    
                    # Save the image
                    image_data = part.inline_data.data
                    with open(output_filepath, 'wb') as f:
                        f.write(image_data)
                    
                    # Verify with PIL
                    img = Image.open(output_filepath)
                    width, height = img.size
                    
                    print("✅ Thumbnail with face generated successfully!")
                    print(f"   📁 Saved to: {output_filepath}")
                    print(f"   📐 Size: {width}x{height} pixels")
                    print(f"   📊 Aspect Ratio: {aspect_ratio_to_use}")
                    if self.model == "gemini-3-pro-image-preview":
                        print(f"   🎯 Resolution: {resolution_to_use}")
                    print(f"   👤 Face Mode: {face_mode}")
                    print(f"   🎨 Face Style: {face_style}")
                    print()
                    
                    image_saved = True
            
            if not image_saved:
                return {
                    'success': False,
                    'error': 'No image data in response',
                    'filepath': None
                }
            
            return {
                'success': True,
                'filepath': str(output_filepath),
                'width': width,
                'height': height,
                'aspect_ratio': aspect_ratio_to_use,
                'resolution': resolution_to_use if self.model == "gemini-3-pro-image-preview" else None,
                'model': self.model,
                'face_mode': face_mode,
                'face_style': face_style,
                'video_title': video_title
            }
            
        except Exception as e:
            print(f"❌ Error generating thumbnail with face: {str(e)}\n")
            return {
                'success': False,
                'error': str(e),
                'filepath': None
            }
    
    def generate_multiple_variations(
        self,
        prompt: str,
        num_variations: int = 3,
        base_filename: Optional[str] = None
    ) -> list[Dict]:
        """
        Generate multiple variations of a thumbnail.
        
        Args:
            prompt: Text description of the thumbnail
            num_variations: Number of variations to generate
            base_filename: Base filename for variations
            
        Returns:
            List of result dicts
        """
        print("\n" + "="*80)
        print(f"🎨 GENERATING {num_variations} THUMBNAIL VARIATIONS")
        print("="*80 + "\n")
        
        results = []
        
        for i in range(1, num_variations + 1):
            print(f"📸 Generating variation {i}/{num_variations}...")
            
            # Add slight variation to prompt
            varied_prompt = f"{prompt}\n\n[Variation {i} - slightly different creative interpretation]"
            
            filename = f"{base_filename}_v{i}" if base_filename else None
            
            result = self.generate_thumbnail(
                prompt=varied_prompt,
                filename=filename
            )
            
            results.append(result)
            
            if result['success']:
                print(f"✅ Variation {i} complete!\n")
            else:
                print(f"❌ Variation {i} failed: {result.get('error')}\n")
        
        successful = sum(1 for r in results if r['success'])
        print("="*80)
        print(f"✅ Generated {successful}/{num_variations} variations successfully")
        print("="*80 + "\n")
        
        return results
    
    def generate_from_multiple_prompts(
        self,
        prompts: List[str],
        base_filename: Optional[str] = None
    ) -> list[Dict]:
        """
        Generate thumbnails from multiple different prompts (sequentially).
        
        Args:
            prompts: List of different prompts
            base_filename: Base filename for outputs
            
        Returns:
            List of result dicts
        """
        print("\n" + "="*80)
        print(f"🎨 GENERATING {len(prompts)} THUMBNAILS FROM DIFFERENT PROMPTS")
        print("="*80 + "\n")
        
        results = []
        
        for i, prompt in enumerate(prompts, 1):
            print(f"📸 Generating thumbnail {i}/{len(prompts)}...")
            print(f"   Prompt preview: {prompt[:100]}...\n")
            
            filename = f"{base_filename}_v{i}" if base_filename else None
            
            result = self.generate_thumbnail(
                prompt=prompt,
                filename=filename
            )
            
            results.append(result)
            
            if result['success']:
                print(f"✅ Thumbnail {i} complete!\n")
            else:
                print(f"❌ Thumbnail {i} failed: {result.get('error')}\n")
        
        successful = sum(1 for r in results if r['success'])
        print("="*80)
        print(f"✅ Generated {successful}/{len(prompts)} thumbnails successfully")
        print("="*80 + "\n")
        
        return results


# ===== Convenience Functions =====

def generate_thumbnail_from_prompt(
    prompt: str,
    output_filename: Optional[str] = None,
    model: str = "gemini-3-pro-image-preview",
    aspect_ratio: str = "16:9",
    resolution: str = "2K"
) -> Dict:
    """
    Quick function to generate a thumbnail from a prompt.
    
    Args:
        prompt: Text description of the thumbnail
        output_filename: Optional custom filename
        model: Gemini model to use
        aspect_ratio: Aspect ratio (16:9, 9:16, 1:1, etc.)
        resolution: Resolution quality ("1K", "2K", "4K")
        
    Returns:
        Dict with success status and filepath
        
    Example:
        >>> result = generate_thumbnail_from_prompt(
        ...     "A dramatic anime thumbnail with Goku in Super Saiyan form",
        ...     output_filename="my_thumbnail",
        ...     aspect_ratio="16:9",
        ...     resolution="4K"
        ... )
        >>> print(result['filepath'])
    """
    generator = ThumbnailGenerator(
        model=model,
        aspect_ratio=aspect_ratio,
        resolution=resolution
    )
    return generator.generate_thumbnail(prompt, filename=output_filename)


def generate_thumbnail_variations(
    prompt: str,
    num_variations: int = 3,
    base_filename: Optional[str] = None,
    model: str = "gemini-3-pro-image-preview"
) -> list[Dict]:
    """
    Generate multiple variations of a thumbnail.
    
    Args:
        prompt: Text description
        num_variations: Number of variations
        base_filename: Base filename
        model: Gemini model to use
        
    Returns:
        List of result dicts
    """
    generator = ThumbnailGenerator(model=model)
    return generator.generate_multiple_variations(prompt, num_variations, base_filename)

