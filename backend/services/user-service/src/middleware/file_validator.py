"""File upload validation middleware"""
import magic
from fastapi import UploadFile, HTTPException
from typing import List
import logging

logger = logging.getLogger(__name__)

class FileValidator:
    """Validate uploaded files for security"""
    
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    async def validate_file(cls, file: UploadFile) -> bool:
        """Validate a single file upload"""
        # Check file size
        contents = await file.read()
        file_size = len(contents)
        await file.seek(0)  # Reset file pointer
        
        if file_size > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {cls.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Check MIME type
        mime_type = magic.from_buffer(contents, mime=True)
        if mime_type not in cls.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Detected: {mime_type}"
            )
        
        # Check filename extension
        if not cls._is_safe_filename(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )
        
        logger.info(f"File validated: {file.filename} ({mime_type}, {file_size} bytes)")
        return True
    
    @staticmethod
    def _is_safe_filename(filename: str) -> bool:
        """Check if filename is safe"""
        # No path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # Reasonable length
        if len(filename) > 255:
            return False
        
        # Has valid extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.doc', '.docx', '.txt']
        return any(filename.lower().endswith(ext) for ext in allowed_extensions)

file_validator = FileValidator()
