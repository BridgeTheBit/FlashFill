import logging
import os
import sys

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # Create console handler with formatting
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def sanitize_log_message(message: str, api_key: str) -> str:
    """Removes API key from log messages if present."""
    if not api_key:
        return message
    return message.replace(api_key, "***HIDDEN_API_KEY***")
