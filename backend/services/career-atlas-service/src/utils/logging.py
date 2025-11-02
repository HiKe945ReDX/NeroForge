import logging
import sys
from datetime import datetime
from typing import Dict, Any
import structlog
from pythonjsonlogger import jsonlogger

from ..core.config import get_settings

def setup_logging():
    """
    Setup production-ready structured logging with JSON format
    Optimized for Docker containers and log aggregation systems
    """
    
    settings = get_settings()
    
    # Create custom formatter for JSON output
    class CareerAtlasFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
            super(CareerAtlasFormatter, self).add_fields(log_record, record, message_dict)
            
            # Add service information
            log_record['service'] = 'career-atlas-service'
            log_record['version'] = '1.0.0'
            
            # Ensure timestamp is present
            if not log_record.get('timestamp'):
                log_record['timestamp'] = datetime.utcnow().isoformat()
            
            # Add level name
            if log_record.get('levelname'):
                log_record['level'] = log_record['levelname']
                del log_record['levelname']
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.log_format.lower() == "json":
        formatter = CareerAtlasFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Configure specific loggers
    logging.getLogger('motor').setLevel(logging.WARNING)
    logging.getLogger('pymongo').setLevel(logging.WARNING)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info("✅ Logging configured for career-atlas-service")
    
    return logger
