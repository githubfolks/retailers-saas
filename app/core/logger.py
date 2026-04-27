import logging
from logging.handlers import RotatingFileHandler
import os

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

request_logger = logging.getLogger("request")
error_logger = logging.getLogger("error")

request_handler = RotatingFileHandler(
    os.path.join(log_dir, "requests.log"),
    maxBytes=10485760,
    backupCount=5
)

error_handler = RotatingFileHandler(
    os.path.join(log_dir, "errors.log"),
    maxBytes=10485760,
    backupCount=5
)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

request_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

request_logger.addHandler(request_handler)
request_logger.setLevel(logging.INFO)

error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)


def get_logger(name: str):
    """Get a logger instance for the given module name"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Add console handler if not already present
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

