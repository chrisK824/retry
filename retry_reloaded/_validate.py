from typing import Tuple, Type, Callable, Optional
import logging
from .backoff import BackOff


def _validate_args(
    exceptions: Tuple[Type[Exception], ...],
    excluded_exceptions: Tuple[Type[Exception], ...],
    max_retries: Optional[int],
    backoff: BackOff,
    timeout: Optional[float],
    deadline: Optional[float],
    logger: Optional[logging.Logger],
    log_retry_traceback: bool,
    failure_callback: Optional[Callable[[], None]],
    retry_callback: Optional[Callable[[], None]],
    successful_retry_callback: Optional[Callable[[], None]],
    reraise_exception: bool
) -> None:
    """
    Validate arguments for retry logic.

    Args:
        exceptions (Tuple[Type[Exception], ...]): Tuple of exception types to catch.
        excluded_exceptions (Tuple[Type[Exception]], ...): Tuple of exception types not to catch.
        max_retries (Optional[int]): Maximum number of retries allowed, or None for unlimited retries.
        backoff (BackOff): BackOff instance to manage retry delays.
        timeout (Optional[float]): Timeout value for the retry operation in seconds, or None if no timeout.
        deadline (Optional[float]): Deadline for the retry operation in seconds, or None if no deadline.
        logger (Optional[logging.Logger]): Logger instance for logging retry information, or None if logging is disabled.
        log_retry_traceback (bool): Flag to indicate if the traceback should be logged on each retry.
        failure_callback (Optional[Callable[[], None]]): Callback function to execute upon a failed retry, or None.
        retry_callback (Optional[Callable[[], None]]): Callback function to execute before each retry attempt, or None.
        successful_retry_callback (Optional[Callable[[], None]]): Callback function to execute upon a successful retry,
          or None.
        reraise_exception (bool): Whether to re-raise the last exception caught in case of failure after retries.

    Raises:
        TypeError: If any of the arguments do not meet the expected types.
    """
    if not isinstance(exceptions, tuple):
        raise TypeError("exceptions must be a tuple")

    for exc in exceptions:
        if not issubclass(exc, Exception):
            raise TypeError("All items in the exceptions tuple must be subclasses of Exception")

    for exc in excluded_exceptions:
        if not issubclass(exc, Exception):
            raise TypeError("All items in the excluded_exceptions tuple must be subclasses of Exception")

    if max_retries is not None and not isinstance(max_retries, int):
        raise TypeError("max_retries must be an integer or None")

    if not isinstance(backoff, BackOff):
        raise TypeError("backoff must be an instance of BackOff")

    if timeout is not None and not isinstance(timeout, (int, float)):
        raise TypeError("timeout must be a float or None")

    if deadline is not None and not isinstance(deadline, (int, float)):
        raise TypeError("deadline must be a float or None")

    if logger is not None and not isinstance(logger, logging.Logger):
        raise TypeError("logger must be an instance of logging.Logger or None")

    if not isinstance(log_retry_traceback, bool):
        raise TypeError("log_retry_traceback must be a boolean")

    if failure_callback is not None and not callable(failure_callback):
        raise TypeError("failure_callback must be a callable or None")

    if retry_callback is not None and not callable(retry_callback):
        raise TypeError("retry_callback must be a callable or None")

    if successful_retry_callback is not None and not callable(successful_retry_callback):
        raise TypeError("successful_retry_callback must be a callable or None")

    if not isinstance(reraise_exception, bool):
        raise TypeError("reraise_exception must be a boolean")