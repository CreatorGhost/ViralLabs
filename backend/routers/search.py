"""
Video search endpoints for content filtering.
Allows users to search and select videos before script generation.
"""

import os
import sys
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.video_fetcher import VideoFetcher
from backend.core.session import session_manager
from backend.models.schemas import (
    SearchVideosRequest,
    SearchVideosResponse,
    VideoItem,
)

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/videos", response_model=SearchVideosResponse)
async def search_videos(request: SearchVideosRequest, session_id: str = "default"):
    """
    Search YouTube videos and return list for user selection.
    
    This is step 1 of the video selection workflow:
    1. User enters topic -> search_videos returns video list
    2. User selects videos they want
    3. User calls generate endpoint with selected_video_ids
    
    Returns all found videos (not just top N) so users can choose.
    """
    
    if not os.getenv("YOUTUBE_API_KEY"):
        raise HTTPException(status_code=400, detail="YOUTUBE_API_KEY not set")
    
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not set")
    
    try:
        loop = asyncio.get_event_loop()
        
        # Initialize video fetcher
        video_fetcher = VideoFetcher(
            subscriber_threshold=request.subscriber_threshold,
            max_workers=5
        )
        
        # Refine the query using LLM
        refined_query = await _refine_query(
            request.topic, 
            request.refine_model, 
            loop
        )
        
        # Search YouTube for videos
        videos = await _search_videos(
            video_fetcher,
            refined_query,
            request.max_videos,
            loop
        )
        
        if not videos:
            return SearchVideosResponse(
                success=False,
                error="No videos found for this topic"
            )
        
        # Calculate scores for all videos
        for video in videos:
            video['score'] = video_fetcher.calculate_score(video)
        
        # Sort by score (highest first)
        videos_sorted = sorted(videos, key=lambda x: x['score'], reverse=True)
        
        # Convert to VideoItem models
        video_items = [
            VideoItem(
                video_id=v['video_id'],
                title=v['title'],
                channel=v['channel'],
                channel_id=v.get('channel_id', ''),
                views=v['views'],
                likes=v.get('likes', 0),
                comments=v.get('comments', 0),
                duration=v.get('duration', 0),
                score=v['score'],
                thumbnail_url=v.get('thumbnail_url', f"https://i.ytimg.com/vi/{v['video_id']}/hqdefault.jpg")
            )
            for v in videos_sorted
        ]
        
        # Store in session for later use
        session_manager.get_or_create(session_id)
        session_manager.set_data(session_id, "searched_videos", videos_sorted)
        session_manager.set_data(session_id, "refined_query", refined_query)
        session_manager.set_data(session_id, "original_query", request.topic)
        
        return SearchVideosResponse(
            success=True,
            refined_query=refined_query,
            original_query=request.topic,
            videos=video_items
        )
        
    except Exception as e:
        return SearchVideosResponse(success=False, error=str(e))


async def _refine_query(topic: str, model: str, loop) -> str:
    """Refine the search query using LLM."""
    from openai import OpenAI
    
    refine_prompt = f"""You are a YouTube search query optimizer. Transform this query into an optimized YouTube search query (3-8 words max):

USER QUERY: {topic}

Return ONLY the refined search query, nothing else."""

    def _call():
        try:
            client = OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": refine_prompt}],
                max_completion_tokens=50
            )
            content = response.choices[0].message.content
            if content:
                refined = content.strip().strip('"').strip("'")
                if refined:
                    return refined
            return topic
        except Exception as e:
            print(f"Query refinement failed: {e}")
            return topic
    
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _call)


async def _search_videos(video_fetcher, query: str, max_videos: int, loop) -> list:
    """Search YouTube for videos."""
    def _call():
        # Return all videos, not just top N (user will select)
        return video_fetcher.search_videos(query, max_results=max_videos, top_n=max_videos)
    
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _call)

