"""
SQLAlchemy ORM models for database tables.
Defines all database entities and their relationships.
"""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Boolean, Integer, Text, DateTime, ForeignKey, Index, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.core.database import Base


class User(Base):
    """User accounts and subscription status."""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Relationships
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    user_state: Mapped[Optional["UserState"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan",
        uselist=False
    )
    media_files: Mapped[List["MediaFile"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    generations: Mapped[List["Generation"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    """Long-lived refresh tokens for session persistence (max 5 per user)."""
    __tablename__ = "refresh_tokens"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
    
    # Indexes
    __table_args__ = (
        Index("idx_refresh_tokens_user", "user_id"),
    )


class UserState(Base):
    """
    Replaces in-memory SessionManager.
    Stores user preferences and current state (face uploads, etc.)
    """
    __tablename__ = "user_state"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    current_face_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="user_state")


class MediaFile(Base):
    """
    All uploaded/generated files (faces, thumbnails, audio).
    Ready for CloudFlare R2 migration.
    """
    __tablename__ = "media_files"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # face, thumbnail, audio
    storage_type: Mapped[str] = mapped_column(String(20), default="local")  # local, r2
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)  # Path or R2 key
    storage_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  # Public URL
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="media_files")
    
    # Indexes
    __table_args__ = (
        Index("idx_media_user", "user_id"),
        Index("idx_media_type", "file_type"),
    )


class Generation(Base):
    """
    All AI generations (scripts, thumbnails, audio, tags, titles, descriptions).
    Stores input settings and output data.
    """
    __tablename__ = "generations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    generation_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )  # script, thumbnail, audio, workflow, tags, title, description
    topic: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    input_settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    output_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    related_media_ids: Mapped[Optional[List[uuid.UUID]]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), 
        nullable=True
    )
    parent_generation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generations.id"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        default="completed"
    )  # pending, processing, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="generations")
    parent_generation: Mapped[Optional["Generation"]] = relationship(
        remote_side=[id],
        backref="child_generations"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_generations_user", "user_id"),
        Index("idx_generations_type", "generation_type"),
        Index("idx_generations_created", "created_at"),
    )

