"""
Tests for Pydantic Schemas.
"""

import pytest
from pydantic import ValidationError
from backend.models.schemas import (
    ScriptGenerateRequest,
    ScriptRegenerateRequest,
    ThumbnailGenerateRequest,
    FullWorkflowRequest,
    ScriptResponse,
    ThumbnailResponse,
    FullWorkflowResponse,
    SessionState,
)


class TestScriptGenerateRequest:
    """Test cases for ScriptGenerateRequest."""
    
    def test_valid_minimal(self):
        """Test with minimal required fields."""
        request = ScriptGenerateRequest(topic="Python tutorial")
        
        assert request.topic == "Python tutorial"
        assert request.model == "gpt-5.1"  # default
        assert request.temperature == 0.7  # default
    
    def test_valid_full(self):
        """Test with all fields."""
        request = ScriptGenerateRequest(
            topic="Advanced Python",
            model="gpt-4",
            refine_model="gpt-3.5-turbo",
            temperature=0.5,
            max_videos=20,
            top_n_videos=7,
            subscriber_threshold=100000,
            max_workers=8
        )
        
        assert request.topic == "Advanced Python"
        assert request.model == "gpt-4"
        assert request.temperature == 0.5
        assert request.max_videos == 20
    
    def test_invalid_topic_too_short(self):
        """Test with topic that's too short."""
        with pytest.raises(ValidationError):
            ScriptGenerateRequest(topic="ab")
    
    def test_invalid_temperature_too_high(self):
        """Test with temperature > 1.0."""
        with pytest.raises(ValidationError):
            ScriptGenerateRequest(topic="Python", temperature=1.5)
    
    def test_invalid_temperature_negative(self):
        """Test with negative temperature."""
        with pytest.raises(ValidationError):
            ScriptGenerateRequest(topic="Python", temperature=-0.1)
    
    def test_invalid_max_videos_too_low(self):
        """Test with max_videos below minimum."""
        with pytest.raises(ValidationError):
            ScriptGenerateRequest(topic="Python", max_videos=3)
    
    def test_invalid_max_videos_too_high(self):
        """Test with max_videos above maximum."""
        with pytest.raises(ValidationError):
            ScriptGenerateRequest(topic="Python", max_videos=50)


class TestThumbnailGenerateRequest:
    """Test cases for ThumbnailGenerateRequest."""
    
    def test_valid_defaults(self):
        """Test with default values."""
        request = ThumbnailGenerateRequest(topic="My Video")
        
        assert request.topic == "My Video"
        assert request.num_thumbnails == 3
        assert request.resolution == "2K"
        assert request.include_face == False
    
    def test_valid_with_face(self):
        """Test with face options."""
        request = ThumbnailGenerateRequest(
            topic="My Video",
            include_face=True,
            face_mode="center",
            face_style="professional"
        )
        
        assert request.include_face == True
        assert request.face_mode == "center"
        assert request.face_style == "professional"
    
    def test_invalid_num_thumbnails(self):
        """Test with invalid number of thumbnails."""
        with pytest.raises(ValidationError):
            ThumbnailGenerateRequest(topic="Test", num_thumbnails=10)


class TestFullWorkflowRequest:
    """Test cases for FullWorkflowRequest."""
    
    def test_valid_script_only(self):
        """Test with thumbnails disabled."""
        request = FullWorkflowRequest(
            topic="Python tutorial",
            enable_thumbnails=False
        )
        
        assert request.enable_thumbnails == False
        assert request.topic == "Python tutorial"
    
    def test_valid_full(self):
        """Test with all options enabled."""
        request = FullWorkflowRequest(
            topic="Python tutorial",
            model="gpt-4",
            temperature=0.8,
            enable_thumbnails=True,
            num_thumbnails=2,
            include_face=True
        )
        
        assert request.enable_thumbnails == True
        assert request.num_thumbnails == 2
        assert request.include_face == True


class TestScriptResponse:
    """Test cases for ScriptResponse."""
    
    def test_success_response(self):
        """Test successful response."""
        response = ScriptResponse(
            success=True,
            script="Generated script content",
            refined_query="python tutorial 2024",
            videos_analyzed=5
        )
        
        assert response.success == True
        assert response.script == "Generated script content"
        assert response.error is None
    
    def test_error_response(self):
        """Test error response."""
        response = ScriptResponse(
            success=False,
            error="API key not configured"
        )
        
        assert response.success == False
        assert response.error == "API key not configured"
        assert response.script is None


class TestThumbnailResponse:
    """Test cases for ThumbnailResponse."""
    
    def test_success_response(self):
        """Test successful response."""
        response = ThumbnailResponse(
            success=True,
            thumbnails=[{"url": "/thumb1.png"}, {"url": "/thumb2.png"}],
            successful_count=2
        )
        
        assert response.success == True
        assert len(response.thumbnails) == 2
        assert response.successful_count == 2


class TestSessionState:
    """Test cases for SessionState."""
    
    def test_default_state(self):
        """Test default session state."""
        state = SessionState()
        
        assert state.has_face == False
        assert state.face_id is None
        assert state.last_script is None
    
    def test_with_face(self):
        """Test session state with face."""
        state = SessionState(
            has_face=True,
            face_id="abc123",
            face_path="/path/to/face.png"
        )
        
        assert state.has_face == True
        assert state.face_id == "abc123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])







