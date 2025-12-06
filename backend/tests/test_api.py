"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    """Test cases for health endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health endpoint returns correct structure."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "openai_key" in data
        assert "gemini_key" in data


class TestSessionEndpoint:
    """Test cases for session endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    def test_get_new_session(self, client):
        """Test getting a new session."""
        response = client.get("/session/test_new_session")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["has_face"] == False
        assert data["face_id"] is None
        assert data["last_script"] is None


class TestScriptEndpointValidation:
    """Test cases for script endpoint validation."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    def test_generate_script_missing_topic(self, client):
        """Test that missing topic returns validation error."""
        response = client.post("/generate/script", json={})
        
        assert response.status_code == 422  # Validation error
    
    def test_generate_script_short_topic(self, client):
        """Test that short topic returns validation error."""
        response = client.post("/generate/script", json={"topic": "ab"})
        
        assert response.status_code == 422
    
    def test_generate_script_invalid_temperature(self, client):
        """Test that invalid temperature returns validation error."""
        response = client.post("/generate/script", json={
            "topic": "Python tutorial",
            "temperature": 2.0
        })
        
        assert response.status_code == 422


class TestThumbnailEndpointValidation:
    """Test cases for thumbnail endpoint validation."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    def test_generate_thumbnails_missing_topic(self, client):
        """Test that missing topic returns validation error."""
        response = client.post("/generate/thumbnails", json={})
        
        assert response.status_code == 422
    
    def test_generate_thumbnails_invalid_count(self, client):
        """Test that invalid thumbnail count returns error."""
        response = client.post("/generate/thumbnails", json={
            "topic": "My Video",
            "num_thumbnails": 10  # Max is 5
        })
        
        assert response.status_code == 422


class TestWorkflowEndpointValidation:
    """Test cases for workflow endpoint validation."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    def test_full_workflow_missing_topic(self, client):
        """Test that missing topic returns validation error."""
        response = client.post("/generate/full-workflow", json={})
        
        assert response.status_code == 422
    
    def test_stream_workflow_missing_topic(self, client):
        """Test streaming endpoint with missing topic."""
        response = client.post("/generate/full-workflow/stream", json={})
        
        assert response.status_code == 422


class TestFaceEndpoint:
    """Test cases for face upload endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    def test_upload_face_no_file(self, client):
        """Test upload without file."""
        response = client.post("/upload/face")
        
        assert response.status_code == 422  # Missing file
    
    def test_get_face_not_found(self, client):
        """Test getting face that doesn't exist."""
        response = client.get("/face/nonexistent_session")
        
        assert response.status_code == 404


class TestThumbnailFileEndpoints:
    """Test cases for thumbnail file endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    def test_get_thumbnail_not_found(self, client):
        """Test getting thumbnail that doesn't exist."""
        response = client.get("/thumbnail/nonexistent.png")
        
        assert response.status_code == 404
    
    def test_list_thumbnails(self, client):
        """Test listing thumbnails."""
        response = client.get("/thumbnail/list")
        
        assert response.status_code == 200
        data = response.json()
        assert "thumbnails" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

