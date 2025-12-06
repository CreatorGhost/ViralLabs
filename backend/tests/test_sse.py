"""
Tests for SSE Service.
"""

import json
import pytest
from backend.services.sse import SSEService, sse_event


class TestSSEService:
    """Test cases for SSEService."""
    
    def test_format_event_basic(self):
        """Test basic event formatting."""
        result = SSEService.format_event("progress", "refining", "Test message", {"key": "value"})
        
        assert result.startswith("data: ")
        assert result.endswith("\n\n")
        
        # Parse the JSON
        json_str = result.replace("data: ", "").strip()
        data = json.loads(json_str)
        
        assert data["type"] == "progress"
        assert data["step"] == "refining"
        assert data["message"] == "Test message"
        assert data["data"] == {"key": "value"}
    
    def test_format_event_empty_data(self):
        """Test event formatting with no data."""
        result = SSEService.format_event("progress", "searching", "Searching...")
        
        json_str = result.replace("data: ", "").strip()
        data = json.loads(json_str)
        
        assert data["data"] == {}
    
    def test_progress_helper(self):
        """Test progress helper method."""
        result = SSEService.progress("ranking", "Ranking videos...", {"count": 5})
        
        json_str = result.replace("data: ", "").strip()
        data = json.loads(json_str)
        
        assert data["type"] == "progress"
        assert data["step"] == "ranking"
        assert data["data"]["count"] == 5
    
    def test_script_chunk_helper(self):
        """Test script_chunk helper method."""
        result = SSEService.script_chunk("Hello ")
        
        json_str = result.replace("data: ", "").strip()
        data = json.loads(json_str)
        
        assert data["type"] == "script_chunk"
        assert data["step"] == "generating"
        assert data["data"]["chunk"] == "Hello "
    
    def test_thumbnail_helper(self):
        """Test thumbnail helper method."""
        result = SSEService.thumbnail(
            index=1,
            url="/thumbnails/test.png",
            filepath="/path/test.png",
            current=1,
            total=3
        )
        
        json_str = result.replace("data: ", "").strip()
        data = json.loads(json_str)
        
        assert data["type"] == "thumbnail"
        assert data["step"] == "thumbnails"
        assert data["data"]["index"] == 1
        assert data["data"]["url"] == "/thumbnails/test.png"
        assert data["data"]["current"] == 1
        assert data["data"]["total"] == 3
    
    def test_complete_helper(self):
        """Test complete helper method."""
        result = SSEService.complete({
            "script": "Test script",
            "word_count": 100
        })
        
        json_str = result.replace("data: ", "").strip()
        data = json.loads(json_str)
        
        assert data["type"] == "complete"
        assert data["step"] == "complete"
        assert data["message"] == "Workflow complete!"
        assert data["data"]["script"] == "Test script"
    
    def test_error_helper(self):
        """Test error helper method."""
        result = SSEService.error("searching", "Search failed", "No results found")
        
        json_str = result.replace("data: ", "").strip()
        data = json.loads(json_str)
        
        assert data["type"] == "error"
        assert data["step"] == "searching"
        assert data["message"] == "Search failed"
        assert data["data"]["error"] == "No results found"
    
    def test_convenience_function(self):
        """Test the sse_event convenience function."""
        result = sse_event("progress", "test", "Test message", {"foo": "bar"})
        
        json_str = result.replace("data: ", "").strip()
        data = json.loads(json_str)
        
        assert data["type"] == "progress"
        assert data["data"]["foo"] == "bar"
    
    def test_event_types_constants(self):
        """Test that event type constants are defined."""
        assert SSEService.PROGRESS == "progress"
        assert SSEService.SCRIPT_CHUNK == "script_chunk"
        assert SSEService.THUMBNAIL == "thumbnail"
        assert SSEService.COMPLETE == "complete"
        assert SSEService.ERROR == "error"
    
    def test_step_constants(self):
        """Test that step constants are defined."""
        assert SSEService.STEP_REFINING == "refining"
        assert SSEService.STEP_SEARCHING == "searching"
        assert SSEService.STEP_RANKING == "ranking"
        assert SSEService.STEP_TRANSCRIPTS == "transcripts"
        assert SSEService.STEP_GENERATING == "generating"
        assert SSEService.STEP_THUMBNAILS == "thumbnails"
        assert SSEService.STEP_COMPLETE == "complete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


