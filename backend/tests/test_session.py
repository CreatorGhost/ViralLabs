"""
Tests for Session Management.
"""

import pytest
from pathlib import Path
from backend.core.session import SessionManager


class TestSessionManager:
    """Test cases for SessionManager."""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh SessionManager for each test."""
        return SessionManager()
    
    def test_get_or_create_new_session(self, manager):
        """Test creating a new session."""
        session = manager.get_or_create("test_session")
        
        assert session is not None
        assert session["has_face"] == False
        assert session["face_id"] is None
        assert session["face_path"] is None
        assert session["last_script"] is None
        assert session["last_thumbnails"] is None
        assert session["research_data"] is None
    
    def test_get_or_create_existing_session(self, manager):
        """Test retrieving an existing session."""
        # Create and modify
        session1 = manager.get_or_create("test_session")
        session1["has_face"] = True
        session1["face_id"] = "abc123"
        
        # Retrieve again
        session2 = manager.get_or_create("test_session")
        
        assert session2["has_face"] == True
        assert session2["face_id"] == "abc123"
    
    def test_get_nonexistent_session(self, manager):
        """Test getting a session that doesn't exist."""
        session = manager.get("nonexistent")
        assert session is None
    
    def test_get_existing_session(self, manager):
        """Test getting an existing session."""
        manager.get_or_create("test_session")
        session = manager.get("test_session")
        assert session is not None
    
    def test_update_session(self, manager):
        """Test updating session data."""
        manager.get_or_create("test_session")
        manager.update("test_session", {"has_face": True, "face_id": "xyz"})
        
        session = manager.get("test_session")
        assert session["has_face"] == True
        assert session["face_id"] == "xyz"
    
    def test_delete_session(self, manager):
        """Test deleting a session."""
        manager.get_or_create("test_session")
        
        result = manager.delete("test_session")
        assert result == True
        
        session = manager.get("test_session")
        assert session is None
    
    def test_delete_nonexistent_session(self, manager):
        """Test deleting a session that doesn't exist."""
        result = manager.delete("nonexistent")
        assert result == False
    
    def test_get_face_path_none(self, manager):
        """Test getting face path when no face is set."""
        manager.get_or_create("test_session")
        
        path = manager.get_face_path("test_session")
        assert path is None
    
    def test_get_face_path_invalid(self, manager):
        """Test getting face path when path doesn't exist on disk."""
        session = manager.get_or_create("test_session")
        session["face_path"] = "/nonexistent/path/face.png"
        
        path = manager.get_face_path("test_session")
        assert path is None
    
    def test_set_face(self, manager):
        """Test setting face information."""
        manager.get_or_create("test_session")
        manager.set_face("test_session", "face123", "/path/to/face.png")
        
        session = manager.get("test_session")
        assert session["has_face"] == True
        assert session["face_id"] == "face123"
        assert session["face_path"] == "/path/to/face.png"
    
    def test_clear_face(self, manager):
        """Test clearing face information."""
        manager.get_or_create("test_session")
        manager.set_face("test_session", "face123", "/path/to/face.png")
        
        old_path = manager.clear_face("test_session")
        
        assert old_path == "/path/to/face.png"
        
        session = manager.get("test_session")
        assert session["has_face"] == False
        assert session["face_id"] is None
        assert session["face_path"] is None
    
    def test_set_last_script(self, manager):
        """Test storing last script."""
        manager.get_or_create("test_session")
        
        script_data = {
            "script": "Test script content",
            "refined_query": "test query",
            "videos_analyzed": 5
        }
        manager.set_last_script("test_session", script_data)
        
        session = manager.get("test_session")
        assert session["last_script"] == script_data
    
    def test_set_research_data(self, manager):
        """Test storing research data."""
        manager.get_or_create("test_session")
        
        research_data = {
            "original_query": "test",
            "refined_query": "refined test",
            "combined_transcripts": "transcript content"
        }
        manager.set_research_data("test_session", research_data)
        
        session = manager.get("test_session")
        assert session["research_data"] == research_data
    
    def test_set_last_thumbnails(self, manager):
        """Test storing last thumbnails."""
        manager.get_or_create("test_session")
        
        thumbnails = [
            {"url": "/thumbnails/1.png"},
            {"url": "/thumbnails/2.png"}
        ]
        manager.set_last_thumbnails("test_session", thumbnails)
        
        session = manager.get("test_session")
        assert session["last_thumbnails"] == thumbnails
    
    def test_multiple_sessions(self, manager):
        """Test managing multiple sessions."""
        session1 = manager.get_or_create("session1")
        session2 = manager.get_or_create("session2")
        
        session1["has_face"] = True
        session2["has_face"] = False
        
        assert manager.get("session1")["has_face"] == True
        assert manager.get("session2")["has_face"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


