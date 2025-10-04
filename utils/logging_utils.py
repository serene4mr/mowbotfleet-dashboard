# utils/logging_utils.py

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """
    Set up simple console logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure root logger for console output only
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )


def get_logger(name: str = "mowbot_fleet") -> logging.Logger:
    """Get a simple logger instance."""
    return logging.getLogger(name)


def initialize_logging(level: str = "INFO") -> None:
    """Initialize simple console logging."""
    setup_logging(level)
    logger = get_logger()
    logger.info("Logging system initialized")


if __name__ == "__main__":
    # Test logging setup
    initialize_logging("DEBUG")
    
    logger = get_logger()
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    print("✅ Simple logging test completed")
