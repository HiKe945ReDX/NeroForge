"""NoSQL injection prevention for MongoDB queries"""
from typing import Any, Dict
import re
from ..utils.structured_logger import logger

class NoSQLInjectionGuard:
    """Prevent NoSQL injection in MongoDB queries"""
    
    # Dangerous MongoDB operators
    DANGEROUS_OPERATORS = {
        "$where", "$regex", "$expr", "$function",
        "$accumulator", "$let", "$map", "$reduce"
    }
    
    # Regex-based patterns
    INJECTION_PATTERNS = [
        r"\$\w+",  # MongoDB operators
        r"function\s*\(",  # JavaScript functions
        r"this\.",  # JavaScript this
        r"sleep\(",  # Time-based attacks
    ]
    
    @classmethod
    def sanitize_query(cls, query: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize MongoDB query"""
        return cls._sanitize_recursive(query)
    
    @classmethod
    def _sanitize_recursive(cls, obj: Any) -> Any:
        """Recursively sanitize nested objects"""
        if isinstance(obj, dict):
            sanitized = {}
            for key, value in obj.items():
                # Check for dangerous operators
                if key in cls.DANGEROUS_OPERATORS:
                    logger.warning(
                        f"Blocked dangerous MongoDB operator: {key}",
                        extra={"operator": key}
                    )
                    continue
                
                # Check for regex injection patterns in string keys
                if isinstance(key, str):
                    for pattern in cls.INJECTION_PATTERNS:
                        if re.search(pattern, key, re.IGNORECASE):
                            logger.warning(
                                f"Blocked potential NoSQL injection in key: {key}",
                                extra={"key": key, "pattern": pattern}
                            )
                            continue
                
                # Recursively sanitize value
                sanitized[key] = cls._sanitize_recursive(value)
            
            return sanitized
        
        elif isinstance(obj, list):
            return [cls._sanitize_recursive(item) for item in obj]
        
        elif isinstance(obj, str):
            # Check for injection patterns in string values
            for pattern in cls.INJECTION_PATTERNS:
                if re.search(pattern, obj, re.IGNORECASE):
                    logger.warning(
                        f"Sanitized potential injection in value: {obj[:50]}",
                        extra={"pattern": pattern}
                    )
                    # Replace with safe placeholder
                    return "[SANITIZED]"
            return obj
        
        else:
            return obj

nosql_guard = NoSQLInjectionGuard()
