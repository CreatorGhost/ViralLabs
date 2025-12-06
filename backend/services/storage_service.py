"""
Unified storage service supporting local filesystem and CloudFlare R2.
Provides a single interface for all file storage operations.
"""

import io
from pathlib import Path
from typing import BinaryIO, Optional, Union
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

from backend.core.config import settings, BASE_DIR


class StorageService:
    """
    Unified storage service that supports both local and R2 storage.
    Storage mode is determined by settings.storage_mode ("local" or "r2").
    """
    
    def __init__(self):
        self.mode = settings.storage_mode
        self._s3_client = None
        
        # Local storage base directory
        self.local_base = BASE_DIR / "uploads"
        self.local_base.mkdir(exist_ok=True)
    
    @property
    def s3_client(self):
        """Lazy initialization of S3 client for R2."""
        if self._s3_client is None and self.mode == "r2":
            if not settings.r2_account_id or not settings.r2_access_key_id:
                raise ValueError(
                    "R2 credentials not configured. Set R2_ACCOUNT_ID, "
                    "R2_ACCESS_KEY_ID, and R2_SECRET_ACCESS_KEY in .env"
                )
            self._s3_client = boto3.client(
                "s3",
                endpoint_url=settings.r2_endpoint_url,
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key,
            )
        return self._s3_client
    
    async def upload(
        self,
        file_data: Union[BinaryIO, bytes],
        key: str,
        content_type: str,
    ) -> dict:
        """
        Upload file to storage (local or R2 based on config).
        
        Args:
            file_data: File bytes or file-like object
            key: Storage key/path (e.g., "faces/user123/face_abc.png")
            content_type: MIME type of the file
            
        Returns:
            dict with storage_type, storage_key, storage_url
        """
        if self.mode == "local":
            return self._upload_local(file_data, key)
        else:
            return self._upload_r2(file_data, key, content_type)
    
    def _upload_local(self, file_data: Union[BinaryIO, bytes], key: str) -> dict:
        """Upload file to local filesystem."""
        path = self.local_base / key
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle both bytes and file-like objects
        if isinstance(file_data, bytes):
            data = file_data
        else:
            data = file_data.read()
        
        with open(path, "wb") as f:
            f.write(data)
        
        return {
            "storage_type": "local",
            "storage_key": str(path),
            "storage_url": f"/uploads/{key}",
        }
    
    def _upload_r2(
        self, 
        file_data: Union[BinaryIO, bytes], 
        key: str, 
        content_type: str
    ) -> dict:
        """Upload file to CloudFlare R2."""
        # Handle both bytes and file-like objects
        if isinstance(file_data, bytes):
            file_obj = io.BytesIO(file_data)
        else:
            file_obj = file_data
        
        self.s3_client.upload_fileobj(
            file_obj,
            settings.r2_bucket_name,
            key,
            ExtraArgs={"ContentType": content_type}
        )
        
        # Construct public URL
        public_url = f"{settings.r2_public_url}/{key}"
        
        return {
            "storage_type": "r2",
            "storage_key": key,
            "storage_url": public_url,
        }
    
    async def upload_from_path(
        self,
        local_path: Path,
        key: str,
        content_type: str,
    ) -> dict:
        """
        Upload a file from a local path to storage.
        Useful for uploading generated files (thumbnails, audio).
        
        Args:
            local_path: Path to the local file
            key: Storage key/path
            content_type: MIME type
            
        Returns:
            dict with storage_type, storage_key, storage_url
        """
        with open(local_path, "rb") as f:
            return await self.upload(f, key, content_type)
    
    async def delete(self, storage_type: str, storage_key: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            storage_type: "local" or "r2"
            storage_key: The key/path used when uploading
            
        Returns:
            True if deleted successfully
        """
        try:
            if storage_type == "local":
                path = Path(storage_key)
                if path.exists():
                    path.unlink()
                    return True
            else:
                self.s3_client.delete_object(
                    Bucket=settings.r2_bucket_name,
                    Key=storage_key
                )
                return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
        
        return False
    
    def get_url(
        self, 
        storage_type: str, 
        storage_key: str, 
        storage_url: Optional[str] = None
    ) -> str:
        """
        Get accessible URL for a file.
        
        Args:
            storage_type: "local" or "r2"
            storage_key: The storage key/path
            storage_url: Pre-computed URL (returned as-is if provided)
            
        Returns:
            Accessible URL string
        """
        if storage_url:
            return storage_url
        
        if storage_type == "r2":
            return f"{settings.r2_public_url}/{storage_key}"
        else:
            # For local, return the API route path
            return f"/uploads/{storage_key}"
    
    def generate_key(
        self, 
        file_type: str, 
        user_id: str, 
        filename: str,
        extension: str = ""
    ) -> str:
        """
        Generate a storage key with proper structure.
        
        Args:
            file_type: Type of file ("faces", "thumbnails", "audio")
            user_id: User's UUID string
            filename: Base filename
            extension: File extension (e.g., ".png", ".mp3")
            
        Returns:
            Storage key like "faces/user123/face_abc.png"
        """
        if not extension.startswith(".") and extension:
            extension = f".{extension}"
        
        return f"{file_type}/{user_id}/{filename}{extension}"


# Global storage service instance
storage_service = StorageService()

