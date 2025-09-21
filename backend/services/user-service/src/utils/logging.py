import logging
import sys
from pathlib import Path

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup application logging"""
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/user-service.log")
        ]
    )
    
    return logging.getLogger("user-service")

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)
