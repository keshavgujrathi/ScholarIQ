import logging
import sys
import json
import time
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .config import settings

# Custom log levels
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_record: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname.lower(),
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request_id if available
        if hasattr(record, 'request_id'):
            log_record["request_id"] = record.request_id
        
        # Add extra fields
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)
        if hasattr(record, 'extra') and isinstance(record.extra, dict):
            log_record.update(record.extra)
        
        return json.dumps(log_record, ensure_ascii=False, default=str)

class RequestIdFilter(logging.Filter):
    """Add request_id to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request_id to the log record if available in the request state."""
        request_id = getattr(record, 'request_id', None)
        if not hasattr(record, 'request_id') and hasattr(record, 'request'):
            request = record.request
            if hasattr(request.state, 'request_id'):
                record.request_id = request.state.request_id
        return True

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Log request and response details."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        logger = logging.getLogger("uvicorn.access")
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )
        
        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log unhandled exceptions
            logger.error(
                "Request failed",
                exc_info=exc,
                extra={
                    "request_id": request_id,
                    "duration": time.time() - start_time,
                },
            )
            raise
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": round(process_time * 1000),  # in milliseconds
            },
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response

def setup_logging() -> None:
    """Configure logging for the application."""
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVELS.get(settings.LOG_LEVEL.lower(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JSONFormatter(
            fmt='%(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S%z'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if LOG_FILE is configured)
    if settings.LOG_FILE:
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Configure third-party loggers
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if settings.APP_ENV != "test" else logging.ERROR
    )
    
    # Add request ID filter to root logger
    logger.addFilter(RequestIdFilter())
    
    # Log configuration
    logger.info(
        "Logging configured",
        extra={
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT,
            "environment": settings.APP_ENV,
            "log_file": str(settings.LOG_FILE) if settings.LOG_FILE else None,
        },
    )

# Initialize logging when this module is imported
setup_logging()

# Create and export logger instance
logger = logging.getLogger("scholariq")

# Make the main logger available as 'logger' for imports
__all__ = [
    "logger", 
    "api_logger", 
    "security_logger", 
    "database_logger",
    "setup_logging", 
    "RequestLoggingMiddleware",
    "JSONFormatter",
    "RequestIdFilter"
]