import logging
import sys
import os

def setup_logging(service_name: str = "guidora-ai"):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

class StructuredLogger:
    def __init__(self, logger: logging.Logger, context: dict = None):
        self.logger = logger
        self.context = context or {}
    
    def info(self, message: str, **kwargs):
        self.logger.info(f"{message} | {kwargs}")
    
    def error(self, message: str, **kwargs):
        self.logger.error(f"{message} | {kwargs}")
