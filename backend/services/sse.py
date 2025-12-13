"""
Server-Sent Events (SSE) service.
Single Responsibility: Only handles SSE message formatting.
"""

import json
from typing import Dict, Any, Optional


class SSEService:
    """Service for formatting Server-Sent Events."""
    
    # Event types
    PROGRESS = "progress"
    SCRIPT_CHUNK = "script_chunk"
    THUMBNAIL = "thumbnail"
    COMPLETE = "complete"
    ERROR = "error"
    
    # Step names
    STEP_REFINING = "refining"
    STEP_SEARCHING = "searching"
    STEP_RANKING = "ranking"
    STEP_TRANSCRIPTS = "transcripts"
    STEP_GENERATING = "generating"
    STEP_THUMBNAILS = "thumbnails"
    STEP_COMPLETE = "complete"
    STEP_INITIALIZING = "initializing"
    
    @staticmethod
    def format_event(
        event_type: str,
        step: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format a Server-Sent Event message.
        
        Args:
            event_type: Type of event (progress, script_chunk, thumbnail, complete, error)
            step: Current step name
            message: Human-readable message
            data: Additional data payload
            
        Returns:
            Properly formatted SSE string
        """
        payload = {
            "type": event_type,
            "step": step,
            "message": message,
            "data": data or {}
        }
        return f"data: {json.dumps(payload)}\n\n"
    
    @classmethod
    def progress(cls, step: str, message: str, data: Optional[Dict] = None) -> str:
        """Create a progress event."""
        return cls.format_event(cls.PROGRESS, step, message, data)
    
    @classmethod
    def script_chunk(cls, chunk: str) -> str:
        """Create a script chunk event."""
        return cls.format_event(cls.SCRIPT_CHUNK, cls.STEP_GENERATING, "", {"chunk": chunk})
    
    @classmethod
    def thumbnail(cls, index: int, url: str, filepath: str, current: int, total: int) -> str:
        """Create a thumbnail completion event."""
        return cls.format_event(
            cls.THUMBNAIL,
            cls.STEP_THUMBNAILS,
            f"Thumbnail {index} ready",
            {
                "index": index,
                "url": url,
                "filepath": filepath,
                "current": current,
                "total": total
            }
        )
    
    @classmethod
    def complete(cls, data: Dict[str, Any]) -> str:
        """Create a completion event."""
        return cls.format_event(cls.COMPLETE, cls.STEP_COMPLETE, "Workflow complete!", data)
    
    @classmethod
    def error(cls, step: str, message: str, error_details: Optional[str] = None) -> str:
        """Create an error event."""
        return cls.format_event(
            cls.ERROR,
            step,
            message,
            {"error": error_details or message, "step": step}
        )


# Convenience function for backward compatibility
def sse_event(event_type: str, step: str, message: str, data: Optional[Dict] = None) -> str:
    """Format a Server-Sent Event message (convenience function)."""
    return SSEService.format_event(event_type, step, message, data)







