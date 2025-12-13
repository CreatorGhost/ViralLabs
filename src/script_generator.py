"""
YouTube Script Generator using LangChain LCEL (2025 Best Practices)
Integrates with existing video_fetcher and transcript_scraper
"""

from typing import Dict, List
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from .video_fetcher import VideoFetcher
from .transcript_scraper import TranscriptScraper


class ScriptGeneratorPipeline:
    """
    Complete LangChain pipeline for YouTube script generation.
    
    Pipeline Flow:
    1. User Query → Query Refinement (LLM)
    2. Refined Query → YouTube Research (Phase 1 code)
    3. Transcripts → Script Generation (LLM)
    """
    
    def __init__(
        self,
        model: str = "gpt-5.1",
        refine_model: str = "gpt-5-nano",
        temperature: float = 0.7,
        subscriber_threshold: int = 50000,
        max_workers: int = 5,
        max_videos: int = 15,
        top_n_videos: int = 7
    ):
        """
        Initialize the script generator pipeline.
        
        Args:
            model: OpenAI model for script generation (gpt-5.1, gpt-5-mini, gpt-5-nano)
            refine_model: Cheaper model for query refinement (gpt-5-nano recommended)
            temperature: LLM creativity (0-1, higher = more creative)
            subscriber_threshold: Minimum subscribers for video selection
            max_workers: Parallel workers for fetching
            max_videos: Maximum videos to search
            top_n_videos: Top N videos to fetch transcripts for
        """
        # Initialize LLMs (different models for different tasks)
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        # Note: Some models (like gpt-5-nano) only support default temperature
        self.refine_llm = ChatOpenAI(model=refine_model)  # Use default temp for refinement
        
        # Initialize YouTube components
        self.video_fetcher = VideoFetcher(
            subscriber_threshold=subscriber_threshold,
            max_workers=max_workers
        )
        self.transcript_scraper = TranscriptScraper()
        
        # Configuration
        self.max_videos = max_videos
        self.top_n_videos = top_n_videos
        
        # Build LCEL chains
        self._build_chains()
    
    def _build_chains(self):
        """Build all LangChain LCEL chains."""
        
        # ===== CHAIN 1: Query Refinement =====
        self.refine_prompt = ChatPromptTemplate.from_template("""
You are a YouTube search query optimizer with deep understanding of YouTube's algorithm.

CURRENT DATE: {current_date}
CURRENT YEAR: {current_year}
NEXT YEAR: {next_year}

USER'S ORIGINAL QUERY: {user_query}

Your task: Transform this into an optimized YouTube search query that will find the most relevant, high-quality videos.

CRITICAL RULES:
1. Keep the user's original intent and scope (don't narrow down broad queries)
2. Remove filler words ("I want to", "help me", "stuff", etc.)
3. Make it 3-8 words maximum
4. Use keywords that appear in successful YouTube video titles
5. DO NOT assume specifics not mentioned (e.g., "programming" ≠ "python")

DATE HANDLING (IMPORTANT):
- Only add dates when contextually relevant
- For "upcoming/future" queries → use NEXT YEAR (e.g., "upcoming anime" → "upcoming anime {next_year}")
- For "latest/current/trending" queries → use CURRENT YEAR (e.g., "latest tech trends" → "tech trends {current_year}")
- For "best/old/classic/history" queries → NO DATE (e.g., "best old anime" → "best classic anime")
- For "how to/tutorial" queries → add current year ONLY if it changes frequently (tech, marketing, etc.)
- For timeless topics → NO DATE (e.g., "learn guitar basics", "history of Rome")

Examples with current year = {current_year}:
- "how to learn programming" → "learn programming for beginners"
- "I want to get better at public speaking" → "public speaking tips"
- "best upcoming anime" → "best upcoming anime {next_year}"
- "latest digital marketing strategies" → "digital marketing strategy {current_year}"
- "python for data science" → "python data science tutorial"
- "teach me about investing" → "investing for beginners"
- "best old movies" → "best classic movies"
- "trending AI tools" → "AI tools {current_year}"
- "history of jazz music" → "history of jazz music"
- "how to use ChatGPT" → "ChatGPT tutorial {current_year}"
- "best productivity hacks" → "productivity tips {current_year}"
- "learn guitar for beginners" → "guitar tutorial for beginners"

Return ONLY the refined search query, nothing else.

Refined Query:""")
        
        # Add preprocessing to inject current date into refine chain
        def add_date_context(user_query: str) -> dict:
            """Add current date context to the query refinement."""
            now = datetime.now()
            return {
                "user_query": user_query,
                "current_date": now.strftime("%B %d, %Y"),  # e.g., "November 24, 2025"
                "current_year": str(now.year),
                "next_year": str(now.year + 1)
            }
        
        self.refine_chain = (
            RunnableLambda(add_date_context)
            | self.refine_prompt 
            | self.refine_llm  # Use cheaper model for refinement
            | StrOutputParser()
            | RunnableLambda(lambda x: x.strip())
        )
        
        # ===== CHAIN 2: YouTube Research (wraps Phase 1 code) =====
        self.youtube_research_chain = RunnableLambda(self._fetch_youtube_transcripts)
        
        # ===== CHAIN 3: Script Generation =====
        self.script_prompt = ChatPromptTemplate.from_template("""
You are an expert YouTube scriptwriter. Write a complete video script that will be read aloud by text-to-speech software.

TOPIC: {original_query}
RESEARCH QUERY: {refined_query}
VIDEOS ANALYZED: {video_count}

RESEARCH TRANSCRIPTS:
{transcripts}

═══════════════════════════════════════════════════════════════════════════════
CRITICAL: OUTPUT RAW SPOKEN TEXT ONLY
═══════════════════════════════════════════════════════════════════════════════

⚠️ ABSOLUTE REQUIREMENTS - VIOLATION WILL FAIL THE TASK:
1. NO square brackets of any kind: [INTRO], [HOOK], [CONCLUSION], [CTA] etc. are FORBIDDEN
2. NO section headers or labels whatsoever
3. NO markdown formatting (no **, no ##, no bullets)
4. NO timestamps or time markers
5. NO stage directions or visual cues
6. ONLY output the exact words to be spoken - nothing else

Your output must be readable from start to finish as one continuous script that a narrator can speak aloud without skipping anything.

STRUCTURE TO FOLLOW (but NEVER label these sections):

Start with an attention-grabbing hook (8-15 seconds worth of text) - a shocking fact, provocative question, or bold statement.

Then a brief introduction setting expectations for what viewers will learn.

The main content should cover 3-5 key points with real examples, storytelling, and insights from the transcripts. Use conversational language, speak directly to the viewer using "you", and make smooth transitions between points.

Around the middle, naturally weave in ONE brief engagement reminder like "If you're finding this helpful, a quick like really helps the channel!"

End with a brief recap, motivational closing thought, and final call-to-action.

STYLE:
- Conversational, like talking to a friend
- Use contractions (you're, don't, it's)
- Vary sentence length
- Energetic but authentic
- 1,200-1,800 words total

EXTRACT VALUE FROM THE TRANSCRIPTS:
- Common themes and patterns
- Specific examples and statistics
- Successful creators' approaches
- Actionable insights

NOW OUTPUT THE RAW SCRIPT (just the spoken words, absolutely no labels or formatting):

""")
        
        self.script_chain = (
            self.script_prompt 
            | self.llm 
            | StrOutputParser()
        )
        
        # ===== COMPLETE PIPELINE =====
        # Preprocessing for complete pipeline
        def prepare_pipeline_input(user_query: str) -> dict:
            """Prepare input with original query preserved."""
            return {
                "refined_query": user_query,  # Will be refined by the chain
                "original_query": user_query
            }
        
        self.complete_pipeline = (
            RunnableLambda(prepare_pipeline_input)
            | {
                # Step 1: Refine the query
                "refined_query": lambda x: self.refine_chain.invoke(x["original_query"]),
                "original_query": lambda x: x["original_query"]
            }
            | RunnableLambda(self._prepare_research_input)
            # Step 2: Fetch YouTube transcripts
            | self.youtube_research_chain
            # Step 3: Generate script
            | self.script_chain
        )
    
    def _prepare_research_input(self, inputs: Dict) -> Dict:
        """Prepare input for YouTube research chain."""
        return {
            "refined_query": inputs["refined_query"],
            "original_query": inputs["original_query"]
        }
    
    def _fetch_youtube_transcripts(self, inputs: Dict) -> Dict:
        """
        Fetch YouTube transcripts using Phase 1 code.
        
        Args:
            inputs: Dict with 'refined_query' and 'original_query'
            
        Returns:
            Dict with transcripts and metadata for script generation
        """
        refined_query = inputs["refined_query"]
        original_query = inputs["original_query"]
        
        print("\n" + "="*80)
        print(f"🔍 YOUTUBE RESEARCH PHASE")
        print("="*80)
        print(f"Original Query: {original_query}")
        print(f"Refined Query: {refined_query}")
        print("="*80 + "\n")
        
        # Search videos (two-phase: fast search + parallel metadata)
        videos = self.video_fetcher.search_videos(
            refined_query, 
            max_results=self.max_videos,
            top_n=self.top_n_videos
        )
        
        if not videos:
            print("❌ No videos found!")
            return {
                'original_query': original_query,
                'refined_query': refined_query,
                'transcripts': None,
                'video_count': 0,
                'metadata': {'error': 'video_search_failed', 'message': 'Could not fetch videos from YouTube. Please try again later.'}
            }
        
        # Rank videos
        top_videos = self.video_fetcher.rank_videos(videos, top_n=self.top_n_videos)
        
        # Fetch transcripts in parallel
        videos_with_transcripts = self.video_fetcher.fetch_transcripts_parallel(
            top_videos,
            self.transcript_scraper
        )
        
        # Combine all transcripts
        combined_transcripts = self._format_transcripts(videos_with_transcripts)
        
        successful_count = sum(
            1 for v in videos_with_transcripts 
            if v.get('transcript_available')
        )
        
        print("\n" + "="*80)
        print(f"✅ RESEARCH COMPLETE: {successful_count} transcripts fetched")
        print("="*80 + "\n")
        
        return {
            'original_query': original_query,
            'refined_query': refined_query,
            'transcripts': combined_transcripts,
            'video_count': successful_count,
            'metadata': {
                'total_videos': len(videos_with_transcripts),
                'successful_transcripts': successful_count,
                'videos': videos_with_transcripts
            }
        }
    
    def _format_transcripts(self, videos: List[Dict]) -> str:
        """Format transcripts for the LLM prompt."""
        formatted = []
        
        for i, video in enumerate(videos, 1):
            if video.get('transcript_available'):
                transcript = video['transcript']
                
                # Truncate if too long (to stay within token limits)
                if len(transcript) > 15000:
                    transcript = transcript[:15000] + "\n\n[... transcript truncated for length ...]"
                
                section = f"""
{'='*79}
VIDEO {i}: {video['title']}
CHANNEL: {video['channel']}
SUBSCRIBERS: {video.get('subscriber_count', 0):,}
VIEWS: {video.get('views', 0):,}
{'='*79}

{transcript}
"""
                formatted.append(section)
        
        if not formatted:
            return None
        
        return "\n\n".join(formatted)
    
    def generate_script(self, user_query: str) -> str:
        """
        Generate a YouTube script based on user query.
        
        Args:
            user_query: User's topic/query
            
        Returns:
            Generated YouTube script
        """
        print("\n" + "🚀"*40)
        print("YOUTUBE SCRIPT GENERATOR - LANGCHAIN PIPELINE")
        print("🚀"*40 + "\n")
        
        print(f"User Query: {user_query}\n")
        print("⏳ Starting pipeline...\n")
        
        # Run the complete LCEL pipeline
        result = self.complete_pipeline.invoke(user_query)
        
        return result
    
    def generate_script_with_metadata(self, user_query: str) -> Dict:
        """
        Generate script and return metadata.
        
        Args:
            user_query: User's topic/query
            
        Returns:
            Dict with 'script', 'refined_query', 'metadata'
        """
        print("\n" + "🚀"*40)
        print("YOUTUBE SCRIPT GENERATOR - LANGCHAIN PIPELINE")
        print("🚀"*40 + "\n")
        
        print(f"User Query: {user_query}\n")
        
        # Step 1: Refine query
        print("📝 Step 1: Refining search query...")
        print(f"   Original: {user_query}")
        refined_query = self.refine_chain.invoke(user_query)
        print(f"   ✓ Refined: {refined_query}\n")
        
        # Step 2: Fetch transcripts
        print("🔍 Step 2: Fetching YouTube transcripts...")
        research_data = self.youtube_research_chain.invoke({
            "refined_query": refined_query,
            "original_query": user_query
        })
        
        # Step 3: Generate script
        print("✍️  Step 3: Generating YouTube script...")
        script = self.script_chain.invoke(research_data)
        print("✓ Script generated!\n")
        
        return {
            'script': script,
            'refined_query': refined_query,
            'metadata': research_data.get('metadata', {}),
            'video_count': research_data.get('video_count', 0)
        }


# ===== Convenience Functions =====

def generate_script(
    user_query: str,
    model: str = "gpt-4",
    temperature: float = 0.7
) -> str:
    """
    Quick function to generate a script.
    
    Args:
        user_query: User's topic/query
        model: OpenAI model (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
        temperature: Creativity level (0-1)
        
    Returns:
        Generated script
    """
    pipeline = ScriptGeneratorPipeline(model=model, temperature=temperature)
    return pipeline.generate_script(user_query)


def generate_script_advanced(
    user_query: str,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_videos: int = 15,
    top_n_videos: int = 7,
    subscriber_threshold: int = 50000
) -> Dict:
    """
    Advanced script generation with full control and metadata.
    
    Args:
        user_query: User's topic/query
        model: OpenAI model
        temperature: Creativity level (0-1)
        max_videos: Maximum videos to search
        top_n_videos: Top N videos to analyze
        subscriber_threshold: Minimum subscribers
        
    Returns:
        Dict with script and metadata
    """
    pipeline = ScriptGeneratorPipeline(
        model=model,
        temperature=temperature,
        max_videos=max_videos,
        top_n_videos=top_n_videos,
        subscriber_threshold=subscriber_threshold
    )
    return pipeline.generate_script_with_metadata(user_query)


def generate_youtube_script(
    topic: str,
    model: str = "gpt-5.1",
    refine_model: str = "gpt-5-nano",
    max_videos: int = 15,
    top_n: int = 7,
    subscriber_threshold: int = 50000,
    max_workers: int = 5
) -> Dict:
    """
    Generate a YouTube script from a topic (API wrapper).
    
    Args:
        topic: User's topic/query
        model: OpenAI model for script generation
        refine_model: Model for query refinement
        max_videos: Maximum videos to search
        top_n: Top N videos to analyze
        subscriber_threshold: Minimum subscribers
        max_workers: Parallel workers
        
    Returns:
        Dict with script and all metadata
    """
    pipeline = ScriptGeneratorPipeline(
        model=model,
        refine_model=refine_model,
        max_videos=max_videos,
        top_n_videos=top_n,
        subscriber_threshold=subscriber_threshold,
        max_workers=max_workers
    )
    
    # Step 1: Refine query
    refined_query = pipeline.refine_chain.invoke(topic)
    
    # Step 2: Fetch transcripts
    research_data = pipeline.youtube_research_chain.invoke({
        "refined_query": refined_query,
        "original_query": topic
    })
    
    # Step 3: Generate script
    script = pipeline.script_chain.invoke(research_data)
    
    return {
        'success': True,
        'script': script,
        'refined_query': refined_query,
        'original_query': topic,
        'videos_analyzed': research_data.get('video_count', 0),
        'combined_transcripts': research_data.get('transcripts'),
        'metadata': research_data.get('metadata', {}),
        'stats': {
            'total_videos': research_data.get('metadata', {}).get('total_videos', 0),
            'successful_transcripts': research_data.get('metadata', {}).get('successful_transcripts', 0),
        }
    }


def regenerate_script_only(
    original_query: str,
    refined_query: str,
    combined_transcripts: str,
    video_count: int = 0,
    model: str = "gpt-5.1",
    temperature: float = 0.7
) -> Dict:
    """
    Regenerate script using existing transcripts (no new YouTube fetch).
    
    Args:
        original_query: Original user query
        refined_query: Refined search query
        combined_transcripts: Pre-fetched transcripts
        video_count: Number of videos analyzed
        model: OpenAI model for generation
        temperature: Creativity level
        
    Returns:
        Dict with regenerated script
    """
    llm = ChatOpenAI(model=model, temperature=temperature)
    
    script_prompt = ChatPromptTemplate.from_template("""
You are an expert YouTube scriptwriter. Write a complete video script that will be read aloud by text-to-speech software.

TOPIC: {original_query}
RESEARCH QUERY: {refined_query}
VIDEOS ANALYZED: {video_count}

RESEARCH TRANSCRIPTS:
{transcripts}

═══════════════════════════════════════════════════════════════════════════════
CRITICAL: OUTPUT RAW SPOKEN TEXT ONLY
═══════════════════════════════════════════════════════════════════════════════

⚠️ ABSOLUTE REQUIREMENTS - VIOLATION WILL FAIL THE TASK:
1. NO square brackets of any kind: [INTRO], [HOOK], [CONCLUSION], [CTA] etc. are FORBIDDEN
2. NO section headers or labels whatsoever
3. NO markdown formatting (no **, no ##, no bullets)
4. NO timestamps or time markers
5. NO stage directions or visual cues
6. ONLY output the exact words to be spoken - nothing else

Your output must be readable from start to finish as one continuous script.

STYLE:
- Conversational, like talking to a friend
- Use contractions (you're, don't, it's)
- Vary sentence length
- Energetic but authentic
- 1,200-1,800 words total

NOW OUTPUT THE RAW SCRIPT (just the spoken words, absolutely no labels or formatting):

""")
    
    script_chain = script_prompt | llm | StrOutputParser()
    
    script = script_chain.invoke({
        'original_query': original_query,
        'refined_query': refined_query,
        'transcripts': combined_transcripts,
        'video_count': video_count
    })
    
    return {
        'success': True,
        'script': script,
        'refined_query': refined_query,
        'original_query': original_query,
        'videos_analyzed': video_count,
        'stats': {
            'regenerated': True,
            'model': model,
            'temperature': temperature
        }
    }

