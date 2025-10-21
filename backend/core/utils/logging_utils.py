from typing import Optional, Dict, Any
from django.utils import timezone


def log_to_db(level: str, module: str, message: str, extra_data: Optional[Dict[str, Any]] = None):
    from core.models.log_model import ApplicationLog
    
    try:
        ApplicationLog.objects.create(
            timestamp=timezone.now(),
            level=level.upper(),
            module=module,
            message=message,
            extra_data=extra_data
        )
    except Exception as e:
        # In production, i think we should log this to a file or monitoring service, right?
        print(f"Failed to log to database: {e}")


def log_debug(module: str, message: str, extra_data: Optional[Dict[str, Any]] = None):
    """Log a debug message."""
    log_to_db('DEBUG', module, message, extra_data)


def log_info(module: str, message: str, extra_data: Optional[Dict[str, Any]] = None):
    """Log an info message."""
    log_to_db('INFO', module, message, extra_data)


def log_warning(module: str, message: str, extra_data: Optional[Dict[str, Any]] = None):
    """Log a warning message."""
    log_to_db('WARNING', module, message, extra_data)


def log_error(module: str, message: str, extra_data: Optional[Dict[str, Any]] = None):
    """Log an error message."""
    log_to_db('ERROR', module, message, extra_data)


def log_critical(module: str, message: str, extra_data: Optional[Dict[str, Any]] = None):
    """Log a critical message."""
    log_to_db('CRITICAL', module, message, extra_data)
