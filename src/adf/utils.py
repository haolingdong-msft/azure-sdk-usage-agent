"""Utility functions for ADF SDK."""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Any
import re

# ==================== Logging Utilities ====================

def setup_logging(level: str = "INFO", log_format: str = "text") -> None:
    """
    Configure logging system for ADF SDK.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ("text" or "json")
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if log_format == "json":
        # Structured logging format
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )
    else:
        # Text logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# ==================== Validation Utilities ====================


UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)


def validate_run_id(run_id: str) -> None:
    """
    Validate pipeline run ID format.
    
    Args:
        run_id: Run ID to validate
        
    Raises:
        ValueError: If run_id is invalid
    """
    if not run_id or not isinstance(run_id, str):
        raise ValueError(f"Invalid run_id: {run_id}")
    
    if not UUID_PATTERN.match(run_id):
        raise ValueError(f"run_id must be a valid UUID: {run_id}")


# ==================== Serialization Utilities ====================

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def save_to_json(
    data: Any,
    filepath: Path | str,
    indent: int = 2,
    ensure_ascii: bool = False,
    **kwargs
) -> None:
    """
    Save data to JSON file with datetime handling.
    
    Args:
        data: Data to save
        filepath: Path to save file
        indent: JSON indentation
        ensure_ascii: Whether to ensure ASCII encoding
        **kwargs: Additional arguments for json.dump
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(
            data,
            f,
            cls=DateTimeEncoder,
            indent=indent,
            ensure_ascii=ensure_ascii,
            **kwargs
        )


def sdk_object_to_dict(obj: Any) -> dict[str, Any]:
    """
    Convert Azure SDK object to dictionary.
    
    Args:
        obj: Azure SDK object
        
    Returns:
        Dictionary representation
    """
    if hasattr(obj, 'as_dict'):
        return obj.as_dict()
    elif isinstance(obj, dict):
        return obj
    else:
        raise TypeError(f"Cannot convert {type(obj)} to dict")
