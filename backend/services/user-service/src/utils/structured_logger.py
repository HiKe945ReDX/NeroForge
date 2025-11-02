"""Structured JSON logger with correlation ID tracking"""
import logging
import sys
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar
import uuid
from typing import Optional

# Context variable for correlation ID (thread-safe)
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to all log records"""
    
    def filter(self, record):
        record.correlation_id = correlation_id_ctx.get() or 'N/A'
        return True

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record['service'] = 'user-service'
        log_record['version'] = '3.0.0'
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['correlation_id'] = getattr(record, 'correlation_id', 'N/A')
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)

def setup_logger(name: str = __name__, level: str = "INFO") -> logging.Logger:
    """Setup structured JSON logger"""
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler with JSON formatting
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(correlation_id)s'
    )
    handler.setFormatter(formatter)
    
    # Add correlation ID filter
    correlation_filter = CorrelationIdFilter()
    handler.addFilter(correlation_filter)
    
    logger.addHandler(handler)
    return logger

def get_correlation_id() -> str:
    """Get current correlation ID or generate new one"""
    corr_id = correlation_id_ctx.get()
    if not corr_id:
        corr_id = str(uuid.uuid4())
        correlation_id_ctx.set(corr_id)
    return corr_id

def set_correlation_id(corr_id: str):
    """Set correlation ID for current request"""
    correlation_id_ctx.set(corr_id)

# Global logger instance
logger = setup_logger(__name__)
