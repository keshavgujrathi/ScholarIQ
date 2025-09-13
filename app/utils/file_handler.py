"""
File Handler Module

This module provides utilities for file operations including upload, download,
validation, and processing of files in the ScholarIQ application.
"""

import os
import shutil
import mimetypes
import magic
import hashlib
from pathlib import Path
from enum import Enum
from typing import Optional, Tuple, BinaryIO, Dict, Any, List, Union
from datetime import datetime
import logging

from fastapi import UploadFile, HTTPException, status

logger = logging.getLogger(__name__)


class FileType(str, Enum):
    """Supported file types for upload and processing."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


class FileOperationError(Exception):
    """Exception raised for file operation errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class FileHandler:
    """
    Handler for file operations including validation, storage, and processing.
    """
    
    # Default allowed file extensions by type
    ALLOWED_EXTENSIONS = {
        FileType.TEXT: ['.txt', '.md', '.csv', '.json', '.xml', '.yaml', '.yml'],
        FileType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
        FileType.AUDIO: ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
        FileType.VIDEO: ['.mp4', '.webm', '.mov', '.avi', '.mkv'],
        FileType.DOCUMENT: ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.odt'],
        FileType.ARCHIVE: ['.zip', '.tar', '.gz', '.rar', '.7z'],
    }
    
    # Default maximum file sizes in bytes (10MB for most files, 100MB for videos)
    DEFAULT_MAX_SIZES = {
        FileType.TEXT: 10 * 1024 * 1024,      # 10MB
        FileType.IMAGE: 10 * 1024 * 1024,     # 10MB
        FileType.AUDIO: 50 * 1024 * 1024,     # 50MB
        FileType.VIDEO: 100 * 1024 * 1024,    # 100MB
        FileType.DOCUMENT: 20 * 1024 * 1024,  # 20MB
        FileType.ARCHIVE: 50 * 1024 * 1024,   # 50MB
        FileType.OTHER: 5 * 1024 * 1024,      # 5MB
    }
    
    def __init__(self, base_path: str = "data/uploads"):
        """
        Initialize the file handler with a base storage path.
        
        Args:
            base_path: Base directory for file storage.
        """
        self.base_path = Path(base_path).resolve()
        self.ensure_directory_exists(self.base_path)
    
    @staticmethod
    def ensure_directory_exists(directory: Path) -> None:
        """Ensure that a directory exists, creating it if necessary."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create directory {directory}: {str(e)}")
            raise FileOperationError(
                f"Could not create directory: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_file_type(self, filename: str) -> FileType:
        """
        Determine the file type based on its extension.
        
        Args:
            filename: Name of the file.
            
        Returns:
            The detected file type.
        """
        ext = Path(filename).suffix.lower()
        
        for file_type, extensions in self.ALLOWED_EXTENSIONS.items():
            if ext in extensions:
                return file_type
        
        return FileType.OTHER
    
    def get_max_size(self, file_type: Union[FileType, str]) -> int:
        """
        Get the maximum allowed file size for a given file type.
        
        Args:
            file_type: The file type as a FileType enum or string.
            
        Returns:
            Maximum allowed size in bytes.
        """
        if isinstance(file_type, str):
            try:
                file_type = FileType(file_type.lower())
            except ValueError:
                file_type = FileType.OTHER
        
        return self.DEFAULT_MAX_SIZES.get(file_type, self.DEFAULT_MAX_SIZES[FileType.OTHER])
    
    def is_allowed_file(self, filename: str, allowed_types: Optional[List[FileType]] = None) -> bool:
        """
        Check if a file has an allowed extension.
        
        Args:
            filename: Name of the file.
            allowed_types: List of allowed file types. If None, all types are allowed.
            
        Returns:
            True if the file is allowed, False otherwise.
        """
        if not filename:
            return False
            
        file_type = self.get_file_type(filename)
        
        if allowed_types is None:
            return True
            
        return file_type in allowed_types
    
    async def save_upload_file(
        self,
        upload_file: UploadFile,
        subdirectory: str = "",
        allowed_types: Optional[List[FileType]] = None,
        max_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Save an uploaded file to the filesystem.
        
        Args:
            upload_file: The uploaded file from FastAPI.
            subdirectory: Optional subdirectory within the base path.
            allowed_types: List of allowed file types. If None, all types are allowed.
            max_size: Maximum file size in bytes. If None, uses default for file type.
            
        Returns:
            Dictionary containing file metadata.
            
        Raises:
            FileOperationError: If the file is not allowed or an error occurs.
        """
        try:
            # Validate file type
            if not self.is_allowed_file(upload_file.filename, allowed_types):
                raise FileOperationError(
                    f"File type not allowed: {upload_file.filename}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Determine file type and max size
            file_type = self.get_file_type(upload_file.filename)
            max_size = max_size or self.get_max_size(file_type)
            
            # Read file content to get size and hash
            content = await upload_file.read()
            
            # Check file size
            if len(content) > max_size:
                raise FileOperationError(
                    f"File too large: {len(content)} bytes (max {max_size} bytes)",
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                )
            
            # Generate a secure filename
            original_filename = Path(upload_file.filename).name
            file_ext = Path(original_filename).suffix
            safe_filename = self.generate_safe_filename(original_filename)
            
            # Create destination directory
            dest_dir = self.base_path / subdirectory
            self.ensure_directory_exists(dest_dir)
            
            # Generate a unique filename if the file already exists
            dest_path = dest_dir / safe_filename
            counter = 1
            while dest_path.exists():
                name = f"{dest_path.stem}_{counter}{dest_path.suffix}"
                dest_path = dest_path.with_name(name)
                counter += 1
            
            # Save the file
            with open(dest_path, "wb") as buffer:
                buffer.write(content)
            
            # Get file metadata
            file_hash = self.calculate_file_hash(dest_path)
            mime_type, _ = mimetypes.guess_type(original_filename)
            
            return {
                "filename": original_filename,
                "saved_as": dest_path.name,
                "path": str(dest_path.relative_to(self.base_path)),
                "size": len(content),
                "file_type": file_type.value,
                "mime_type": mime_type or "application/octet-stream",
                "hash": file_hash,
                "uploaded_at": datetime.utcnow().isoformat(),
            }
            
        except FileOperationError:
            raise
        except Exception as e:
            logger.error(f"Error saving file {upload_file.filename}: {str(e)}")
            raise FileOperationError(
                f"Failed to save file: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def generate_safe_filename(filename: str) -> str:
        """
        Generate a safe filename by removing or replacing unsafe characters.
        
        Args:
            filename: Original filename.
            
        Returns:
            Safe version of the filename.
        """
        # Keep only alphanumeric, dots, underscores, and hyphens
        safe_chars = "-_ .()"
        safe_name = "".join(
            c if c.isalnum() or c in safe_chars else "_" 
            for c in filename
        )
        
        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip(' .')
        
        # Ensure the filename is not empty
        if not safe_name:
            safe_name = f"file_{int(datetime.utcnow().timestamp())}"
        
        return safe_name
    
    @staticmethod
    def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
        """
        Calculate the hash of a file.
        
        Args:
            file_path: Path to the file.
            algorithm: Hash algorithm to use (default: sha256).
            
        Returns:
            The file's hash as a hexadecimal string.
        """
        hash_func = getattr(hashlib, algorithm, hashlib.sha256)
        
        with open(file_path, "rb") as f:
            file_hash = hash_func()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        
        return file_hash.hexdigest()
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get metadata about a file.
        
        Args:
            file_path: Path to the file, relative to base_path or absolute.
            
        Returns:
            Dictionary containing file metadata.
            
        Raises:
            FileOperationError: If the file doesn't exist or an error occurs.
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if not path.exists() or not path.is_file():
                raise FileOperationError("File not found", status_code=status.HTTP_404_NOT_FOUND)
            
            # Get file stats
            stat = path.stat()
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(path.name)
            
            return {
                "filename": path.name,
                "path": str(path.relative_to(self.base_path)),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "mime_type": mime_type or "application/octet-stream",
                "file_type": self.get_file_type(path.name).value,
                "hash": self.calculate_file_hash(path),
            }
            
        except FileOperationError:
            raise
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            raise FileOperationError(
                f"Failed to get file info: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file, relative to base_path or absolute.
            
        Returns:
            True if the file was deleted, False otherwise.
            
        Raises:
            FileOperationError: If an error occurs during deletion.
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            # Prevent directory traversal
            if not path.resolve().is_relative_to(self.base_path.resolve()):
                raise FileOperationError("Invalid file path", status_code=status.HTTP_400_BAD_REQUEST)
            
            if not path.exists():
                return False
                
            if path.is_file():
                path.unlink()
                return True
            else:
                raise FileOperationError("Path is not a file", status_code=status.HTTP_400_BAD_REQUEST)
                
        except FileOperationError:
            raise
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            raise FileOperationError(
                f"Failed to delete file: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list_files(
        self, 
        directory: str = "", 
        recursive: bool = False,
        file_types: Optional[List[FileType]] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in a directory.
        
        Args:
            directory: Directory path relative to base_path.
            recursive: Whether to list files recursively.
            file_types: Optional list of file types to include.
            
        Returns:
            List of file metadata dictionaries.
            
        Raises:
            FileOperationError: If the directory doesn't exist or an error occurs.
        """
        try:
            dir_path = self.base_path / directory
            
            if not dir_path.exists() or not dir_path.is_dir():
                raise FileOperationError("Directory not found", status_code=status.HTTP_404_NOT_FOUND)
            
            files = []
            
            if recursive:
                walk = dir_path.rglob('*')
            else:
                walk = dir_path.glob('*')
            
            for item in walk:
                if item.is_file():
                    file_type = self.get_file_type(item.name)
                    if file_types is None or file_type in file_types:
                        try:
                            files.append(self.get_file_info(item.relative_to(self.base_path)))
                        except Exception as e:
                            logger.warning(f"Could not get info for {item}: {str(e)}")
                            continue
            
            return files
            
        except FileOperationError:
            raise
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {str(e)}")
            raise FileOperationError(
                f"Failed to list files: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
