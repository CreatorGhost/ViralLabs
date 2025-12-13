"""
YouTube Thumbnail Prompt Enhancer
Transforms simple video titles into optimized prompts for image generation.

This module uses an LLM to enhance basic prompts into detailed, 
YouTube-thumbnail-optimized prompts that work well with image generators
like Seedream and Gemini.
"""

import os
from typing import Optional, Dict
from pathlib import Path

# Load .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


# ============================================
# PROMPT TEMPLATES
# ============================================

THUMBNAIL_SYSTEM_PROMPT = """You are a YouTube thumbnail prompt expert. Your job is to transform simple video titles into detailed, optimized prompts for AI image generation.

## YOUR TASK
Take the user's video title and create a compelling image generation prompt that will produce a clickable, engaging YouTube thumbnail.

## KEY PRINCIPLES FOR YOUTUBE THUMBNAILS

### Visual Elements:
- Bold, high-contrast colors that pop
- Clear focal point (usually a face or main subject)
- Dynamic poses and expressions (shock, excitement, curiosity)
- Professional lighting with dramatic effects
- Clean, uncluttered composition

### Text Guidelines:
- If text is needed, keep it SHORT (2-4 words max)
- Use BOLD, easy-to-read fonts
- Position text to not cover faces
- Common text styles: outlined, shadowed, 3D effect
- Text should create urgency or curiosity

### Composition Tips:
- Rule of thirds for subject placement
- Leave space for text if needed
- Face takes up 30-50% of frame for reaction thumbnails
- Use visual hierarchy (biggest = most important)

### Style Considerations:
- Vibrant, saturated colors
- High contrast between elements
- Professional but eye-catching
- Match the video's tone (funny, serious, educational, etc.)

## OUTPUT FORMAT
Return ONLY the enhanced prompt - no explanations, no markdown, no quotes.
The prompt should be 2-4 sentences that paint a vivid picture for the AI.

## EXAMPLES

Input: "How to make $10000 in a week"
Output: A shocked young entrepreneur in business casual pointing at floating green dollar bills and gold coins, with bold white text "10K/WEEK" with gold outline, dramatic lighting from below, dark gradient background with money rain effect, ultra realistic, 4K quality

Input: "iPhone 15 vs Samsung Galaxy - Which is Better?"
Output: Split-screen composition with iPhone 15 on left in blue glow and Samsung Galaxy on right in red glow, VS symbol with lightning bolts in center, phones floating with dramatic reflections, dark tech-style background with circuit patterns, bold text "WHO WINS?" at bottom, cinematic lighting

Input: "I Survived 100 Days in Minecraft Hardcore"
Output: Epic Minecraft scene with player character standing victorious on mountain peak at sunset, zombie horde below, bold red text "100 DAYS" with fire effect, dramatic clouds and god rays, pixel art style blended with cinematic lighting, survival gear visible

Input: "Best Pizza Recipe Ever"
Output: Steaming hot pepperoni pizza being pulled apart with cheese stretch, chef's hands visible, warm golden lighting, rustic wooden table background, bold yellow text "BEST EVER" with Italian flag accent, close-up food photography style, mouth-watering presentation

Input: "Goku vs Vegeta Epic Battle"
Output: Goku in orange gi and Vegeta in blue armor clashing fists with explosive energy burst between them, dynamic action poses, anime style with speed lines, bold text "ULTIMATE BATTLE" with energy glow effect, dramatic lighting with ki auras"""


SIMPLE_ENHANCEMENT_TEMPLATE = """Transform this video title into an optimized YouTube thumbnail prompt:

Title: "{title}"

Additional context (if any): {context}

Remember:
- Describe the visual scene in detail
- Include text that should appear on the thumbnail (keep it 2-4 words)
- Specify colors, lighting, and style
- Make it eye-catching and clickable

Enhanced prompt:"""


# ============================================
# PROMPT ENHANCER CLASS
# ============================================

class PromptEnhancer:
    """
    Enhances simple prompts into optimized YouTube thumbnail prompts.
    
    Uses LLM (OpenAI or Gemini) to transform basic titles into detailed,
    professional prompts for image generation.
    """
    
    def __init__(self, provider: str = "auto"):
        """
        Initialize the prompt enhancer.
        
        Args:
            provider: LLM provider - "openai", "gemini", or "auto" (tries both)
        """
        self.provider = provider
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize the LLM client based on available API keys."""
        if self.provider == "auto":
            # Try OpenAI first, then Gemini
            if os.getenv("OPENAI_API_KEY"):
                self.provider = "openai"
            elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                self.provider = "gemini"
            else:
                print("⚠️ No LLM API key found. Using template-based enhancement.")
                self.provider = "template"
                return
        
        if self.provider == "openai":
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                print("✅ PromptEnhancer using OpenAI")
            except Exception as e:
                print(f"⚠️ Failed to init OpenAI: {e}. Falling back to template.")
                self.provider = "template"
                
        elif self.provider == "gemini":
            try:
                from google import genai
                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                self._client = genai.Client(api_key=api_key)
                print("✅ PromptEnhancer using Gemini")
            except Exception as e:
                print(f"⚠️ Failed to init Gemini: {e}. Falling back to template.")
                self.provider = "template"
    
    def enhance(
        self,
        title: str,
        context: Optional[str] = None,
        style: str = "auto",
        include_text: bool = True,
        text_content: Optional[str] = None
    ) -> str:
        """
        Enhance a simple title into an optimized thumbnail prompt.
        
        Args:
            title: The video title or simple description
            context: Additional context about the video
            style: Visual style hint ("gaming", "tech", "lifestyle", "educational", "auto")
            include_text: Whether to include text overlay in the thumbnail
            text_content: Specific text to include (if different from auto-generated)
            
        Returns:
            Enhanced prompt optimized for thumbnail generation
        """
        print(f"\n🎨 Enhancing prompt for: '{title}'")
        
        if self.provider == "template":
            return self._template_enhance(title, context, style, include_text, text_content)
        elif self.provider == "openai":
            return self._openai_enhance(title, context, style, include_text, text_content)
        elif self.provider == "gemini":
            return self._gemini_enhance(title, context, style, include_text, text_content)
        else:
            return self._template_enhance(title, context, style, include_text, text_content)
    
    def _openai_enhance(
        self, title: str, context: Optional[str], 
        style: str, include_text: bool, text_content: Optional[str]
    ) -> str:
        """Enhance using OpenAI."""
        try:
            user_prompt = f"Video Title: {title}"
            if context:
                user_prompt += f"\nContext: {context}"
            if style != "auto":
                user_prompt += f"\nStyle: {style}"
            if not include_text:
                user_prompt += "\nNote: Do NOT include any text overlay in the thumbnail."
            elif text_content:
                user_prompt += f"\nText to include: {text_content}"
            
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": THUMBNAIL_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            enhanced = response.choices[0].message.content.strip()
            print(f"✅ Enhanced prompt generated ({len(enhanced)} chars)")
            return enhanced
            
        except Exception as e:
            print(f"⚠️ OpenAI enhancement failed: {e}. Using template.")
            return self._template_enhance(title, context, style, include_text, text_content)
    
    def _gemini_enhance(
        self, title: str, context: Optional[str],
        style: str, include_text: bool, text_content: Optional[str]
    ) -> str:
        """Enhance using Gemini."""
        try:
            user_prompt = f"Video Title: {title}"
            if context:
                user_prompt += f"\nContext: {context}"
            if style != "auto":
                user_prompt += f"\nStyle: {style}"
            if not include_text:
                user_prompt += "\nNote: Do NOT include any text overlay in the thumbnail."
            elif text_content:
                user_prompt += f"\nText to include: {text_content}"
            
            full_prompt = f"{THUMBNAIL_SYSTEM_PROMPT}\n\n{user_prompt}"
            
            response = self._client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            
            enhanced = response.text.strip()
            print(f"✅ Enhanced prompt generated ({len(enhanced)} chars)")
            return enhanced
            
        except Exception as e:
            print(f"⚠️ Gemini enhancement failed: {e}. Using template.")
            return self._template_enhance(title, context, style, include_text, text_content)
    
    def _template_enhance(
        self, title: str, context: Optional[str],
        style: str, include_text: bool, text_content: Optional[str]
    ) -> str:
        """Template-based enhancement (no LLM required)."""
        
        # Detect style from title if auto
        if style == "auto":
            title_lower = title.lower()
            if any(w in title_lower for w in ["game", "minecraft", "fortnite", "gta", "gaming"]):
                style = "gaming"
            elif any(w in title_lower for w in ["phone", "iphone", "android", "tech", "review", "laptop"]):
                style = "tech"
            elif any(w in title_lower for w in ["recipe", "cook", "food", "eat", "pizza", "burger"]):
                style = "food"
            elif any(w in title_lower for w in ["vs", "versus", "battle", "fight", "who wins"]):
                style = "versus"
            elif any(w in title_lower for w in ["anime", "goku", "naruto", "dragon ball", "one piece"]):
                style = "anime"
            elif any(w in title_lower for w in ["money", "$", "rich", "income", "passive"]):
                style = "money"
            else:
                style = "general"
        
        # Style-specific templates
        style_templates = {
            "gaming": f"""Epic gaming scene depicting "{title}", dramatic lighting with neon accents, 
dynamic action pose, bold text "{self._extract_key_text(title, text_content)}" with glowing outline, 
dark background with particle effects, cinematic composition, 4K quality, gaming aesthetic""",
            
            "tech": f"""Clean tech presentation for "{title}", modern gradient background with 
subtle tech patterns, product in spotlight with reflections, bold minimalist text 
"{self._extract_key_text(title, text_content)}", professional lighting, sleek and premium feel""",
            
            "food": f"""Mouth-watering food photography for "{title}", warm golden lighting, 
steam rising, close-up with shallow depth of field, rustic wooden elements, 
text "{self._extract_key_text(title, text_content)}" in appetizing colors, delicious presentation""",
            
            "versus": f"""Epic split-screen battle composition for "{title}", 
dramatic VS symbol with energy effects in center, opposing elements on each side with 
contrasting color schemes (blue vs red), bold text "{self._extract_key_text(title, text_content)}" 
with impact effect, cinematic lighting, high contrast""",
            
            "anime": f"""Dynamic anime-style illustration for "{title}", 
vibrant colors with speed lines and energy effects, dramatic poses, 
bold stylized text "{self._extract_key_text(title, text_content)}" with anime aesthetic, 
action-packed composition, high quality anime art style""",
            
            "money": f"""Eye-catching wealth visualization for "{title}", 
floating money/gold elements, confident person pointing or celebrating, 
bold green/gold text "{self._extract_key_text(title, text_content)}", 
dramatic lighting from below, aspirational and professional vibe""",
            
            "general": f"""Professional YouTube thumbnail for "{title}", 
bold and eye-catching composition, high contrast colors, 
clear focal point with dramatic lighting, 
text "{self._extract_key_text(title, text_content)}" with outline for readability, 
clean background that doesn't distract, click-worthy presentation"""
        }
        
        enhanced = style_templates.get(style, style_templates["general"])
        
        if context:
            enhanced += f" Context: {context}."
        
        if not include_text:
            # Remove text references
            enhanced = enhanced.replace(f'text "{self._extract_key_text(title, text_content)}"', "")
            enhanced = enhanced.replace("bold text", "")
            enhanced = enhanced.replace("with outline for readability,", "")
        
        print(f"✅ Template-enhanced prompt generated ({len(enhanced)} chars)")
        return enhanced.strip()
    
    def _extract_key_text(self, title: str, text_content: Optional[str] = None) -> str:
        """Extract or generate key text for thumbnail overlay."""
        if text_content:
            return text_content.upper()
        
        # Extract key words (usually 2-4 words)
        title_upper = title.upper()
        
        # Common patterns to extract
        patterns = [
            # Numbers and money
            (r'\$[\d,]+', lambda m: m.group()),
            (r'\d+K|\d+ DAYS|\d+ HOURS', lambda m: m.group()),
            # VS battles
            (r'VS\.?|VERSUS', lambda m: "VS"),
            # Questions
            (r'WHO WINS\??', lambda m: "WHO WINS?"),
            (r'WHICH IS BETTER\??', lambda m: "WHICH IS BETTER?"),
        ]
        
        import re
        for pattern, extractor in patterns:
            match = re.search(pattern, title_upper)
            if match:
                return extractor(match)
        
        # Default: first 2-3 significant words
        words = [w for w in title.split() if len(w) > 2 and w.lower() not in 
                 ['the', 'and', 'for', 'how', 'what', 'why', 'when', 'this', 'that', 'with']]
        
        if len(words) >= 2:
            return ' '.join(words[:2]).upper()
        elif words:
            return words[0].upper()
        else:
            return title[:15].upper()


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

# Global enhancer instance
_enhancer: Optional[PromptEnhancer] = None

def get_enhancer() -> PromptEnhancer:
    """Get or create the global prompt enhancer."""
    global _enhancer
    if _enhancer is None:
        _enhancer = PromptEnhancer()
    return _enhancer


def enhance_prompt(
    title: str,
    context: Optional[str] = None,
    style: str = "auto",
    include_text: bool = True,
    text_content: Optional[str] = None
) -> str:
    """
    Quick function to enhance a prompt.
    
    Args:
        title: Video title or simple description
        context: Additional context
        style: Visual style hint
        include_text: Whether to include text overlay
        text_content: Specific text to show
        
    Returns:
        Enhanced prompt for image generation
    """
    return get_enhancer().enhance(
        title=title,
        context=context,
        style=style,
        include_text=include_text,
        text_content=text_content
    )


def enhance_for_seedream(title: str, text_overlay: Optional[str] = None) -> str:
    """
    Enhance prompt specifically optimized for Seedream.
    
    Seedream renders text literally, so this function creates
    prompts that take advantage of that capability.
    
    Args:
        title: Video title
        text_overlay: Specific text to show on thumbnail
        
    Returns:
        Seedream-optimized prompt
    """
    enhancer = get_enhancer()
    
    # Get base enhanced prompt
    enhanced = enhancer.enhance(
        title=title,
        include_text=True,
        text_content=text_overlay
    )
    
    # Add Seedream-specific optimizations
    seedream_suffix = ", ultra high quality, professional YouTube thumbnail, 16:9 aspect ratio, vibrant colors, high contrast"
    
    return enhanced + seedream_suffix


# ============================================
# CLI TESTING
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhance prompts for YouTube thumbnails")
    parser.add_argument("title", type=str, help="Video title to enhance")
    parser.add_argument("--context", "-c", type=str, help="Additional context")
    parser.add_argument("--style", "-s", type=str, default="auto",
                       choices=["auto", "gaming", "tech", "food", "versus", "anime", "money", "general"])
    parser.add_argument("--no-text", action="store_true", help="Don't include text overlay")
    parser.add_argument("--text", "-t", type=str, help="Specific text to show")
    parser.add_argument("--provider", "-p", type=str, default="auto",
                       choices=["auto", "openai", "gemini", "template"])
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🎨 YOUTUBE THUMBNAIL PROMPT ENHANCER")
    print("="*80)
    print(f"Title: {args.title}")
    print(f"Style: {args.style}")
    print(f"Provider: {args.provider}")
    print("="*80 + "\n")
    
    enhancer = PromptEnhancer(provider=args.provider)
    
    enhanced = enhancer.enhance(
        title=args.title,
        context=args.context,
        style=args.style,
        include_text=not args.no_text,
        text_content=args.text
    )
    
    print("\n" + "="*80)
    print("📝 ENHANCED PROMPT:")
    print("="*80)
    print(enhanced)
    print("="*80 + "\n")

