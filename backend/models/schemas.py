"""
Pydantic schemas for API request/response validation.
Single Responsibility: Only defines data shapes.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# ===== Authentication Models =====

class SignupRequest(BaseModel):
    """Request model for user signup."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="User's full name")


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str = Field(..., description="The refresh token")


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires


class UserResponse(BaseModel):
    """Response model for user data."""
    id: UUID
    email: str
    full_name: str
    is_premium: bool
    premium_expires_at: Optional[datetime] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Response model for successful authentication."""
    success: bool
    user: Optional[UserResponse] = None
    tokens: Optional[TokenResponse] = None
    error: Optional[str] = None


class SessionInfo(BaseModel):
    """Information about an active session."""
    id: UUID
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_used_at: datetime

    model_config = {"from_attributes": True}


class ActiveSessionsResponse(BaseModel):
    """Response model for active sessions list."""
    sessions: List[SessionInfo]
    count: int


# ===== Request Models =====

class ScriptGenerateRequest(BaseModel):
    """Request model for script generation."""
    topic: str = Field(..., min_length=3, description="Video topic/query")
    model: str = Field(default="gpt-5.1", description="LLM model for script generation")
    refine_model: str = Field(default="gpt-5-nano", description="Model for query refinement")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Creativity level")
    max_videos: int = Field(default=15, ge=5, le=30, description="Max videos to search")
    top_n_videos: int = Field(default=5, ge=3, le=15, description="Top videos to analyze")
    subscriber_threshold: int = Field(default=50000, ge=0, description="Min subscribers")
    max_workers: int = Field(default=5, ge=1, le=10, description="Parallel workers")
    selected_video_ids: Optional[List[str]] = Field(default=None, description="Pre-selected video IDs (skips search if provided)")


class ScriptRegenerateRequest(BaseModel):
    """Request model for script regeneration using existing transcripts."""
    original_query: str
    refined_query: str
    combined_transcripts: str
    video_count: int
    model: str = Field(default="gpt-5.1")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class ThumbnailGenerateRequest(BaseModel):
    """Request model for thumbnail generation."""
    topic: str = Field(..., min_length=3, description="Video topic/title")
    num_thumbnails: int = Field(default=3, ge=1, le=5, description="Number of thumbnails")
    resolution: str = Field(default="2K", description="Resolution (1K, 2K, 4K)")
    use_reference_images: bool = Field(default=False, description="Use reference images from YouTube")
    youtube_video_ids: Optional[List[str]] = Field(default=None, description="YouTube video IDs to download thumbnails as references")
    include_face: bool = Field(default=False, description="Include uploaded face")
    face_mode: str = Field(default="auto", description="Face mode: auto, center, left, right")
    face_style: str = Field(default="realistic", description="Face style: realistic, professional, cartoon")


class ThumbnailRegenerateRequest(BaseModel):
    """Request model for thumbnail regeneration."""
    topic: str
    num_thumbnails: int = Field(default=3, ge=1, le=5)
    resolution: str = Field(default="2K")
    use_reference_images: bool = Field(default=False)
    youtube_video_ids: Optional[List[str]] = Field(default=None)
    include_face: bool = Field(default=False)
    face_mode: str = Field(default="auto")
    face_style: str = Field(default="realistic")


class FullWorkflowRequest(BaseModel):
    """Request model for complete workflow (script + thumbnails)."""
    topic: str = Field(..., min_length=3)
    # Script settings
    model: str = Field(default="gpt-5.1")
    refine_model: str = Field(default="gpt-5-nano")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_videos: int = Field(default=15, ge=5, le=30)
    top_n_videos: int = Field(default=5, ge=3, le=15)
    subscriber_threshold: int = Field(default=50000, ge=0)
    max_workers: int = Field(default=5, ge=1, le=10)
    selected_video_ids: Optional[List[str]] = Field(default=None, description="Pre-selected video IDs (skips search if provided)")
    # Thumbnail settings
    enable_thumbnails: bool = Field(default=True)
    num_thumbnails: int = Field(default=3, ge=1, le=5)
    resolution: str = Field(default="2K")
    use_reference_images: bool = Field(default=False)
    include_face: bool = Field(default=False)
    face_mode: str = Field(default="auto")
    face_style: str = Field(default="realistic")


# ===== Video Search Models =====

class SearchVideosRequest(BaseModel):
    """Request model for video search (step 1 of video selection)."""
    topic: str = Field(..., min_length=3, description="Video topic/query")
    max_videos: int = Field(default=15, ge=5, le=30, description="Max videos to search")
    subscriber_threshold: int = Field(default=50000, ge=0, description="Min subscribers")
    refine_model: str = Field(default="gpt-5-nano", description="Model for query refinement")


class VideoItem(BaseModel):
    """Individual video item with metadata."""
    video_id: str
    title: str
    channel: str
    channel_id: str
    views: int
    likes: int
    comments: int
    duration: int  # seconds
    score: float = 0.0
    thumbnail_url: str = ""  # YouTube thumbnail URL


class SearchVideosResponse(BaseModel):
    """Response model for video search."""
    success: bool
    refined_query: Optional[str] = None
    original_query: Optional[str] = None
    videos: Optional[List[VideoItem]] = None
    error: Optional[str] = None


# ===== Response Models =====

class ScriptResponse(BaseModel):
    """Response model for script generation."""
    success: bool
    script: Optional[str] = None
    refined_query: Optional[str] = None
    original_query: Optional[str] = None
    videos_analyzed: Optional[int] = None
    stats: Optional[dict] = None
    metadata: Optional[dict] = None
    combined_transcripts: Optional[str] = None
    error: Optional[str] = None


class ThumbnailResponse(BaseModel):
    """Response model for thumbnail generation."""
    success: bool
    thumbnails: Optional[List[dict]] = None
    successful_count: Optional[int] = None
    error: Optional[str] = None


class FullWorkflowResponse(BaseModel):
    """Response model for full workflow."""
    success: bool
    script: Optional[ScriptResponse] = None
    thumbnails: Optional[ThumbnailResponse] = None
    error: Optional[str] = None


class FaceUploadResponse(BaseModel):
    """Response model for face upload."""
    success: bool
    face_id: Optional[str] = None
    filepath: Optional[str] = None
    error: Optional[str] = None


class SessionState(BaseModel):
    """Model representing session state."""
    has_face: bool = False
    face_id: Optional[str] = None
    face_path: Optional[str] = None
    last_script: Optional[dict] = None
    last_thumbnails: Optional[List[dict]] = None


# ===== Audio Models =====

class AudioGenerateRequest(BaseModel):
    """Request model for audio generation from script text."""
    script: str = Field(..., min_length=1, description="Script text to convert to audio")
    voice: str = Field(default="female", description="Voice gender (male or female)")
    persona: str = Field(default="storyteller", description="Persona preset ID (storyteller, anime, tech, etc.)")
    custom_instructions: Optional[str] = Field(default=None, description="Custom voice instructions (overrides persona)")
    filename: Optional[str] = Field(default=None, description="Custom filename without extension")


class AudioGenerateFromSessionRequest(BaseModel):
    """Request model for audio generation from session's last script."""
    voice: str = Field(default="female", description="Voice gender (male or female)")
    persona: str = Field(default="storyteller", description="Persona preset ID")
    custom_instructions: Optional[str] = Field(default=None, description="Custom voice instructions")


class AudioResponse(BaseModel):
    """Response model for audio generation."""
    success: bool
    filepath: Optional[str] = None
    filename: Optional[str] = None
    audio_url: Optional[str] = None
    voice: Optional[str] = None
    persona: Optional[str] = None
    persona_name: Optional[str] = None
    model: Optional[str] = None
    script_length: Optional[int] = None
    chunks_processed: Optional[int] = None  # Number of chunks if script was split
    error: Optional[str] = None


class PersonaInfo(BaseModel):
    """Persona information for audio generation."""
    id: str
    name: str
    description: str
    icon: str


class AudioOptionsResponse(BaseModel):
    """Response model for available audio options."""
    voices: List[str]
    personas: List[PersonaInfo]

