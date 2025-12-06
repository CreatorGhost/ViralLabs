"""
Tests for video search and selection functionality.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os


class TestSearchEndpointValidation:
    """Test cases for search endpoint validation."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    def test_search_videos_missing_topic(self, client):
        """Test that missing topic returns validation error."""
        response = client.post("/search/videos", json={})
        
        assert response.status_code == 422  # Validation error
    
    def test_search_videos_short_topic(self, client):
        """Test that short topic returns validation error."""
        response = client.post("/search/videos", json={"topic": "ab"})
        
        assert response.status_code == 422
    
    def test_search_videos_invalid_max_videos(self, client):
        """Test that invalid max_videos returns validation error."""
        response = client.post("/search/videos", json={
            "topic": "Python tutorial",
            "max_videos": 100  # Max is 30
        })
        
        assert response.status_code == 422


class TestSearchEndpointWithMocks:
    """Test search endpoint with mocked external services."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    @pytest.fixture
    def mock_env(self):
        """Mock environment variables."""
        with patch.dict(os.environ, {
            "YOUTUBE_API_KEY": "fake_youtube_key",
            "OPENAI_API_KEY": "fake_openai_key"
        }):
            yield
    
    @pytest.fixture
    def mock_video_fetcher(self):
        """Mock VideoFetcher to return test videos."""
        mock_videos = [
            {
                'video_id': 'vid1',
                'title': 'Python Tutorial for Beginners',
                'channel': 'CodeChannel',
                'channel_id': 'ch1',
                'views': 1000000,
                'likes': 50000,
                'comments': 1000,
                'duration': 1200,
                'subscriber_count': 500000
            },
            {
                'video_id': 'vid2',
                'title': 'Advanced Python Tips',
                'channel': 'DevMaster',
                'channel_id': 'ch2',
                'views': 500000,
                'likes': 25000,
                'comments': 500,
                'duration': 900,
                'subscriber_count': 200000
            },
            {
                'video_id': 'vid3',
                'title': 'Python Best Practices',
                'channel': 'TechGuru',
                'channel_id': 'ch3',
                'views': 750000,
                'likes': 35000,
                'comments': 700,
                'duration': 1500,
                'subscriber_count': 300000
            }
        ]
        
        with patch('backend.routers.search.VideoFetcher') as MockFetcher:
            mock_instance = MagicMock()
            mock_instance.search_videos.return_value = mock_videos
            mock_instance.calculate_score.side_effect = lambda v: v['views'] / 1_000_000
            MockFetcher.return_value = mock_instance
            yield mock_videos
    
    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI client for query refinement."""
        with patch('openai.OpenAI') as MockOpenAI:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "python programming tutorial"
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client
            yield mock_client
    
    def test_search_videos_success(self, client, mock_env, mock_video_fetcher, mock_openai):
        """Test successful video search."""
        response = client.post("/search/videos", json={
            "topic": "Python tutorial",
            "max_videos": 15
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["refined_query"] == "python programming tutorial"
        assert data["original_query"] == "Python tutorial"
        assert len(data["videos"]) == 3
        
        # Check video structure
        video = data["videos"][0]
        assert "video_id" in video
        assert "title" in video
        assert "channel" in video
        assert "views" in video
        assert "duration" in video
        assert "score" in video
    
    def test_search_videos_stores_in_session(self, client, mock_env, mock_video_fetcher, mock_openai):
        """Test that search results are stored in session."""
        from backend.core.session import session_manager
        
        response = client.post("/search/videos?session_id=test_session", json={
            "topic": "Python tutorial"
        })
        
        assert response.status_code == 200
        
        # Check session data
        searched_videos = session_manager.get_data("test_session", "searched_videos")
        refined_query = session_manager.get_data("test_session", "refined_query")
        
        assert searched_videos is not None
        assert len(searched_videos) == 3
        assert refined_query == "python programming tutorial"
    
    def test_search_videos_no_results(self, client, mock_env, mock_video_fetcher, mock_openai):
        """Test search with no video results."""
        with patch('backend.routers.search.VideoFetcher') as MockFetcher:
            mock_instance = MagicMock()
            mock_instance.search_videos.return_value = []
            MockFetcher.return_value = mock_instance
            
            response = client.post("/search/videos", json={
                "topic": "very obscure topic xyz123"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == False
            assert "No videos found" in data["error"]


class TestSearchEndpointAPIKeyValidation:
    """Test API key validation for search endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    def test_search_without_youtube_key(self, client):
        """Test search fails without YouTube API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake"}, clear=True):
            # Ensure YOUTUBE_API_KEY is not set
            os.environ.pop("YOUTUBE_API_KEY", None)
            
            response = client.post("/search/videos", json={
                "topic": "Python tutorial"
            })
            
            assert response.status_code == 400
            assert "YOUTUBE_API_KEY" in response.json()["detail"]
    
    def test_search_without_openai_key(self, client):
        """Test search fails without OpenAI API key."""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "fake"}, clear=True):
            # Ensure OPENAI_API_KEY is not set
            os.environ.pop("OPENAI_API_KEY", None)
            
            response = client.post("/search/videos", json={
                "topic": "Python tutorial"
            })
            
            assert response.status_code == 400
            assert "OPENAI_API_KEY" in response.json()["detail"]


class TestWorkflowWithSelectedVideos:
    """Test workflow endpoint with pre-selected videos."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from backend.main import app
        return TestClient(app)
    
    def test_workflow_request_accepts_selected_video_ids(self, client):
        """Test that workflow request schema accepts selected_video_ids."""
        from backend.models.schemas import FullWorkflowRequest
        
        # Should not raise validation error
        request = FullWorkflowRequest(
            topic="Python tutorial",
            selected_video_ids=["vid1", "vid2", "vid3"]
        )
        
        assert request.selected_video_ids == ["vid1", "vid2", "vid3"]
    
    def test_workflow_request_without_selected_videos(self, client):
        """Test that selected_video_ids is optional."""
        from backend.models.schemas import FullWorkflowRequest
        
        request = FullWorkflowRequest(topic="Python tutorial")
        
        assert request.selected_video_ids is None


class TestVideoItemSchema:
    """Test VideoItem schema."""
    
    def test_video_item_creation(self):
        """Test VideoItem can be created with all fields."""
        from backend.models.schemas import VideoItem
        
        video = VideoItem(
            video_id="test123",
            title="Test Video",
            channel="Test Channel",
            channel_id="ch123",
            views=100000,
            likes=5000,
            comments=200,
            duration=600,
            score=1.5
        )
        
        assert video.video_id == "test123"
        assert video.title == "Test Video"
        assert video.views == 100000
        assert video.score == 1.5
    
    def test_video_item_default_score(self):
        """Test VideoItem has default score of 0."""
        from backend.models.schemas import VideoItem
        
        video = VideoItem(
            video_id="test123",
            title="Test Video",
            channel="Test Channel",
            channel_id="ch123",
            views=100000,
            likes=5000,
            comments=200,
            duration=600
        )
        
        assert video.score == 0.0


class TestSearchVideosResponseSchema:
    """Test SearchVideosResponse schema."""
    
    def test_response_with_videos(self):
        """Test response with video list."""
        from backend.models.schemas import SearchVideosResponse, VideoItem
        
        videos = [
            VideoItem(
                video_id="v1",
                title="Video 1",
                channel="Channel 1",
                channel_id="c1",
                views=100,
                likes=10,
                comments=5,
                duration=300
            )
        ]
        
        response = SearchVideosResponse(
            success=True,
            refined_query="test query",
            original_query="test",
            videos=videos
        )
        
        assert response.success == True
        assert len(response.videos) == 1
        assert response.error is None
    
    def test_response_with_error(self):
        """Test response with error."""
        from backend.models.schemas import SearchVideosResponse
        
        response = SearchVideosResponse(
            success=False,
            error="No videos found"
        )
        
        assert response.success == False
        assert response.videos is None
        assert response.error == "No videos found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

