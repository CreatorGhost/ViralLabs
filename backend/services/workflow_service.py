"""
Workflow orchestration service with streaming support.
Single Responsibility: Orchestrates the full generation workflow.
Dependency Inversion: Depends on abstractions (services) not implementations.
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import AsyncGenerator
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.models.schemas import FullWorkflowRequest
from backend.services.sse import SSEService
from backend.services.thumbnail_service import ThumbnailService
from backend.core.session import SessionManager


class WorkflowStreamService:
    """
    Service for orchestrating the full workflow with SSE streaming.
    
    Workflow steps:
    1. Refine search query
    2. Search YouTube for videos
    3. Rank videos by relevance
    4. Fetch video transcripts
    5. Generate script (streamed word-by-word)
    6. Generate thumbnails (parallel, streamed as completed)
    """
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.thumbnail_service = ThumbnailService()
    
    async def generate_stream(
        self,
        request: FullWorkflowRequest,
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Async generator that yields SSE events during the full workflow.
        
        Args:
            request: Full workflow request parameters
            session_id: User session identifier
            
        Yields:
            SSE formatted strings for each event
        """
        from openai import OpenAI
        from src.video_fetcher import VideoFetcher
        from src.transcript_scraper import TranscriptScraper
        
        current_step = SSEService.STEP_INITIALIZING
        
        try:
            session = self.session_manager.get_or_create(session_id)
            loop = asyncio.get_event_loop()
            
            # Initialize components
            video_fetcher = VideoFetcher(
                subscriber_threshold=request.subscriber_threshold,
                max_workers=request.max_workers
            )
            transcript_scraper = TranscriptScraper()
            client = OpenAI()
            
            # Check if user provided pre-selected videos
            has_selected_videos = request.selected_video_ids and len(request.selected_video_ids) > 0
            
            if has_selected_videos:
                # ===== USER SELECTED VIDEOS: Skip search/rank =====
                current_step = SSEService.STEP_REFINING
                yield SSEService.progress(
                    current_step,
                    "Using pre-selected videos...",
                    {"original": request.topic, "video_count": len(request.selected_video_ids)}
                )
                
                # Use stored refined query from search step, or use topic as-is
                refined_query = self.session_manager.get_data(session_id, "refined_query") or request.topic
                
                yield SSEService.progress(
                    current_step,
                    "Videos selected by user",
                    {"original": request.topic, "refined": refined_query}
                )
                
                # Fetch metadata for selected videos
                current_step = SSEService.STEP_SEARCHING
                yield SSEService.progress(
                    current_step,
                    f"Loading {len(request.selected_video_ids)} selected videos...",
                    {"count": len(request.selected_video_ids)}
                )
                
                top_videos = await self._fetch_videos_by_ids(
                    request.selected_video_ids, loop
                )
                
                if not top_videos:
                    yield SSEService.error(
                        current_step,
                        "Failed to load selected videos",
                        "Could not fetch metadata for selected video IDs"
                    )
                    return
                
                video_summaries = [
                    {
                        "title": v.get('title', 'Unknown')[:60],
                        "channel": v.get('channel', 'Unknown'),
                        "views": v.get('views', 0)
                    }
                    for v in top_videos
                ]
                
                yield SSEService.progress(
                    current_step,
                    f"Loaded {len(top_videos)} user-selected videos",
                    {"count": len(top_videos), "videos": video_summaries}
                )
                
            else:
                # ===== STANDARD FLOW: Search and rank =====
                
                # ===== STEP 1: Refine Query =====
                current_step = SSEService.STEP_REFINING
                yield SSEService.progress(
                    current_step,
                    "Refining search query...",
                    {"original": request.topic}
                )
                
                refined_query = await self._refine_query(
                    client, request.topic, request.refine_model, loop
                )
                
                yield SSEService.progress(
                    current_step,
                    "Query refined",
                    {"original": request.topic, "refined": refined_query}
                )
                
                # ===== STEP 2: Search YouTube =====
                current_step = SSEService.STEP_SEARCHING
                yield SSEService.progress(current_step, "Searching YouTube...", {})
                
                videos = await self._search_videos(
                    video_fetcher, refined_query, request.max_videos, loop
                )
                
                if not videos:
                    yield SSEService.error(
                        current_step,
                        "No videos found",
                        "Could not find videos matching your query"
                    )
                    return
                
                yield SSEService.progress(
                    current_step,
                    f"Found {len(videos)} videos",
                    {"count": len(videos)}
                )
                
                # ===== STEP 3: Rank Videos =====
                current_step = SSEService.STEP_RANKING
                yield SSEService.progress(current_step, "Ranking videos by relevance...", {})
                
                top_videos = await self._rank_videos(
                    video_fetcher, videos, request.top_n_videos, loop
                )
                
                video_summaries = [
                    {
                        "title": v.get('title', 'Unknown')[:60],
                        "channel": v.get('channel', 'Unknown'),
                        "views": v.get('views', 0)
                    }
                    for v in top_videos
                ]
                
                yield SSEService.progress(
                    current_step,
                    f"Selected top {len(top_videos)} videos",
                    {"count": len(top_videos), "videos": video_summaries}
                )
            
            # ===== STEP 4: Fetch Transcripts =====
            current_step = SSEService.STEP_TRANSCRIPTS
            total_transcripts = len(top_videos)
            yield SSEService.progress(
                current_step,
                "Fetching video transcripts...",
                {"current": 0, "total": total_transcripts}
            )
            
            videos_with_transcripts = []
            async for event, result in self._fetch_transcripts_stream(
                top_videos, transcript_scraper, total_transcripts, loop
            ):
                yield event
                if result:
                    videos_with_transcripts.append(result)
            
            successful_transcripts = sum(
                1 for v in videos_with_transcripts if v.get('transcript_available')
            )
            
            yield SSEService.progress(
                current_step,
                "Transcripts complete",
                {"success": successful_transcripts, "total": total_transcripts}
            )
            
            if successful_transcripts == 0:
                yield SSEService.error(
                    current_step,
                    "No transcripts available",
                    "Could not fetch any video transcripts"
                )
                return
            
            # ===== STEP 5: Generate Script (Streaming) =====
            current_step = SSEService.STEP_GENERATING
            yield SSEService.progress(current_step, "Generating YouTube script...", {})
            
            combined_transcripts = self._format_transcripts(videos_with_transcripts)
            
            full_script = ""
            word_count = 0
            
            async for chunk_event, chunk_text in self._generate_script_stream(
                client, request, refined_query, successful_transcripts,
                combined_transcripts, loop
            ):
                yield chunk_event
                if chunk_text:
                    full_script += chunk_text
                    word_count += chunk_text.count(' ') + (1 if chunk_text.strip() else 0)
            
            yield SSEService.progress(
                current_step,
                "Script complete",
                {"word_count": word_count}
            )
            
            # Store in session
            self.session_manager.set_last_script(session_id, {
                "script": full_script,
                "refined_query": refined_query,
                "original_query": request.topic,
                "videos_analyzed": successful_transcripts
            })
            self.session_manager.set_research_data(session_id, {
                "original_query": request.topic,
                "refined_query": refined_query,
                "combined_transcripts": combined_transcripts,
                "videos_analyzed": successful_transcripts
            })
            
            # ===== STEP 6: Generate Thumbnails (if enabled) =====
            thumbnail_urls = []
            if request.enable_thumbnails:
                current_step = SSEService.STEP_THUMBNAILS
                
                face_path = self.session_manager.get_face_path(session_id)
                
                async for event in self.thumbnail_service.generate_parallel_stream(
                    topic=request.topic,
                    num_thumbnails=request.num_thumbnails,
                    resolution=request.resolution,
                    face_path=face_path,
                    face_mode=request.face_mode,
                    face_style=request.face_style,
                    use_reference_images=request.use_reference_images
                ):
                    if event:
                        yield event
                        # Extract thumbnail URLs from events
                        try:
                            event_data = json.loads(event.replace("data: ", "").strip())
                            if (event_data.get("type") == "thumbnail" and 
                                event_data.get("data", {}).get("url")):
                                thumbnail_urls.append({
                                    "url": event_data["data"]["url"],
                                    "filepath": event_data["data"].get("filepath")
                                })
                        except:
                            pass
                
                self.session_manager.set_last_thumbnails(session_id, thumbnail_urls)
            
            # ===== FINAL: Complete Event =====
            yield SSEService.complete({
                "script": full_script,
                "script_word_count": word_count,
                "refined_query": refined_query,
                "videos_analyzed": successful_transcripts,
                "thumbnails": thumbnail_urls if request.enable_thumbnails else None
            })
            
        except Exception as e:
            yield SSEService.error(current_step, str(e), str(e))
    
    async def _refine_query(
        self, client, topic: str, model: str, loop
    ) -> str:
        """Refine the search query using LLM."""
        refine_prompt = f"""You are a YouTube search query optimizer. Transform this query into an optimized YouTube search query (3-8 words max):

USER QUERY: {topic}

Return ONLY the refined search query, nothing else."""

        def _call():
            try:
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
                # Fallback to original topic
                return topic
            except Exception as e:
                print(f"Query refinement failed: {e}")
                return topic
        
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _call)
    
    async def _search_videos(
        self, video_fetcher, query: str, max_videos: int, loop
    ) -> list:
        """Search YouTube for videos."""
        def _call():
            return video_fetcher.search_videos(query, max_results=max_videos, top_n=max_videos)
        
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _call)
    
    async def _rank_videos(
        self, video_fetcher, videos: list, top_n: int, loop
    ) -> list:
        """Rank videos by relevance."""
        def _call():
            return video_fetcher.rank_videos(videos, top_n=top_n)
        
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _call)
    
    async def _fetch_videos_by_ids(self, video_ids: list, loop) -> list:
        """
        Fetch video metadata for specific video IDs using YouTube Data API.
        Used when user has pre-selected videos from the search step.
        """
        import os
        import requests
        
        def _call():
            youtube_api_key = os.environ.get('YOUTUBE_API_KEY')
            if not youtube_api_key:
                print("❌ YOUTUBE_API_KEY not set!")
                return []
            
            try:
                # Batch request for all video IDs
                stats_url = "https://www.googleapis.com/youtube/v3/videos"
                stats_params = {
                    'part': 'snippet,statistics,contentDetails',
                    'id': ','.join(video_ids),
                    'key': youtube_api_key,
                }
                
                stats_response = requests.get(stats_url, params=stats_params, timeout=10)
                
                if stats_response.status_code != 200:
                    print(f"❌ YouTube API error: {stats_response.status_code}")
                    return []
                
                stats_data = stats_response.json()
                videos = []
                
                for item in stats_data.get('items', []):
                    snippet = item.get('snippet', {})
                    stats = item.get('statistics', {})
                    content = item.get('contentDetails', {})
                    
                    # Parse duration (ISO 8601 format like PT5M30S)
                    duration_str = content.get('duration', 'PT0S')
                    duration_seconds = self._parse_duration(duration_str)
                    
                    videos.append({
                        'video_id': item['id'],
                        'title': snippet.get('title', 'Unknown'),
                        'channel': snippet.get('channelTitle', 'Unknown'),
                        'channel_id': snippet.get('channelId', ''),
                        'views': int(stats.get('viewCount', 0)),
                        'likes': int(stats.get('likeCount', 0)),
                        'comments': int(stats.get('commentCount', 0)),
                        'duration': duration_seconds,
                        'subscriber_count': 0,
                    })
                
                return videos
                
            except Exception as e:
                print(f"❌ Error fetching videos by IDs: {e}")
                return []
        
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _call)
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration string to seconds."""
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    async def _fetch_transcripts_stream(
        self, videos: list, scraper, total: int, loop
    ) -> AsyncGenerator:
        """Fetch transcripts with progress streaming."""
        
        async def fetch_single(video, index):
            def _fetch():
                video_id = video['video_id']
                transcript_text = scraper.fetch_transcript(video_id)
                video_copy = video.copy()
                if transcript_text:
                    video_copy['transcript'] = transcript_text
                    video_copy['transcript_available'] = True
                else:
                    video_copy['transcript'] = None
                    video_copy['transcript_available'] = False
                return video_copy
            
            with ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(executor, _fetch)
        
        tasks = [
            asyncio.create_task(fetch_single(v, i))
            for i, v in enumerate(videos)
        ]
        
        completed = 0
        for coro in asyncio.as_completed(tasks):
            result = await coro
            completed += 1
            
            status = "✓" if result.get('transcript_available') else "✗"
            event = SSEService.progress(
                SSEService.STEP_TRANSCRIPTS,
                f"Transcript {completed}/{total} {status}",
                {
                    "current": completed,
                    "total": total,
                    "video_title": result.get('title', '')[:40]
                }
            )
            yield event, result
    
    def _format_transcripts(self, videos: list) -> str:
        """Format transcripts for the script prompt."""
        formatted = []
        for i, video in enumerate(videos, 1):
            if video.get('transcript_available'):
                transcript = video['transcript']
                if len(transcript) > 15000:
                    transcript = transcript[:15000] + "\n\n[... truncated ...]"
                section = f"""
{'='*79}
VIDEO {i}: {video['title']}
CHANNEL: {video['channel']}
VIEWS: {video.get('views', 0):,}
{'='*79}

{transcript}
"""
                formatted.append(section)
        
        return "\n\n".join(formatted)
    
    async def _generate_script_stream(
        self, client, request, refined_query: str,
        video_count: int, transcripts: str, loop
    ) -> AsyncGenerator:
        """Generate script with word-by-word streaming."""
        
        script_prompt = f"""You are an expert YouTube scriptwriter. Create an engaging, well-structured video script.

USER'S ORIGINAL TOPIC: {request.topic}
RESEARCH QUERY USED: {refined_query}
NUMBER OF VIDEOS ANALYZED: {video_count}

Below are transcripts from {video_count} high-performing YouTube videos:

{transcripts}

YOUR TASK: Write a complete video script (1,200-1,800 words) as PLAIN TEXT ONLY.
- No markdown, no headings, no timestamps
- Write words that should be spoken, exactly as they should be spoken
- Include: Hook (8-15 sec), Introduction, Main Content (3-5 key points), Mid-video CTA, Conclusion

Write the script now:
"""

        def _create_stream():
            return client.chat.completions.create(
                model=request.model,
                messages=[{"role": "user", "content": script_prompt}],
                temperature=request.temperature,
                stream=True
            )
        
        with ThreadPoolExecutor() as executor:
            stream = await loop.run_in_executor(executor, _create_stream)
        
        # Stream content directly for smoother output - no buffering needed
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                # Yield each chunk immediately for smooth streaming
                yield SSEService.script_chunk(content), content

