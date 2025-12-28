"""
Cloud Storage Manager - Handles media file uploads and management
"""

import os
import io
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, BinaryIO
from pathlib import Path

from google.cloud import storage
from google.cloud.storage import Blob, Bucket
from PIL import Image as PILImage

from src.monitoring.logger import StructuredLogger


class CloudStorageManager:
    """Manages media storage in Google Cloud Storage"""
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        """
        Initialize Cloud Storage Manager
        
        Args:
            bucket_name: GCS bucket name (defaults to env var)
            project_id: GCP project ID (defaults to env var)
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.bucket_name = bucket_name or os.getenv('GCS_MEDIA_BUCKET', f'{self.project_id}-media')
        
        self.logger = StructuredLogger(name="infrastructure.storage")
        
        # Initialize storage client
        self.client = storage.Client(project=self.project_id)
        
        # Get or create bucket
        self.bucket = self._get_or_create_bucket()
    
    def _get_or_create_bucket(self) -> Bucket:
        """Get existing bucket or create new one"""
        try:
            bucket = self.client.get_bucket(self.bucket_name)
            self.logger.info(
                "Using existing bucket",
                bucket_name=self.bucket_name
            )
            return bucket
        except Exception as e:
            self.logger.info(
                "Bucket not found, creating new bucket",
                bucket_name=self.bucket_name
            )
            return self._create_bucket()
    
    def _create_bucket(self) -> Bucket:
        """Create new GCS bucket with optimal settings"""
        bucket = self.client.bucket(self.bucket_name)
        
        # Set bucket location (multi-region for better availability)
        bucket.location = 'US'
        
        # Set storage class (Standard for frequently accessed media)
        bucket.storage_class = 'STANDARD'
        
        # Enable uniform bucket-level access
        bucket.iam_configuration.uniform_bucket_level_access_enabled = True
        
        # Create the bucket
        bucket = self.client.create_bucket(bucket)
        
        # Set lifecycle policy (archive old files)
        self._set_lifecycle_policy(bucket)
        
        # Enable CORS for web access
        self._set_cors_policy(bucket)
        
        self.logger.info(
            "Created new bucket",
            bucket_name=self.bucket_name,
            location=bucket.location
        )
        
        return bucket
    
    def _set_lifecycle_policy(self, bucket: Bucket) -> None:
        """Set lifecycle rules for automatic archival"""
        rules = [
            {
                'action': {'type': 'SetStorageClass', 'storageClass': 'NEARLINE'},
                'condition': {'age': 30}  # Move to Nearline after 30 days
            },
            {
                'action': {'type': 'SetStorageClass', 'storageClass': 'COLDLINE'},
                'condition': {'age': 90}  # Move to Coldline after 90 days
            },
            {
                'action': {'type': 'Delete'},
                'condition': {'age': 365}  # Delete after 1 year (optional)
            }
        ]
        
        bucket.lifecycle_rules = rules
        bucket.patch()
    
    def _set_cors_policy(self, bucket: Bucket) -> None:
        """Enable CORS for web access"""
        cors_config = [
            {
                'origin': ['*'],
                'method': ['GET', 'HEAD'],
                'responseHeader': ['Content-Type'],
                'maxAgeSeconds': 3600
            }
        ]
        
        bucket.cors = cors_config
        bucket.patch()
    
    def upload_image(
        self,
        image: PILImage.Image,
        project_id: str,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        optimize: bool = True,
        quality: int = 85
    ) -> Dict[str, Any]:
        """
        Upload PIL Image to Cloud Storage
        
        Args:
            image: PIL Image object
            project_id: Project ID for organization
            filename: Optional custom filename
            metadata: Optional metadata dict
            optimize: Whether to optimize image before upload
            quality: JPEG quality (1-100)
            
        Returns:
            Upload result with URL and metadata
        """
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"image_{timestamp}.jpg"
        
        # Ensure proper file extension
        if not any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            filename = f"{filename}.jpg"
        
        # Create blob path
        blob_path = f"projects/{project_id}/images/{filename}"
        
        # Optimize image if requested
        if optimize:
            image = self._optimize_image(image, quality)
        
        # Convert to bytes
        img_byte_array = io.BytesIO()
        image_format = 'JPEG' if filename.endswith(('.jpg', '.jpeg')) else 'PNG'
        image.save(img_byte_array, format=image_format, quality=quality, optimize=True)
        img_byte_array.seek(0)
        
        # Upload to GCS
        result = self.upload_file(
            file_obj=img_byte_array,
            blob_path=blob_path,
            content_type=f'image/{image_format.lower()}',
            metadata=metadata
        )
        
        # Add image-specific metadata
        result['dimensions'] = {
            'width': image.width,
            'height': image.height
        }
        result['format'] = image_format
        
        return result
    
    def upload_file(
        self,
        file_obj: BinaryIO,
        blob_path: str,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None,
        cache_control: str = 'public, max-age=3600'
    ) -> Dict[str, Any]:
        """
        Upload file to Cloud Storage
        
        Args:
            file_obj: File-like object to upload
            blob_path: Destination path in bucket
            content_type: MIME type
            metadata: Optional metadata
            cache_control: Cache control header
            
        Returns:
            Upload result
        """
        blob = self.bucket.blob(blob_path)
        
        # Set metadata
        if metadata:
            blob.metadata = metadata
        
        # Set cache control
        blob.cache_control = cache_control
        
        # Upload
        blob.upload_from_file(
            file_obj,
            content_type=content_type,
            rewind=True
        )
        
        # Generate public URL (signed URL for security or public URL)
        public_url = blob.public_url
        
        # Try to generate signed URL (requires service account credentials)
        signed_url = None
        try:
            signed_url = blob.generate_signed_url(
                version='v4',
                expiration=timedelta(days=7),
                method='GET'
            )
        except (AttributeError, ValueError) as e:
            # User doesn't have service account credentials, skip signed URL
            self.logger.warning(
                "Could not generate signed URL (requires service account)",
                error=str(e)
            )
        
        self.logger.info(
            "Uploaded file to Cloud Storage",
            blob_path=blob_path,
            size_bytes=blob.size,
            content_type=content_type
        )
        
        return {
            'blob_path': blob_path,
            'bucket': self.bucket_name,
            'public_url': public_url,
            'signed_url': signed_url,
            'size_bytes': blob.size,
            'content_type': content_type,
            'metadata': blob.metadata,
            'created': blob.time_created,
            'md5_hash': blob.md5_hash
        }
    
    def upload_from_local(
        self,
        local_path: str,
        blob_path: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file from local filesystem
        
        Args:
            local_path: Path to local file
            blob_path: Destination path (auto-generated if None)
            project_id: Project ID for organization
            
        Returns:
            Upload result
        """
        local_file = Path(local_path)
        
        if not local_file.exists():
            raise FileNotFoundError(f"File not found: {local_path}")
        
        # Generate blob path if not provided
        if not blob_path:
            if project_id:
                file_type = self._get_file_type(local_file.suffix)
                blob_path = f"projects/{project_id}/{file_type}/{local_file.name}"
            else:
                blob_path = f"uploads/{local_file.name}"
        
        # Determine content type
        content_type = self._get_content_type(local_file.suffix)
        
        # Upload
        with open(local_file, 'rb') as f:
            return self.upload_file(f, blob_path, content_type)
    
    def download_file(
        self,
        blob_path: str,
        local_path: Optional[str] = None
    ) -> bytes:
        """
        Download file from Cloud Storage
        
        Args:
            blob_path: Path to blob in bucket
            local_path: Optional local path to save file
            
        Returns:
            File contents as bytes
        """
        blob = self.bucket.blob(blob_path)
        
        if not blob.exists():
            raise FileNotFoundError(f"Blob not found: {blob_path}")
        
        # Download to memory
        content = blob.download_as_bytes()
        
        # Optionally save to local file
        if local_path:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(content)
            
            self.logger.info(
                "Downloaded file from Cloud Storage",
                blob_path=blob_path,
                local_path=local_path
            )
        
        return content
    
    def delete_file(self, blob_path: str) -> bool:
        """Delete file from Cloud Storage"""
        blob = self.bucket.blob(blob_path)
        
        if blob.exists():
            blob.delete()
            self.logger.info("Deleted file", blob_path=blob_path)
            return True
        
        return False
    
    def list_files(
        self,
        prefix: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in bucket
        
        Args:
            prefix: Optional prefix to filter by
            project_id: Optional project ID to filter by
            
        Returns:
            List of file metadata
        """
        if project_id and not prefix:
            prefix = f"projects/{project_id}/"
        
        blobs = self.bucket.list_blobs(prefix=prefix)
        
        files = []
        for blob in blobs:
            files.append({
                'name': blob.name,
                'size_bytes': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'public_url': blob.public_url,
                'md5_hash': blob.md5_hash
            })
        
        return files
    
    def _optimize_image(
        self,
        image: PILImage.Image,
        quality: int = 85,
        max_dimension: int = 2048
    ) -> PILImage.Image:
        """Optimize image for web delivery"""
        # Resize if too large
        if max(image.size) > max_dimension:
            ratio = max_dimension / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, PILImage.Resampling.LANCZOS)
        
        # Convert RGBA to RGB if needed
        if image.mode == 'RGBA':
            background = PILImage.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        
        return image
    
    def _get_content_type(self, extension: str) -> str:
        """Get MIME type from file extension"""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.pdf': 'application/pdf',
            '.json': 'application/json',
            '.txt': 'text/plain'
        }
        
        return content_types.get(extension.lower(), 'application/octet-stream')
    
    def _get_file_type(self, extension: str) -> str:
        """Determine file type category from extension"""
        if extension.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'images'
        elif extension.lower() in ['.mp4', '.webm', '.mov', '.avi']:
            return 'videos'
        elif extension.lower() in ['.mp3', '.wav', '.ogg', '.m4a']:
            return 'audio'
        else:
            return 'files'
    
    def get_storage_stats(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get storage statistics"""
        prefix = f"projects/{project_id}/" if project_id else None
        
        blobs = self.bucket.list_blobs(prefix=prefix)
        
        total_size = 0
        file_count = 0
        file_types = {}
        
        for blob in blobs:
            total_size += blob.size or 0
            file_count += 1
            
            # Count by type
            content_type = blob.content_type or 'unknown'
            file_types[content_type] = file_types.get(content_type, 0) + 1
        
        return {
            'total_files': file_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_types': file_types,
            'bucket': self.bucket_name,
            'project_filter': project_id
        }
