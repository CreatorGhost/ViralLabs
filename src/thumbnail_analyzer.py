"""
YouTube Thumbnail Analyzer using GPT-4 Vision
Downloads and analyzes thumbnails from top videos to create a winning thumbnail prompt
"""

import os
import asyncio
import base64
import requests
from typing import List, Dict, Optional
from pathlib import Path
from openai import AsyncOpenAI


class ThumbnailAnalyzer:
    """Analyzes YouTube thumbnails using GPT-4 Vision to generate winning thumbnail prompts."""
    
    def __init__(
        self,
        model: str = "gpt-5.1",
        temperature: float = 0.3,
        download_dir: str = "thumbnails"
    ):
        """
        Initialize the thumbnail analyzer.
        
        Args:
            model: Vision model to use (gpt-4o, gpt-4-turbo, gpt-4-vision-preview)
            temperature: Creativity level (lower = more factual)
            download_dir: Directory to save thumbnails
        """
        self.model = model
        self.temperature = temperature
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # Initialize async OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = AsyncOpenAI(api_key=api_key)
        
    def get_thumbnail_url(self, video_id: str, quality: str = "maxresdefault") -> str:
        """
        Get YouTube thumbnail URL.
        
        Args:
            video_id: YouTube video ID
            quality: Thumbnail quality (maxresdefault, hqdefault, mqdefault, sddefault)
            
        Returns:
            Thumbnail URL
        """
        # YouTube thumbnail URL format
        return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"
    
    def is_youtube_short(self, video: Dict) -> bool:
        """
        Check if a video is a YouTube Short (typically < 60 seconds).
        
        Args:
            video: Video metadata dict
            
        Returns:
            True if it's likely a Short
        """
        duration = video.get('duration', 0)
        # Shorts are typically 60 seconds or less
        return duration > 0 and duration <= 60
    
    def download_thumbnail(self, video_id: str, title: str) -> Optional[str]:
        """
        Download thumbnail for a video.
        
        Args:
            video_id: YouTube video ID
            title: Video title (for filename)
            
        Returns:
            Path to downloaded thumbnail or None if failed
        """
        # Try different quality levels
        qualities = ["maxresdefault", "hqdefault", "mqdefault", "sddefault"]
        
        for quality in qualities:
            url = self.get_thumbnail_url(video_id, quality)
            
            try:
                response = requests.get(url, timeout=10)
                
                # maxresdefault returns 404 for some videos, try next quality
                if response.status_code == 200:
                    # Clean filename
                    clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
                    filename = f"{video_id}_{clean_title}_{quality}.jpg"
                    filepath = self.download_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    return str(filepath)
                    
            except Exception as e:
                print(f"  ⚠️  Failed to download {quality} for {video_id}: {str(e)[:50]}")
                continue
        
        return None
    
    def encode_image_base64(self, image_path: str) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    async def analyze_single_thumbnail(
        self,
        video: Dict,
        thumbnail_path: str,
        index: int
    ) -> Dict:
        """
        Analyze a single thumbnail using GPT-4 Vision.
        
        Args:
            video: Video metadata
            thumbnail_path: Path to thumbnail image
            index: Index of the video (for display)
            
        Returns:
            Dict with analysis results
        """
        print(f"  🔍 [{index}] Analyzing: {video['title'][:60]}...")
        
        try:
            # Encode image
            base64_image = self.encode_image_base64(thumbnail_path)
            
            # Create detailed analysis prompt
            analysis_prompt = """You are an expert at analyzing YouTube thumbnails. Analyze this thumbnail in extreme detail.

CRITICAL INSTRUCTIONS:
1. IDENTIFY SPECIFIC NAMES:
   - If there are anime/manga characters → Name them specifically (e.g., "Naruto Uzumaki", "Goku", "Luffy")
   - If there are celebrities/public figures → Name them (e.g., "Elon Musk", "MrBeast")
   - If there are tech gadgets → Name the exact model (e.g., "iPhone 15 Pro Max", "MacBook Pro M3")
   - If there are game characters → Name them (e.g., "Master Chief", "Kratos")
   - If there are brand logos → Name the brands (e.g., "Apple", "Tesla", "OpenAI")

2. USE WEB KNOWLEDGE:
   - Use your training data to identify characters, products, and brands
   - Be as specific as possible with names and models
   - If you recognize something but aren't 100% sure, say "possibly [name]"

3. DETAILED ANALYSIS - Cover ALL of these aspects:

A) TEXT ELEMENTS:
   - Exact text shown (including capitalization, styling)
   - Font style (bold, outlined, shadow, 3D effect)
   - Text color and any gradients
   - Text placement (top, center, bottom, corners)
   - Text size relative to image (large, medium, small)
   - Any text effects (glow, shadow, outline, 3D)

B) MAIN SUBJECTS/PEOPLE:
   - Number of people/characters
   - Specific names if recognizable
   - Facial expressions (shocked, excited, serious, smiling, etc.)
   - Positioning (center, left, right)
   - Body language and gestures
   - What they're wearing or holding
   - Eye contact (looking at camera, away, at object)

C) VISUAL ELEMENTS:
   - Arrows (direction, color, style - solid/dashed)
   - Circles/highlights (what they're highlighting)
   - Icons or symbols (checkmarks, X's, stars, etc.)
   - Graphics/overlays (flames, explosions, sparkles, etc.)
   - Emojis used
   - Split screens or comparisons

D) COLOR SCHEME:
   - Primary colors (be specific: "bright red", "electric blue")
   - Background color/gradient
   - Contrast level (high/low)
   - Color psychology (red = urgency, blue = trust, etc.)

E) COMPOSITION:
   - Layout type (center focus, rule of thirds, split screen)
   - Depth (foreground, midground, background elements)
   - Visual hierarchy (what draws attention first)
   - Balance and symmetry

F) EMOTIONAL/PSYCHOLOGICAL TRIGGERS:
   - What emotion does it evoke? (curiosity, shock, excitement, FOMO)
   - Clickbait elements (if any)
   - Storytelling elements
   - Problem/solution indicators

G) TECHNICAL DETAILS:
   - Image quality (sharp, blurry, professional)
   - Lighting (bright, dark, dramatic)
   - Style (realistic, cartoon, anime, minimalist)

H) SPECIFIC OBJECTS/GADGETS:
   - List every identifiable object with specific names/models
   - Brand names visible
   - Product categories

Provide your analysis in a structured format covering all these points. Be extremely detailed and specific."""

            # Call GPT-4 Vision
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"  # High detail for better analysis
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=self.temperature
            )
            
            analysis = response.choices[0].message.content
            
            print(f"  ✅ [{index}] Analysis complete: {video['title'][:60]}")
            
            return {
                'video_id': video['video_id'],
                'title': video['title'],
                'channel': video['channel'],
                'views': video.get('views', 0),
                'thumbnail_path': thumbnail_path,
                'analysis': analysis,
                'success': True
            }
            
        except Exception as e:
            print(f"  ❌ [{index}] Analysis failed: {str(e)[:100]}")
            return {
                'video_id': video['video_id'],
                'title': video['title'],
                'thumbnail_path': thumbnail_path,
                'analysis': None,
                'success': False,
                'error': str(e)
            }
    
    async def analyze_thumbnails_parallel(
        self,
        videos: List[Dict]
    ) -> List[Dict]:
        """
        Analyze multiple thumbnails in parallel.
        
        Args:
            videos: List of video metadata dicts with thumbnail_path
            
        Returns:
            List of analysis results
        """
        print(f"\n🔬 Analyzing {len(videos)} thumbnails in parallel...")
        print(f"⚡ Using {self.model} with async processing\n")
        
        # Create tasks for parallel execution
        tasks = [
            self.analyze_single_thumbnail(video, video['thumbnail_path'], i+1)
            for i, video in enumerate(videos)
        ]
        
        # Run all analyses in parallel
        results = await asyncio.gather(*tasks)
        
        successful = sum(1 for r in results if r['success'])
        print(f"\n✅ Successfully analyzed {successful}/{len(videos)} thumbnails\n")
        
        return results
    
    async def generate_thumbnail_prompt(
        self,
        analyses: List[Dict],
        original_topic: str
    ) -> str:
        """
        Generate a comprehensive thumbnail creation prompt based on all analyses.
        
        Args:
            analyses: List of thumbnail analysis results
            original_topic: The original video topic
            
        Returns:
            Final thumbnail generation prompt
        """
        print("🎨 Synthesizing analyses into thumbnail generation prompt...")
        
        # Filter successful analyses
        successful_analyses = [a for a in analyses if a['success']]
        
        if not successful_analyses:
            return "No successful thumbnail analyses to synthesize."
        
        # Combine all analyses
        combined_analyses = "\n\n".join([
            f"=== THUMBNAIL {i+1}: {a['title']} ===\n"
            f"Channel: {a['channel']}\n"
            f"Views: {a.get('views', 0):,}\n"
            f"ANALYSIS:\n{a['analysis']}"
            for i, a in enumerate(successful_analyses)
        ])
        
        # Create synthesis prompt
        synthesis_prompt = f"""You are a creative director and expert thumbnail designer who has studied {len(successful_analyses)} high-performing YouTube thumbnails on the topic: "{original_topic}".

Below are the detailed analyses of each successful thumbnail:

{combined_analyses}

═══════════════════════════════════════════════════════════════════════════════
YOUR TASK: CREATE AN IMPROVED, MORE APPEALING THUMBNAIL PROMPT
═══════════════════════════════════════════════════════════════════════════════

IMPORTANT: Do NOT just describe what you see in these thumbnails. Instead:
1. LEARN from the patterns and successful elements
2. USE CREATIVITY to design something NEW and MORE APPEALING
3. COMBINE the best elements in an innovative way
4. ENHANCE the emotional impact and click-worthiness

ANALYSIS PHASE (in your mind):

1. IDENTIFY WINNING PATTERNS:
   - What visual styles work? (anime art, realistic photos, split screens, collages)
   - What text strategies grab attention? (bold statements, questions, numbers)
   - What colors create contrast and stand out?
   - What facial expressions or character poses work?
   - What composition layouts are most effective?
   - What specific characters/brands/products appear?

2. FIND THE EMOTIONAL HOOKS:
   - What makes people curious? (mystery, controversy, comparison)
   - What creates urgency? (FOMO, exclusivity, trending)
   - What triggers excitement? (hype, best of, top tier)
   - What sparks debate? (rankings, hot takes, vs. comparisons)

CREATIVE SYNTHESIS PHASE (your output):

Now CREATE a NEW thumbnail design that:
- Takes the BEST elements from these {len(successful_analyses)} thumbnails
- AMPLIFIES the emotional appeal
- INCREASES the click-worthiness
- Adds CREATIVE IMPROVEMENTS (better composition, bolder text, more dynamic)
- Makes it MORE VISUALLY STRIKING than the originals

GUIDELINES FOR YOUR CREATIVE OUTPUT:

1. BE SPECIFIC WITH NAMES:
   - Use exact character names (e.g., "Goku in Super Saiyan form", "Naruto", "Luffy")
   - Use exact product names (e.g., "iPhone 15 Pro Max", "PS5")
   - Use exact brand names (e.g., "Tesla Cybertruck", "Apple Vision Pro")

2. ENHANCE THE COMPOSITION:
   - If originals use centered subjects → consider dynamic angles or rule of thirds
   - If originals use faces → suggest more expressive emotions or dramatic poses
   - If originals use split screens → make the contrast more striking
   - Add depth and layers (foreground, midground, background)

3. AMPLIFY THE TEXT:
   - Make it BOLDER and more attention-grabbing
   - Use power words (BEST, ULTIMATE, INSANE, SHOCKING, SECRET)
   - Create curiosity gaps ("You Won't Believe #3", "This Changed Everything")
   - Ensure maximum readability with strong contrast

4. OPTIMIZE COLORS:
   - Use high-contrast combinations (yellow on black, white on red, etc.)
   - Create visual pop with complementary colors
   - Add gradients or glows for depth
   - Make it stand out in a feed of gray/muted thumbnails

5. ADD EMOTIONAL AMPLIFIERS:
   - Exaggerated expressions (shock, excitement, confusion)
   - Dynamic action poses or movements
   - Visual tension (vs., arrows pointing, circles highlighting)
   - Elements that trigger FOMO or curiosity

6. MAKE IT SCROLL-STOPPING:
   - High contrast that pops on small screens
   - Clear visual hierarchy (what to look at first, second, third)
   - Intriguing elements that make people pause
   - Professional polish with clean edges and spacing

FORMAT YOUR OUTPUT:

Write a detailed, creative prompt that starts with: "Create a YouTube thumbnail featuring..."

Include EVERYTHING in vivid detail:
- Exact composition and layout
- Specific characters/products/brands by name
- Detailed text overlay (exact wording, style, effects, placement)
- Precise color scheme and gradients
- All visual elements (arrows, circles, icons, effects)
- Emotional tone and energy level
- Art style (photorealistic, anime-style, digital art, etc.)
- Lighting and atmosphere

Make it SO DETAILED that an AI image generator can create exactly what you envision.
Make it SO APPEALING that it's BETTER than the originals you analyzed.

OUTPUT ONLY THE FINAL CREATIVE PROMPT - NO PREAMBLE, NO EXPLANATION.

THUMBNAIL GENERATION PROMPT:"""

        # Generate final prompt
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": synthesis_prompt
                }
            ],
            max_tokens=2000,
            temperature=0.7  # Higher temperature for creative synthesis
        )
        
        final_prompt = response.choices[0].message.content.strip()
        
        print("✅ Thumbnail generation prompt created!\n")
        
        return final_prompt
    
    async def generate_multiple_thumbnail_prompts(
        self,
        analyses: List[Dict],
        original_topic: str,
        num_prompts: int = 3
    ) -> List[str]:
        """
        Generate multiple varied creative prompts from the same analysis.
        
        Args:
            analyses: List of thumbnail analysis results
            original_topic: The original video topic
            num_prompts: Number of different prompts to generate
            
        Returns:
            List of different creative prompts
        """
        print(f"🎨 Generating {num_prompts} different creative prompts from analysis...")
        
        # Filter successful analyses
        successful_analyses = [a for a in analyses if a['success']]
        
        if not successful_analyses:
            return ["No successful thumbnail analyses to synthesize."] * num_prompts
        
        # Combine all analyses
        combined_analyses = "\n\n".join([
            f"=== THUMBNAIL {i+1}: {a['title']} ===\n"
            f"Channel: {a['channel']}\n"
            f"Views: {a.get('views', 0):,}\n"
            f"ANALYSIS:\n{a['analysis']}"
            for i, a in enumerate(successful_analyses)
        ])
        
        # Create prompts with different creative focuses
        variation_focuses = [
            "Focus on BOLD TEXT and HIGH CONTRAST colors for maximum attention",
            "Focus on DYNAMIC COMPOSITION and DRAMATIC CHARACTER POSES for visual impact",
            "Focus on EMOTIONAL EXPRESSION and CURIOSITY-TRIGGERING ELEMENTS for engagement",
            "Focus on CLEAN PROFESSIONAL DESIGN with STRIKING VISUAL HIERARCHY",
            "Focus on ENERGETIC COLORS and MOVEMENT to create excitement"
        ]
        
        # Generate each prompt in parallel
        tasks = []
        for i in range(num_prompts):
            focus = variation_focuses[i % len(variation_focuses)]
            synthesis_prompt = self._create_synthesis_prompt(
                combined_analyses, 
                original_topic, 
                len(successful_analyses),
                variation_number=i+1,
                creative_focus=focus
            )
            tasks.append(self._generate_single_prompt(synthesis_prompt))
        
        prompts = await asyncio.gather(*tasks)
        
        print(f"✅ Generated {len(prompts)} different creative prompts!\n")
        
        return prompts
    
    async def _generate_single_prompt(self, synthesis_prompt: str) -> str:
        """Generate a single prompt from synthesis prompt."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": synthesis_prompt
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    
    def _create_synthesis_prompt(
        self, 
        combined_analyses: str, 
        original_topic: str, 
        num_analyses: int,
        variation_number: int = 1,
        creative_focus: str = ""
    ) -> str:
        """Create the synthesis prompt with optional variation focus."""
        
        return f"""You are a creative director and expert thumbnail designer who has studied {num_analyses} high-performing YouTube thumbnails on the topic: "{original_topic}".

Below are the detailed analyses of each successful thumbnail:

{combined_analyses}

═══════════════════════════════════════════════════════════════════════════════
YOUR TASK: CREATE AN IMPROVED, MORE APPEALING THUMBNAIL PROMPT (VARIATION #{variation_number})
═══════════════════════════════════════════════════════════════════════════════

CREATIVE FOCUS FOR THIS VARIATION: {creative_focus}

IMPORTANT: Do NOT just describe what you see in these thumbnails. Instead:
1. LEARN from the patterns and successful elements
2. USE CREATIVITY to design something NEW and MORE APPEALING
3. COMBINE the best elements in an innovative way
4. ENHANCE the emotional impact and click-worthiness

ANALYSIS PHASE (in your mind):

1. IDENTIFY WINNING PATTERNS:
   - What visual styles work? (anime art, realistic photos, split screens, collages)
   - What text strategies grab attention? (bold statements, questions, numbers)
   - What colors create contrast and stand out?
   - What facial expressions or character poses work?
   - What composition layouts are most effective?
   - What specific characters/brands/products appear?

2. FIND THE EMOTIONAL HOOKS:
   - What makes people curious? (mystery, controversy, comparison)
   - What creates urgency? (FOMO, exclusivity, trending)
   - What triggers excitement? (hype, best of, top tier)
   - What sparks debate? (rankings, hot takes, vs. comparisons)

CREATIVE SYNTHESIS PHASE (your output):

Now CREATE a NEW thumbnail design that:
- Takes the BEST elements from these {num_analyses} thumbnails
- AMPLIFIES the emotional appeal
- INCREASES the click-worthiness
- Adds CREATIVE IMPROVEMENTS (better composition, bolder text, more dynamic)
- Makes it MORE VISUALLY STRIKING than the originals
- Applies the CREATIVE FOCUS mentioned above

GUIDELINES FOR YOUR CREATIVE OUTPUT:

1. BE SPECIFIC WITH NAMES:
   - Use exact character names (e.g., "Goku in Super Saiyan form", "Naruto", "Luffy")
   - Use exact product names (e.g., "iPhone 15 Pro Max", "PS5")
   - Use exact brand names (e.g., "Tesla Cybertruck", "Apple Vision Pro")

2. ENHANCE THE COMPOSITION:
   - If originals use centered subjects → consider dynamic angles or rule of thirds
   - If originals use faces → suggest more expressive emotions or dramatic poses
   - If originals use split screens → make the contrast more striking
   - Add depth and layers (foreground, midground, background)

3. AMPLIFY THE TEXT:
   - Make it BOLDER and more attention-grabbing
   - Use power words (BEST, ULTIMATE, INSANE, SHOCKING, SECRET)
   - Create curiosity gaps ("You Won't Believe #3", "This Changed Everything")
   - Ensure maximum readability with strong contrast

4. OPTIMIZE COLORS:
   - Use high-contrast combinations (yellow on black, white on red, etc.)
   - Create visual pop with complementary colors
   - Add gradients or glows for depth
   - Make it stand out in a feed of gray/muted thumbnails

5. ADD EMOTIONAL AMPLIFIERS:
   - Exaggerated expressions (shock, excitement, confusion)
   - Dynamic action poses or movements
   - Visual tension (vs., arrows pointing, circles highlighting)
   - Elements that trigger FOMO or curiosity

6. MAKE IT SCROLL-STOPPING:
   - High contrast that pops on small screens
   - Clear visual hierarchy (what to look at first, second, third)
   - Intriguing elements that make people pause
   - Professional polish with clean edges and spacing

FORMAT YOUR OUTPUT:

Write a detailed, creative prompt that starts with: "Create a YouTube thumbnail featuring..."

Include EVERYTHING in vivid detail:
- Exact composition and layout
- Specific characters/products/brands by name
- Detailed text overlay (exact wording, style, effects, placement)
- Precise color scheme and gradients
- All visual elements (arrows, circles, icons, effects)
- Emotional tone and energy level
- Art style (photorealistic, anime-style, digital art, etc.)
- Lighting and atmosphere

Make it SO DETAILED that an AI image generator can create exactly what you envision.
Make it SO APPEALING that it's BETTER than the originals you analyzed.
Make this variation DIFFERENT from other variations (apply the creative focus above).

OUTPUT ONLY THE FINAL CREATIVE PROMPT - NO PREAMBLE, NO EXPLANATION.

THUMBNAIL GENERATION PROMPT:"""
    
    async def analyze_and_generate_prompt_async(
        self,
        videos: List[Dict],
        original_topic: str,
        top_n: int = 5
    ) -> Dict:
        """
        Complete async pipeline: download, analyze, and generate prompt.
        
        Args:
            videos: List of video metadata (must have video_id, title, duration)
            original_topic: Original search topic
            top_n: Number of videos to analyze (default: 5)
            
        Returns:
            Dict with thumbnail_prompt, analyses, and metadata
        """
        print("\n" + "="*80)
        print("🎨 THUMBNAIL ANALYZER - GPT-4 VISION PIPELINE")
        print("="*80)
        print(f"Topic: {original_topic}")
        print(f"Videos to analyze: {top_n}")
        print(f"Vision Model: {self.model}")
        print("="*80 + "\n")
        
        # Step 1: Filter out Shorts and select top N
        print("📊 Step 1: Filtering videos...")
        regular_videos = [v for v in videos if not self.is_youtube_short(v)]
        
        shorts_count = len(videos) - len(regular_videos)
        if shorts_count > 0:
            print(f"  ⏭️  Skipped {shorts_count} YouTube Short(s)")
        
        if len(regular_videos) < top_n:
            print(f"  ⚠️  Only {len(regular_videos)} regular videos available (requested {top_n})")
            top_n = len(regular_videos)
        
        selected_videos = regular_videos[:top_n]
        print(f"  ✅ Selected {len(selected_videos)} videos for analysis\n")
        
        # Step 2: Download thumbnails
        print(f"📥 Step 2: Downloading {len(selected_videos)} thumbnails...")
        videos_with_thumbnails = []
        
        for i, video in enumerate(selected_videos, 1):
            print(f"  [{i}/{len(selected_videos)}] Downloading: {video['title'][:60]}...")
            thumbnail_path = self.download_thumbnail(video['video_id'], video['title'])
            
            if thumbnail_path:
                video['thumbnail_path'] = thumbnail_path
                videos_with_thumbnails.append(video)
                print(f"  ✅ Downloaded: {thumbnail_path}")
            else:
                print("  ❌ Failed to download thumbnail")
        
        print(f"\n✅ Downloaded {len(videos_with_thumbnails)}/{len(selected_videos)} thumbnails\n")
        
        if not videos_with_thumbnails:
            return {
                'success': False,
                'error': 'No thumbnails could be downloaded',
                'thumbnail_prompt': None,
                'analyses': []
            }
        
        # Step 3: Analyze thumbnails in parallel
        print("="*80)
        print("🔬 Step 3: Analyzing thumbnails with GPT-4 Vision")
        print("="*80)
        analyses = await self.analyze_thumbnails_parallel(videos_with_thumbnails)
        
        # Step 4: Generate final prompt
        print("="*80)
        print("🎯 Step 4: Generating thumbnail creation prompt")
        print("="*80)
        final_prompt = await self.generate_thumbnail_prompt(analyses, original_topic)
        
        # Summary
        successful_analyses = [a for a in analyses if a['success']]
        
        print("\n" + "="*80)
        print("✅ THUMBNAIL ANALYSIS COMPLETE")
        print("="*80)
        print(f"Videos Analyzed: {len(successful_analyses)}/{len(selected_videos)}")
        print(f"Thumbnails Downloaded: {len(videos_with_thumbnails)}")
        print(f"Successful Analyses: {len(successful_analyses)}")
        print("="*80 + "\n")
        
        return {
            'success': True,
            'thumbnail_prompt': final_prompt,
            'analyses': analyses,
            'metadata': {
                'topic': original_topic,
                'videos_analyzed': len(successful_analyses),
                'thumbnails_downloaded': len(videos_with_thumbnails),
                'total_videos': len(selected_videos),
                'shorts_filtered': shorts_count
            }
        }
    
    def analyze_and_generate_prompt(
        self,
        videos: List[Dict],
        original_topic: str,
        top_n: int = 5
    ) -> Dict:
        """
        Synchronous wrapper for the async pipeline.
        
        Args:
            videos: List of video metadata
            original_topic: Original search topic
            top_n: Number of videos to analyze
            
        Returns:
            Dict with thumbnail_prompt, analyses, and metadata
        """
        return asyncio.run(
            self.analyze_and_generate_prompt_async(videos, original_topic, top_n)
        )


# ===== Convenience Function =====

def analyze_thumbnails(
    videos: List[Dict],
    topic: str,
    top_n: int = 5,
    model: str = "gpt-4o"
) -> Dict:
    """
    Quick function to analyze thumbnails and get generation prompt.
    
    Args:
        videos: List of video metadata (from VideoFetcher)
        topic: Video topic
        top_n: Number of thumbnails to analyze (default: 5)
        model: Vision model to use (default: gpt-4o)
        
    Returns:
        Dict with thumbnail_prompt and analyses
        
    Example:
        >>> from src.video_fetcher import VideoFetcher
        >>> from src.thumbnail_analyzer import analyze_thumbnails
        >>> 
        >>> fetcher = VideoFetcher()
        >>> videos = fetcher.search_videos("python tutorial", max_results=10)
        >>> result = analyze_thumbnails(videos, "python tutorial", top_n=5)
        >>> print(result['thumbnail_prompt'])
    """
    analyzer = ThumbnailAnalyzer(model=model)
    return analyzer.analyze_and_generate_prompt(videos, topic, top_n)

