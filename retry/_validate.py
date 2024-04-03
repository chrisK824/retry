from typing import Union, Tuple, Type, Callable
import logging
from .backoff import BackOff


def _validate_args(
    exceptions: Tuple[Type[Exception]],
    max_retries: Union[int, None],
    backoff: BackOff,
    timeout: Union[float, None],
    deadline: Union[float, None],
    logger: Union[logging.Logger, None],
    log_retry_traceback: bool,
    failure_callback: Union[Callable, None],
    retry_callback: Union[Callable, None],
    successful_retry_callback: Union[Callable, None]
):
    if not isinstance(exceptions, tuple):
        raise TypeError("exceptions must be a tuple")

    for exc in exceptions:
        if not issubclass(exc, Exception):
            raise TypeError("All items in the exceptions tuple must be subclasses of exception class")

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
