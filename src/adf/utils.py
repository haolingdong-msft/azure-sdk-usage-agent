"""Utility functions for ADF SDK."""

import logging
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Callable
from functools import wraps


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


# ==================== DateTime Utilities ====================

def parse_iso_datetime(time_str: str) -> datetime:
    """
    Parse ISO 8601 datetime string.
    
    Args:
        time_str: ISO 8601 formatted datetime string
        
    Returns:
        datetime object
        
    Raises:
        ValueError: If the time string is invalid
    """
    try:
        # Handle both Z and +00:00 timezone formats
        normalized = time_str.replace('Z', '+00:00')
        return datetime.fromisoformat(normalized)
    except Exception as e:
        raise ValueError(f"Invalid ISO 8601 datetime: {time_str}") from e


def format_iso_datetime(dt: datetime) -> str:
    """
    Format datetime as ISO 8601 string.
    
    Args:
        dt: datetime object
        
    Returns:
        ISO 8601 formatted string
    """
    # Ensure timezone awareness
    iso_str = dt.isoformat()
    # Replace +00:00 with Z for consistency
    if iso_str.endswith('+00:00'):
        iso_str = iso_str[:-6] + 'Z'
    return iso_str


def get_time_range(hours: int = 24) -> tuple[str, str]:
    """
    Get time range for the last N hours.
    
    Args:
        hours: Number of hours to look back
        
    Returns:
        Tuple of (start_time, end_time) in ISO 8601 format
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    return format_iso_datetime(start_time), format_iso_datetime(end_time)


def ensure_iso8601(time_input: str | datetime) -> str:
    """
    Ensure the time input is in ISO 8601 format.
    
    Args:
        time_input: Either an ISO 8601 string or datetime object
        
    Returns:
        ISO 8601 formatted string
    """
    if isinstance(time_input, datetime):
        return format_iso_datetime(time_input)
    elif isinstance(time_input, str):
        # Validate by parsing and re-formatting
        dt = parse_iso_datetime(time_input)
        return format_iso_datetime(dt)
    else:
        raise TypeError(f"Expected str or datetime, got {type(time_input)}")


# ==================== Retry Utilities ====================

def retry_on_error(
    max_attempts: int = 3,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff: Backoff multiplier for exponential delay
        exceptions: Tuple of exception types to catch
        logger: Optional logger for logging retries
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        # Last attempt failed, re-raise
                        raise
                    
                    wait_time = backoff ** attempt
                    if logger:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator


# ==================== Validation Utilities ====================

import re

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


def validate_time_range(start_time: str, end_time: str) -> None:
    """
    Validate that start_time is before end_time.
    
    Args:
        start_time: Start time in ISO 8601 format
        end_time: End time in ISO 8601 format
        
    Raises:
        ValueError: If time range is invalid
    """
    start_dt = parse_iso_datetime(start_time)
    end_dt = parse_iso_datetime(end_time)
    
    if start_dt >= end_dt:
        raise ValueError(
            f"start_time must be before end_time. "
            f"Got: start={start_time}, end={end_time}"
        )


def validate_azure_resource_name(name: str, resource_type: str = "resource") -> None:
    """
    Validate Azure resource name.
    
    Args:
        name: Resource name to validate
        resource_type: Type of resource (for error messages)
        
    Raises:
        ValueError: If name is invalid
    """
    if not name or not isinstance(name, str):
        raise ValueError(f"Invalid {resource_type} name: {name}")
    
    if len(name) < 1 or len(name) > 260:
        raise ValueError(
            f"{resource_type} name must be between 1 and 260 characters: {name}"
        )


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


def load_from_json(filepath: Path | str) -> Any:
    """
    Load data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded data
    """
    filepath = Path(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


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


def sanitize_dict_for_logging(data: dict[str, Any], sensitive_keys: Optional[list[str]] = None) -> dict[str, Any]:
    """
    Sanitize dictionary for logging by redacting sensitive information.
    
    Args:
        data: Dictionary to sanitize
        sensitive_keys: List of keys to redact (default: common sensitive keys)
        
    Returns:
        Sanitized dictionary
    """
    if sensitive_keys is None:
        sensitive_keys = [
            'password', 'secret', 'token', 'key', 'credential',
            'authorization', 'api_key', 'access_token'
        ]
    
    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict_for_logging(value, sensitive_keys)
        else:
            sanitized[key] = value
    
    return sanitized
