"""
Retry logic and decorators for API calls.
"""
from functools import wraps
from typing import Callable, Type, Union, Tuple

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError
)
import structlog

from .error_handler import is_retryable_error


logger = structlog.get_logger()


def create_retry_decorator(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception
):
    """
    Create a retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds
        exception_types: Exception types to retry on

    Returns:
        Retry decorator
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(min=min_wait, max=max_wait),
        retry=retry_if_exception_type(exception_types),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )


def retry_on_api_error(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0
):
    """
    Decorator for retrying API calls with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            @retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(min=min_wait, max=max_wait),
                retry=retry_if_exception(is_retryable_error),
                before_sleep=_log_retry_attempt,
                reraise=True
            )
            def _retry_wrapper():
                return func(*args, **kwargs)

            try:
                return _retry_wrapper()
            except RetryError as e:
                # Re-raise the original exception
                raise e.last_attempt.exception()

        return wrapper
    return decorator


def retry_if_exception(predicate: Callable[[Exception], bool]):
    """
    Create a retry condition based on an exception predicate.

    Args:
        predicate: Function that takes an exception and returns True if should retry

    Returns:
        Retry condition
    """
    def _retry_if_exception_predicate(retry_state):
        if retry_state.outcome.failed:
            exception = retry_state.outcome.exception()
            return predicate(exception)
        return False

    return _retry_if_exception_predicate


def _log_retry_attempt(retry_state):
    """Log retry attempts with structured logging."""
    exception = retry_state.outcome.exception()
    attempt_number = retry_state.attempt_number
    wait_time = retry_state.next_action.sleep if retry_state.next_action else 0

    logger.warning(
        "retrying_after_error",
        attempt=attempt_number,
        wait_seconds=wait_time,
        error_type=type(exception).__name__,
        error_message=str(exception)
    )


# Pre-configured retry decorators for different APIs

news_api_retry = create_retry_decorator(
    max_attempts=3,
    min_wait=2.0,
    max_wait=10.0
)

claude_api_retry = create_retry_decorator(
    max_attempts=5,
    min_wait=1.0,
    max_wait=30.0
)

kling_api_retry = create_retry_decorator(
    max_attempts=2,
    min_wait=5.0,
    max_wait=30.0
)

elevenlabs_api_retry = create_retry_decorator(
    max_attempts=3,
    min_wait=2.0,
    max_wait=15.0
)
