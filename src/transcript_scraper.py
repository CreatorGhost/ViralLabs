"""
Transcript scraping module - fetches transcripts from transcript websites
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Optional


class TranscriptScraper:
    """Scrapes transcripts from transcript websites (bypasses YouTube rate limits)."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.invidious_instances = [
            "https://inv.nadeko.net",
            "https://invidious.nerdvpn.de",
            "https://invidious.privacyredirect.com",
            "https://vid.puffyan.us",
        ]
    
    def fetch_from_youtubetotranscript(self, video_id: str) -> Optional[str]:
        """Fetch transcript from youtubetotranscript.com (most reliable)."""
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            response = self.session.post(
                'https://youtubetotranscript.com/transcript',
                data={'youtube_url': youtube_url},
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                containers = [
                    soup.find('div', {'id': re.compile(r'transcript', re.I)}),
                    soup.find('pre'),
                    soup.find('div', {'class': re.compile(r'transcript|content|result', re.I)}),
                    soup.find('textarea'),
                ]
                
                for container in containers:
                    if container:
                        text = container.get_text(strip=True)
                        if text and len(text) > 100:
                            return text
            return None
        except Exception:
            return None
    
    def fetch_from_invidious(self, video_id: str) -> Optional[str]:
        """Fetch transcript/captions from Invidious API."""
        for instance in self.invidious_instances:
            try:
                # First get video info to find caption tracks
                url = f"{instance}/api/v1/videos/{video_id}"
                response = self.session.get(url, timeout=15)
                
                if response.status_code != 200:
                    continue
                    
                video_info = response.json()
                captions = video_info.get('captions', [])
                
                # Look for English captions
                caption_url = None
                for cap in captions:
                    label = cap.get('label', '').lower()
                    if 'english' in label or cap.get('language_code', '').startswith('en'):
                        caption_url = cap.get('url')
                        break
                
                # If no English, try first available
                if not caption_url and captions:
                    caption_url = captions[0].get('url')
                
                if not caption_url:
                    continue
                
                # Fetch the captions
                if not caption_url.startswith('http'):
                    caption_url = f"{instance}{caption_url}"
                    
                cap_response = self.session.get(caption_url, timeout=15)
                if cap_response.status_code == 200:
                    # Parse caption format (usually TTML or VTT)
                    text = cap_response.text
                    
                    # Clean up TTML/VTT to plain text
                    soup = BeautifulSoup(text, 'html.parser')
                    
                    # For TTML format
                    paragraphs = soup.find_all('p')
                    if paragraphs:
                        transcript = ' '.join(p.get_text(strip=True) for p in paragraphs)
                        if transcript and len(transcript) > 100:
                            return transcript
                    
                    # For VTT format - extract text between timestamps
                    lines = text.split('\n')
                    transcript_lines = []
                    for line in lines:
                        line = line.strip()
                        # Skip timestamp lines, WEBVTT header, and empty lines
                        if not line or '-->' in line or line.startswith('WEBVTT') or line.startswith('NOTE'):
                            continue
                        # Skip numbered cue identifiers
                        if line.isdigit():
                            continue
                        transcript_lines.append(line)
                    
                    if transcript_lines:
                        transcript = ' '.join(transcript_lines)
                        if len(transcript) > 100:
                            return transcript
                            
            except Exception:
                continue
        
        return None
    
    def fetch_transcript(self, video_id: str) -> Optional[str]:
        """
        Fetch transcript with fallback mechanism.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Transcript text or None if unavailable
        """
        # Primary method (most reliable for cloud servers)
        result = self.fetch_from_invidious(video_id)
        if result:
            return result
        
        # Secondary method
        result = self.fetch_from_youtubetotranscript(video_id)
        if result:
            return result
        
        return None

