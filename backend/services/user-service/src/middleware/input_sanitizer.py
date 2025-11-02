"""Input sanitization middleware to prevent XSS and injection attacks"""
import bleach
import re
from typing import Any, Dict
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Allowed HTML tags (empty = strip all)
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}

class InputSanitizer:
    """Sanitize all string inputs to prevent XSS/injection"""
    
    def __init__(self):
        self.max_string_length = 10000  # 10KB
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',                 # JavaScript protocol
            r'on\w+\s*=',                  # Event handlers (onclick, etc)
            r'<iframe[^>]*>.*?</iframe>',  # Iframes
        ]
    
    async def __call__(self, request: Request, call_next):
        """Sanitize request body if it's JSON"""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body and request.headers.get("content-type") == "application/json":
                    import json
                    data = json.loads(body)
                    sanitized = self._sanitize_dict(data)
                    
                    # Replace request body with sanitized version
                    async def receive():
                        return {"type": "http.request", "body": json.dumps(sanitized).encode()}
                    
                    request._receive = receive
            except Exception as e:
                logger.error(f"Sanitization error: {e}")
        
        response = await call_next(request)
        return response
    
    def _sanitize_dict(self, data: Dict) -> Dict:
        """Recursively sanitize dictionary"""
        if isinstance(data, dict):
            return {k: self._sanitize_value(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_value(item) for item in data]
        else:
            return self._sanitize_value(data)
    
    def _sanitize_value(self, value: Any) -> Any:
        """Sanitize individual value"""
        if isinstance(value, str):
            return self._sanitize_string(value)
        elif isinstance(value, dict):
            return self._sanitize_dict(value)
        elif isinstance(value, list):
            return [self._sanitize_value(item) for item in value]
        else:
            return value
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize string value"""
        # Length check
        if len(text) > self.max_string_length:
            text = text[:self.max_string_length]
        
        # Strip HTML tags
        text = bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
        
        # Remove dangerous patterns
        for pattern in self.dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()

input_sanitizer = InputSanitizer()
