"""
Token service for creating and verifying JWT tokens
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from .config import settings
import secrets

class TokenService:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = "HS256"
    
    def create_verification_token(self, user_id: str, email: str) -> str:
        """Create email verification token (24h validity)"""
        payload = {
            "user_id": user_id,
            "email": email,
            "type": "email_verification",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_verification_token(self, token: str) -> Optional[Dict]:
        """Verify email verification token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "email_verification":
                return None
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
    
    def create_password_reset_token(self, user_id: str, email: str) -> str:
        """Create password reset token (1h validity)"""
        payload = {
            "user_id": user_id,
            "email": email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_reset_token(self, token: str) -> Optional[Dict]:
        """Verify password reset token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "password_reset":
                return None
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token (30 days validity)"""
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=30),
            "jti": secrets.token_urlsafe(32)  # Unique token ID for revocation
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_refresh_token(self, token: str) -> Optional[Dict]:
        """Verify refresh token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "refresh":
                return None
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

# Global instance
token_service = TokenService()
