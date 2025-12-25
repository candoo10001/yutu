"""
Structured logging setup for the video generation pipeline.
"""
import logging
import sys
from pathlib import Path
from typing import Optional

import structlog


def setup_logger(
    log_level: str = "INFO",
    log_dir: Optional[str] = None,
    log_file: str = "pipeline.log"
) -> structlog.BoundLogger:
    """
    Configure and return a structured logger.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files (None for no file logging)
        log_file: Name of the log file

    Returns:
        Configured structlog logger
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # Add file handler if log_dir is specified
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path / log_file)
        file_handler.setLevel(numeric_level)
        logging.root.addHandler(file_handler)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def log_api_call(
    logger: structlog.BoundLogger,
    api_name: str,
    operation: str,
    **kwargs
):
    """
    Log an API call with structured data.

    Args:
        logger: The structlog logger instance
        api_name: Name of the API (e.g., "News API", "Claude API")
        operation: Operation being performed
        **kwargs: Additional context to log
    """
    logger.info(
        "api_call",
        api=api_name,
        operation=operation,
        **kwargs
    )


def log_api_response(
    logger: structlog.BoundLogger,
    api_name: str,
    operation: str,
    success: bool,
    duration_ms: Optional[float] = None,
    **kwargs
):
    """
    Log an API response with structured data.

    Args:
        logger: The structlog logger instance
        api_name: Name of the API
        operation: Operation that was performed
        success: Whether the operation succeeded
        duration_ms: Duration in milliseconds
        **kwargs: Additional context to log
    """
    log_data = {
        "api": api_name,
        "operation": operation,
        "success": success,
        **kwargs
    }

    if duration_ms is not None:
        log_data["duration_ms"] = duration_ms

    if success:
        logger.info("api_response", **log_data)
    else:
        logger.error("api_response", **log_data)


def log_metric(
    logger: structlog.BoundLogger,
    metric_name: str,
    value: float,
    unit: str = "",
    **kwargs
):
    """
    Log a metric with structured data.

    Args:
        logger: The structlog logger instance
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        **kwargs: Additional context to log
    """
    logger.info(
        "metric",
        metric=metric_name,
        value=value,
        unit=unit,
        **kwargs
    )


def log_error(
    logger: structlog.BoundLogger,
    error: Exception,
    context: str,
    **kwargs
):
    """
    Log an error with structured data.

    Args:
        logger: The structlog logger instance
        error: The exception that occurred
        context: Context where the error occurred
        **kwargs: Additional context to log
    """
    logger.error(
        "error",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context,
        **kwargs,
        exc_info=True
    )
