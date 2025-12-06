"""
YouTube video search and metadata fetching module
Uses YouTube Data API v3 for reliable video search and metadata
"""

import requests
import os
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class VideoFetcher:
    """Handles YouTube video search, ranking, and metadata fetching using YouTube Data API."""
    
    def __init__(self, subscriber_threshold: int = 50000, max_workers: int = 10):
        """
        Initialize the video fetcher.
        
        Args:
            subscriber_threshold: Minimum subscribers for higher scoring
            max_workers: Maximum number of parallel workers for transcript fetching
        """
        self.subscriber_threshold = subscriber_threshold
        self.max_workers = max_workers
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY')
        self._lock = threading.Lock()
        
        if not self.youtube_api_key:
            print("⚠️ Warning: YOUTUBE_API_KEY not set. Video search will fail.")
    
    def search_videos(self, topic: str, max_results: int = 15, top_n: int = 10) -> List[Dict]:
        """
        Search for YouTube videos using the YouTube Data API v3.
        
        This makes 2 API calls:
        1. Search for videos matching the topic
        2. Get statistics (views, etc.) for found videos
        
        Args:
            topic: Search query
            max_results: Maximum videos to search for
            top_n: Number of top videos to return (by view count)
            
        Returns:
            List of video dicts with metadata
        """
        if not self.youtube_api_key:
            print("❌ YOUTUBE_API_KEY not set!")
            return []
        
        print(f"🔍 Searching YouTube for: '{topic}'...")
        
        try:
            # Step 1: Search for videos
            search_url = "https://www.googleapis.com/youtube/v3/search"
            search_params = {
                'part': 'snippet',
                'q': topic,
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance',  # relevance gives better results than viewCount for search
                'key': self.youtube_api_key,
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=10)
            
            if search_response.status_code != 200:
                error_msg = search_response.json().get('error', {}).get('message', 'Unknown error')
                print(f"❌ YouTube API search error: {error_msg}")
                return []
            
            search_data = search_response.json()
            video_ids = [item['id']['videoId'] for item in search_data.get('items', [])]
            
            if not video_ids:
                print("❌ No videos found")
                return []
            
            # Step 2: Get video statistics (single batched request for all videos)
            stats_url = "https://www.googleapis.com/youtube/v3/videos"
            stats_params = {
                'part': 'snippet,statistics,contentDetails',
                'id': ','.join(video_ids),  # Batch all IDs in one request
                'key': self.youtube_api_key,
            }
            
            stats_response = requests.get(stats_url, params=stats_params, timeout=10)
            
            if stats_response.status_code != 200:
                print(f"❌ YouTube API stats error: {stats_response.status_code}")
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
                
                # Get best available thumbnail (prefer high quality)
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = (
                    thumbnails.get('high', {}).get('url') or
                    thumbnails.get('medium', {}).get('url') or
                    thumbnails.get('default', {}).get('url') or
                    f"https://i.ytimg.com/vi/{item['id']}/hqdefault.jpg"
                )
                
                videos.append({
                    'video_id': item['id'],
                    'title': snippet.get('title', 'Unknown'),
                    'channel': snippet.get('channelTitle', 'Unknown'),
                    'channel_id': snippet.get('channelId', ''),
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'duration': duration_seconds,
                    'subscriber_count': 0,  # Would need separate channel API call
                    'thumbnail_url': thumbnail_url,
                })
            
            # Sort by views and return top N
            videos_sorted = sorted(videos, key=lambda x: x['views'], reverse=True)
            top_videos = videos_sorted[:top_n]
            
            print(f"✓ Found {len(top_videos)} videos via YouTube API")
            return top_videos
            
        except requests.exceptions.Timeout:
            print("❌ YouTube API timeout")
            return []
        except Exception as e:
            print(f"❌ YouTube API error: {str(e)}")
            return []
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration string to seconds."""
        import re
        
        # Match hours, minutes, seconds
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def calculate_score(self, video: Dict) -> float:
        """Calculate ranking score based on views, subscribers, and duration."""
        views = video.get('views', 0)
        subs = video.get('subscriber_count', 0)
        duration = video.get('duration', 0)
        
        # Base score from views (in millions)
        score = views / 1_000_000
        
        # Subscriber multiplier (50k+ gets 2x boost)
        if subs >= self.subscriber_threshold:
            score *= 2
        
        # Duration bonus (longer videos are often more comprehensive)
        if duration > 3600:  # 1+ hour
            score *= 1.5
        elif duration > 1800:  # 30+ minutes
            score *= 1.2
        
        return score
    
    def rank_videos(self, videos: List[Dict], top_n: int = 5) -> List[Dict]:
        """Rank and select top N videos."""
        print("📊 Ranking videos...")
        
        # Calculate scores
        for video in videos:
            video['score'] = self.calculate_score(video)
        
        # Sort by score
        ranked = sorted(videos, key=lambda x: x['score'], reverse=True)
        top_videos = ranked[:top_n]
        
        print(f"✓ Selected top {len(top_videos)} videos:\n")
        
        for i, video in enumerate(top_videos, 1):
            score = video['score']
            views = video.get('views', 0)
            duration = video.get('duration', 0)
            mins = duration // 60
            print(f"  {i}. [{score:.2f}] {video['title'][:60]}...")
            print(f"     Channel: {video['channel']} | {views:,} views | {mins}min")
        
        print()
        return top_videos
    
    def fetch_single_transcript(self, video: Dict, scraper) -> Dict:
        """Fetch transcript for a single video."""
        video_id = video['video_id']
        title = video['title']
        
        with self._lock:
            print(f"  📝 Fetching transcript: {title[:50]}...")
        
        transcript_text = scraper.fetch_transcript(video_id)
        
        if transcript_text:
            video['transcript'] = transcript_text
            video['transcript_available'] = True
            with self._lock:
                print(f"  ✅ Got transcript: {title[:50]}...")
        else:
            video['transcript'] = None
            video['transcript_available'] = False
            with self._lock:
                print(f"  ❌ No transcript: {title[:50]}...")
        
        return video
    
    def fetch_transcripts_parallel(self, videos: List[Dict], scraper) -> List[Dict]:
        """
        Fetch transcripts for multiple videos in parallel.
        
        Uses ThreadPoolExecutor to fetch all transcripts concurrently.
        
        Args:
            videos: List of video dicts
            scraper: TranscriptScraper instance
            
        Returns:
            Videos with transcript data added
        """
        print(f"\n⚡ Fetching transcripts for {len(videos)} videos in parallel...")
        print(f"   Using {self.max_workers} parallel workers\n")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks at once
            futures = {
                executor.submit(self.fetch_single_transcript, video, scraper): video 
                for video in videos
            }
            
            # Collect results as they complete
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        successful = sum(1 for v in results if v.get('transcript_available'))
        print(f"\n✓ Transcripts fetched: {successful}/{len(videos)} successful\n")
        
        return results
