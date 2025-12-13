"""
Seedream Image Generator - Backup to Gemini
Uses BytePlus ModelArk's Seedream models for image generation
Documentation: https://docs.byteplus.com/en/docs/ModelArk/1541523

Setup:
1. Create account at https://console.byteplus.com/
2. Navigate to ModelArk > Foundation Models
3. Activate Seedream model
4. Create an API Key at https://console.byteplus.com/ark/region:ark+ap-southeast-1/apikey
5. Set ARK_API_KEY in your .env file
6. Set ARK_MODEL_ID to your model (e.g., seedream-4-0-250828)

Model IDs (check BytePlus console for latest):
- seedream-4-0-250828 (Seedream 4.0 - confirmed working)
- seedream-4-5-251128 (Seedream 4.5)
"""

import os
import base64
import requests
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime

# Load .env file if available
try:
    from dotenv import load_dotenv
    # Load from project root
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not installed, skip


class SeedreamGenerator:
    """Generates images using BytePlus Seedream models (4.0 or 4.5)."""
    
    # BytePlus API endpoint
    API_ENDPOINT = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"
    
    # Valid size options for Seedream
    VALID_SIZES = ["1K", "2K", "4K"]
    
    def __init__(
        self,
        model: Optional[str] = None,
        output_dir: str = "generated_thumbnails",
        size: str = "2K",
        watermark: bool = False,
        api_key: Optional[str] = None
    ):
        """
        Initialize the Seedream generator.
        
        Args:
            model: Seedream model ID. 
                   Defaults to ARK_MODEL_ID env var or "seedream-4-0-250828"
                   Known working models:
                   - seedream-4-0-250828 (Seedream 4.0)
                   - seedream-4-5-251128 (Seedream 4.5)
            output_dir: Directory to save generated images
            size: Image size - "1K", "2K", or "4K"
            watermark: Whether to add watermark to generated images
            api_key: BytePlus API key (defaults to ARK_API_KEY env var)
        """
        # Get model from parameter, env var, or default
        self.model = model or os.getenv('ARK_MODEL_ID') or "seedream-4-0-250828"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.size = size if size in self.VALID_SIZES else "2K"
        self.watermark = watermark
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('ARK_API_KEY')
        if not self.api_key:
            raise ValueError(
                "ARK_API_KEY environment variable not set.\n"
                "Setup steps:\n"
                "1. Create account at https://console.byteplus.com/\n"
                "2. Navigate to ModelArk > Foundation Models\n"
                "3. Activate Seedream model\n"
                "4. Create API Key at https://console.byteplus.com/ark/region:ark+ap-southeast-1/apikey\n"
                "5. Add ARK_API_KEY=your_key to your .env file"
            )
        
        print(f"✅ Initialized Seedream generator (model: {self.model})")
    
    def generate_image(
        self,
        prompt: str,
        filename: Optional[str] = None,
        size: Optional[str] = None,
        watermark: Optional[bool] = None,
    ) -> Dict:
        """
        Generate an image from a text prompt using BytePlus API directly.
        
        Args:
            prompt: Text description of the image to generate
            filename: Optional custom filename (without extension)
            size: Override default size ("1K", "2K", "4K")
            watermark: Override default watermark setting
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        print("\n" + "="*80)
        print("🎨 GENERATING IMAGE WITH SEEDREAM")
        print("="*80)
        print(f"Model: {self.model}")
        print(f"Size: {size or self.size}")
        print(f"Watermark: {watermark if watermark is not None else self.watermark}")
        print("="*80 + "\n")
        
        print("📝 Prompt:")
        print(f"   {prompt[:200]}..." if len(prompt) > 200 else f"   {prompt}")
        print()
        
        try:
            # Resolve size (must be 1K, 2K, or 4K for BytePlus)
            size_to_use = size or self.size
            if size_to_use not in self.VALID_SIZES:
                size_to_use = "2K"  # Default to 2K
            
            watermark_to_use = watermark if watermark is not None else self.watermark
            
            print("⏳ Generating image (this may take 10-60 seconds)...\n")
            
            # Build payload matching working implementation
            payload = {
                "model": self.model,
                "prompt": prompt,
                "size": size_to_use,
                "response_format": "b64_json",
                "watermark": watermark_to_use,
                "sequential_image_generation": "disabled",
                "stream": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Make direct HTTP request
            print(f"📡 Calling BytePlus API...")
            response = requests.post(
                self.API_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=120
            )
            
            # Handle errors
            if response.status_code != 200:
                error_text = response.text
                print(f"❌ API Error: {response.status_code}")
                print(f"   Response: {error_text[:500]}")
                
                if 'ModelNotOpen' in error_text:
                    return {
                        'success': False,
                        'error': (
                            f"Model '{self.model}' not activated on your account.\n"
                            "To fix this:\n"
                            "1. Go to https://console.byteplus.com/ark\n"
                            "2. Navigate to 'Foundation Models'\n"
                            "3. Find and activate the Seedream model\n"
                            "4. Set ARK_MODEL_ID in .env to the exact model name"
                        ),
                        'filepath': None
                    }
                return {
                    'success': False,
                    'error': f"API Error {response.status_code}: {error_text[:200]}",
                    'filepath': None
                }
            
            # Parse response
            data = response.json()
            
            if "data" not in data or len(data["data"]) == 0:
                return {
                    'success': False,
                    'error': 'No image data in response',
                    'filepath': None
                }
            
            b64_json = data["data"][0]["b64_json"]
            print(f"✅ Image generated! (base64 length: {len(b64_json)} chars)\n")
            
            # Generate filename
            if filename:
                clean_filename = filename
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                clean_filename = f"seedream_{timestamp}"
            
            output_filepath = self.output_dir / f"{clean_filename}.png"
            
            # Decode and save the image
            print("💾 Saving image...")
            image_data = base64.b64decode(b64_json)
            with open(output_filepath, 'wb') as f:
                f.write(image_data)
            
            # Get image dimensions
            width, height = None, None
            try:
                from PIL import Image
                img = Image.open(output_filepath)
                width, height = img.size
                img.close()
            except ImportError:
                pass  # PIL not available
            
            print("✅ Image saved successfully!")
            print(f"   📁 Saved to: {output_filepath}")
            if width and height:
                print(f"   📐 Size: {width}x{height} pixels")
            print(f"   🎯 Model: {self.model}")
            print()
            
            return {
                'success': True,
                'filepath': str(output_filepath),
                'b64_json': b64_json,
                'width': width,
                'height': height,
                'size': size_to_use,
                'model': self.model,
                'prompt': prompt
            }
            
        except requests.exceptions.Timeout:
            print(f"❌ Request timed out after 120 seconds\n")
            return {
                'success': False,
                'error': 'Request timed out. BytePlus API may be slow or unreachable.',
                'filepath': None
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {str(e)}\n")
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'filepath': None
            }
        except Exception as e:
            print(f"❌ Error generating image: {str(e)}\n")
            return {
                'success': False,
                'error': str(e),
                'filepath': None
            }
    
    def generate_thumbnail(
        self,
        prompt: str,
        filename: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Dict:
        """
        Generate a thumbnail image (compatible interface with ThumbnailGenerator).
        
        Args:
            prompt: Text description of the thumbnail to generate
            filename: Optional custom filename (without extension)
            aspect_ratio: Aspect ratio (16:9, 9:16, 1:1) - mapped to size
            resolution: Resolution quality ("1K", "2K") - mapped to size
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        # Map aspect ratio and resolution to Seedream size
        if resolution:
            size = resolution
        elif aspect_ratio:
            size = aspect_ratio
        else:
            size = self.size
        
        return self.generate_image(
            prompt=prompt,
            filename=filename,
            size=size
        )
    
    def generate_multiple(
        self,
        prompt: str,
        num_images: int = 3,
        base_filename: Optional[str] = None,
        size: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate multiple images from the same prompt.
        
        Args:
            prompt: Text description
            num_images: Number of images to generate
            base_filename: Base filename for outputs
            size: Image size
            
        Returns:
            List of result dicts
        """
        print("\n" + "="*80)
        print(f"🎨 GENERATING {num_images} IMAGES WITH SEEDREAM 4.5")
        print("="*80 + "\n")
        
        results = []
        
        for i in range(1, num_images + 1):
            print(f"📸 Generating image {i}/{num_images}...")
            
            filename = f"{base_filename}_v{i}" if base_filename else None
            
            result = self.generate_image(
                prompt=prompt,
                filename=filename,
                size=size
            )
            
            results.append(result)
            
            if result['success']:
                print(f"✅ Image {i} complete!\n")
            else:
                print(f"❌ Image {i} failed: {result.get('error')}\n")
        
        successful = sum(1 for r in results if r['success'])
        print("="*80)
        print(f"✅ Generated {successful}/{num_images} images successfully")
        print("="*80 + "\n")
        
        return results
    
    def edit_image(
        self,
        reference_image: str,
        edit_instruction: str,
        filename: Optional[str] = None,
        size: Optional[str] = None,
    ) -> Dict:
        """
        Edit an existing image using a text instruction.
        
        Args:
            reference_image: Path to reference image OR base64 string
            edit_instruction: Text description of changes to make
            filename: Optional custom filename (without extension)
            size: Override default size ("1K", "2K", "4K")
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        print("\n" + "="*80)
        print("🎨 EDITING IMAGE WITH SEEDREAM")
        print("="*80)
        print(f"Model: {self.model}")
        print(f"Edit Instruction: {edit_instruction[:100]}...")
        print("="*80 + "\n")
        
        try:
            # Load reference image
            if Path(reference_image).exists():
                print(f"📸 Loading reference image: {reference_image}")
                with open(reference_image, 'rb') as f:
                    image_bytes = f.read()
                b64_image = base64.b64encode(image_bytes).decode('utf-8')
            else:
                # Assume it's already base64
                b64_image = reference_image
            
            # Create Data URI (required by BytePlus API)
            data_uri = f"data:image/png;base64,{b64_image}"
            
            size_to_use = size or self.size
            if size_to_use not in self.VALID_SIZES:
                size_to_use = "2K"
            
            print("⏳ Editing image (this may take 10-60 seconds)...\n")
            
            payload = {
                "model": self.model,
                "prompt": edit_instruction,
                "image": data_uri,
                "size": size_to_use,
                "response_format": "b64_json",
                "watermark": self.watermark,
                "sequential_image_generation": "disabled",
                "stream": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            print(f"📡 Calling BytePlus API...")
            response = requests.post(
                self.API_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=120
            )
            
            if response.status_code != 200:
                error_text = response.text
                print(f"❌ API Error: {response.status_code}")
                return {
                    'success': False,
                    'error': f"API Error {response.status_code}: {error_text[:200]}",
                    'filepath': None
                }
            
            data = response.json()
            b64_json = data["data"][0]["b64_json"]
            print(f"✅ Image edited! (base64 length: {len(b64_json)} chars)\n")
            
            # Generate filename
            if filename:
                clean_filename = filename
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                clean_filename = f"seedream_edit_{timestamp}"
            
            output_filepath = self.output_dir / f"{clean_filename}.png"
            
            # Save the image
            print("💾 Saving image...")
            image_data = base64.b64decode(b64_json)
            with open(output_filepath, 'wb') as f:
                f.write(image_data)
            
            # Get dimensions
            width, height = None, None
            try:
                from PIL import Image
                img = Image.open(output_filepath)
                width, height = img.size
                img.close()
            except ImportError:
                pass
            
            print("✅ Edited image saved!")
            print(f"   📁 Saved to: {output_filepath}")
            if width and height:
                print(f"   📐 Size: {width}x{height} pixels")
            print()
            
            return {
                'success': True,
                'filepath': str(output_filepath),
                'b64_json': b64_json,
                'width': width,
                'height': height,
                'size': size_to_use,
                'model': self.model,
                'edit_instruction': edit_instruction
            }
            
        except Exception as e:
            print(f"❌ Error editing image: {str(e)}\n")
            return {
                'success': False,
                'error': str(e),
                'filepath': None
            }
    
    def generate_with_face(
        self,
        face_image: str,
        prompt: str,
        filename: Optional[str] = None,
        size: Optional[str] = None,
    ) -> Dict:
        """
        Generate an image incorporating a face/subject from a reference image.
        Uses Seedream's Subject Locking capability to preserve face identity.
        
        Args:
            face_image: Path to face image OR base64 string
            prompt: Text description of the image to generate (describe the scene, 
                   the model will preserve the face from the reference)
            filename: Optional custom filename (without extension)
            size: Override default size ("1K", "2K", "4K")
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        print("\n" + "="*80)
        print("🎨 GENERATING IMAGE WITH FACE (SEEDREAM)")
        print("="*80)
        print(f"Model: {self.model}")
        print(f"Prompt: {prompt[:100]}...")
        print("="*80 + "\n")
        
        try:
            # Load face image
            if Path(face_image).exists():
                print(f"👤 Loading face image: {face_image}")
                with open(face_image, 'rb') as f:
                    image_bytes = f.read()
                b64_image = base64.b64encode(image_bytes).decode('utf-8')
            else:
                b64_image = face_image
            
            # Create Data URI
            data_uri = f"data:image/png;base64,{b64_image}"
            
            size_to_use = size or self.size
            if size_to_use not in self.VALID_SIZES:
                size_to_use = "2K"
            
            # Enhanced prompt for face preservation
            enhanced_prompt = f"""Preserve the face and identity of the person in the reference image.
Generate a new image with this person: {prompt}
Maintain facial features, skin tone, and likeness accurately."""
            
            print("⏳ Generating image with face (this may take 10-60 seconds)...\n")
            
            payload = {
                "model": self.model,
                "prompt": enhanced_prompt,
                "image": data_uri,
                "size": size_to_use,
                "response_format": "b64_json",
                "watermark": self.watermark,
                "sequential_image_generation": "disabled",
                "stream": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            print(f"📡 Calling BytePlus API...")
            response = requests.post(
                self.API_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=120
            )
            
            if response.status_code != 200:
                error_text = response.text
                print(f"❌ API Error: {response.status_code}")
                return {
                    'success': False,
                    'error': f"API Error {response.status_code}: {error_text[:200]}",
                    'filepath': None
                }
            
            data = response.json()
            b64_json = data["data"][0]["b64_json"]
            print(f"✅ Image with face generated! (base64 length: {len(b64_json)} chars)\n")
            
            # Generate filename
            if filename:
                clean_filename = filename
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                clean_filename = f"seedream_face_{timestamp}"
            
            output_filepath = self.output_dir / f"{clean_filename}.png"
            
            # Save the image
            print("💾 Saving image...")
            image_data = base64.b64decode(b64_json)
            with open(output_filepath, 'wb') as f:
                f.write(image_data)
            
            # Get dimensions
            width, height = None, None
            try:
                from PIL import Image
                img = Image.open(output_filepath)
                width, height = img.size
                img.close()
            except ImportError:
                pass
            
            print("✅ Image with face saved!")
            print(f"   📁 Saved to: {output_filepath}")
            if width and height:
                print(f"   📐 Size: {width}x{height} pixels")
            print()
            
            return {
                'success': True,
                'filepath': str(output_filepath),
                'b64_json': b64_json,
                'width': width,
                'height': height,
                'size': size_to_use,
                'model': self.model,
                'prompt': prompt
            }
            
        except Exception as e:
            print(f"❌ Error generating image with face: {str(e)}\n")
            return {
                'success': False,
                'error': str(e),
                'filepath': None
            }
    
    def generate_with_reference(
        self,
        reference_images: List[str],
        prompt: str,
        filename: Optional[str] = None,
        size: Optional[str] = None,
    ) -> Dict:
        """
        Generate an image using reference images for style/subject consistency.
        
        Note: BytePlus API currently accepts one image per request via the 'image' field.
        For multiple references, we use the first image. For true multi-image fusion,
        Seedream 4.5 with specific endpoint may be required.
        
        Args:
            reference_images: List of paths to reference images
            prompt: Text description incorporating reference styles
            filename: Optional custom filename
            size: Override default size
            
        Returns:
            Dict with success status, filepath, and metadata
        """
        if not reference_images:
            return self.generate_image(prompt=prompt, filename=filename, size=size)
        
        # Use first reference image
        return self.edit_image(
            reference_image=reference_images[0],
            edit_instruction=prompt,
            filename=filename,
            size=size
        )


# ===== Convenience Functions =====

def generate_image_seedream(
    prompt: str,
    output_filename: Optional[str] = None,
    size: str = "2K",
    watermark: bool = False
) -> Dict:
    """
    Quick function to generate an image using Seedream 4.5.
    
    Args:
        prompt: Text description of the image
        output_filename: Optional custom filename
        size: Image size ("1K", "2K", "1024x1024", etc.)
        watermark: Whether to add watermark
        
    Returns:
        Dict with success status and filepath
        
    Example:
        >>> result = generate_image_seedream(
        ...     "A futuristic city with flying cars",
        ...     output_filename="my_image",
        ...     size="2K"
        ... )
        >>> print(result['filepath'])
    """
    generator = SeedreamGenerator(size=size, watermark=watermark)
    return generator.generate_image(prompt, filename=output_filename)


# ===== Command Line Testing =====

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate images using Seedream 4.5 model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python seedream_generator.py "A beautiful sunset over mountains"
  python seedream_generator.py "Cyberpunk city" --size 2K --output my_image
  python seedream_generator.py "Anime character" --num 3 --size 1024x1024
        """
    )
    
    parser.add_argument(
        "prompt",
        type=str,
        help="Text prompt for image generation"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output filename (without extension)"
    )
    parser.add_argument(
        "--size", "-s",
        type=str,
        default="2K",
        help="Image size: 1K, 2K, 1024x1024, 1280x720, etc. (default: 2K)"
    )
    parser.add_argument(
        "--num", "-n",
        type=int,
        default=1,
        help="Number of images to generate (default: 1)"
    )
    parser.add_argument(
        "--watermark", "-w",
        action="store_true",
        help="Add watermark to generated images"
    )
    parser.add_argument(
        "--output-dir", "-d",
        type=str,
        default="generated_thumbnails",
        help="Output directory (default: generated_thumbnails)"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="Model/endpoint ID (default: ARK_MODEL_ID env or seedream-4-5-251128)"
    )
    
    args = parser.parse_args()
    
    model_to_use = args.model or os.getenv('ARK_MODEL_ID') or "seedream-4-5-251128"
    
    print("\n" + "="*80)
    print("🚀 SEEDREAM 4.5 IMAGE GENERATOR - BytePlus ModelArk")
    print("="*80)
    print(f"Prompt: {args.prompt}")
    print(f"Model: {model_to_use}")
    print(f"Size: {args.size}")
    print(f"Number of images: {args.num}")
    print(f"Watermark: {args.watermark}")
    print(f"Output directory: {args.output_dir}")
    print("="*80 + "\n")
    
    try:
        generator = SeedreamGenerator(
            model=args.model,
            output_dir=args.output_dir,
            size=args.size,
            watermark=args.watermark
        )
        
        if args.num == 1:
            result = generator.generate_image(
                prompt=args.prompt,
                filename=args.output
            )
            
            if result['success']:
                print("\n" + "="*80)
                print("🎉 SUCCESS!")
                print(f"Image saved to: {result['filepath']}")
                if result.get('url'):
                    print(f"URL: {result['url']}")
                print("="*80 + "\n")
            else:
                print("\n" + "="*80)
                print(f"❌ FAILED: {result.get('error')}")
                print("="*80 + "\n")
                exit(1)
        else:
            results = generator.generate_multiple(
                prompt=args.prompt,
                num_images=args.num,
                base_filename=args.output
            )
            
            successful = [r for r in results if r['success']]
            print("\n" + "="*80)
            print(f"🎉 Generated {len(successful)}/{args.num} images successfully!")
            for r in successful:
                print(f"   - {r['filepath']}")
            print("="*80 + "\n")
            
            if len(successful) == 0:
                exit(1)
                
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        exit(1)
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Install the SDK with: pip install byteplus-python-sdk-v2")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        exit(1)

