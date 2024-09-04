import logging
from copy import deepcopy
from time import sleep
from functools import wraps
from typing import Union, Callable, Tuple, Type
from time import time
from ._validate import _validate_args
from ._logging import _init_logger, _log_retry
from ._exceptions import (
    MaxRetriesException,
    RetriesTimeoutException,
    RetriesDeadlineException,
)
from .backoff import BackOff, FixedBackOff


retry_logger = _init_logger(__package__)


def retry(
    exceptions: Tuple[Type[Exception]] = (Exception,),
    max_retries: Union[int, None] = None,
    backoff: BackOff = FixedBackOff(base_delay=0),
    timeout: Union[float, None] = None,
    deadline: Union[float, None] = None,
    logger: Union[logging.Logger, None] = retry_logger,
    log_retry_traceback: bool = False,
    failure_callback: Union[Callable, None] = None,
    retry_callback: Union[Callable, None] = None,
    successful_retry_callback: Union[Callable, None] = None,
    reraise_exception: bool = False
) -> Callable:
    """
    Decorator that adds retry functionality to a function.

    Parameters:
        exceptions (Tuple[Type[Exception]], optional): A tuple of exception types that should trigger a retry.
            Defaults to (Exception,), meaning any exception will trigger a retry.
        max_retries (int, optional): The maximum number of retry attempts. Defaults to None (unlimited retries).
        backoff (BackOff, optional): The backoff strategy to use between retry attempts.
            Defaults to FixedBackOff(base_delay=0) with base_delay referring to seconds.
        timeout (float, optional): The maximum time (in seconds) to spend on retries. Defaults to None (no timeout).
            Timeout check happens right before retry execution of the wrapped function.
        deadline (float, optional): The deadline (in seconds) for retries. Defaults to None (no deadline).
            Deadline check happens right after the retry execution of the wrapped function.
        logger (logging.Logger, optional): The logger instance to use for logging retry attempts. Defaults to retry_logger.
        log_retry_traceback (bool, optional): Whether to log the traceback of exceptions triggering retries.
            Defaults to False.
        failure_callback (Callable, optional): A callback function to call in case of eventual failure after retries.
            Defaults to None.
        retry_callback (Callable, optional): A callback function to call between subsequent retry attempts.
            Defaults to None.
        successful_retry_callback (Callable, optional): A callback function to call after a successful retry.
            Defaults to None.
        reraise_exception (bool, optional): Whether to re-raise the last exception caught in case of failure after retries.
            Defaults to False.

    Returns:
        Callable: The decorated function.

    Raises:
        TypeError: If any argument has an invalid type.

    Example:
        @retry(exceptions=(ValueError,), max_retries=3, backoff=ExponentialBackOff(), timeout=10, logger=my_logger)
        def my_function():
            # Function body
    """

    _validate_args(
        exceptions, max_retries, backoff, timeout,
        deadline, logger, log_retry_traceback,
        failure_callback, retry_callback, successful_retry_callback,
        reraise_exception
    )

    def wrapped_func(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time()
            retries = 0
            _backoff = deepcopy(backoff)
            _backoff.reset()
            fname = f.__name__
            last_exception = None

            while True:
                try:
                    if timeout:
                        elapsed_time_before = time() - start_time
                        if elapsed_time_before > timeout:
                            raise RetriesTimeoutException(
                                logger=logger,
                                fname=fname,
                                failure_callback=failure_callback,
                                elapsed_time=elapsed_time_before,
                                timeout=timeout,
                            )

                    result = f(*args, **kwargs)

                    if deadline:
                        elapsed_time_after = time() - start_time
                        if elapsed_time_after > deadline:
                            raise RetriesDeadlineException(
                                logger=logger,
                                fname=fname,
                                failure_callback=failure_callback,
                                elapsed_time=elapsed_time_after,
                                deadline=deadline,
                            )

                    if retries > 0 and successful_retry_callback:
                        successful_retry_callback()

                    return result
                except exceptions as original_exc:
                    if isinstance(original_exc, (RetriesTimeoutException, RetriesDeadlineException)):
                        if reraise_exception and last_exception is not None:
                            raise last_exception
                        raise original_exc

                    last_exception = original_exc

                    if max_retries is not None:
                        if retries == max_retries:
                            if reraise_exception and last_exception is not None:
                                raise last_exception
                            raise MaxRetriesException(
                                logger=logger,
                                fname=fname,
                                failure_callback=failure_callback,
                                max_retries=max_retries,
                            ) from original_exc

                    delay = _backoff.delay
                    exc_info = original_exc if log_retry_traceback else None
                    _log_retry(
                        logger=logger,
                        fname=fname,
                        max_retries=max_retries,
                        retries=retries,
                        timeout=timeout,
                        deadline=deadline,
                        start_time=start_time,
                        delay=delay,
                        exc_info=exc_info,
                    )

                    if retry_callback:
                        retry_callback()

                    sleep(delay)
                    retries += 1

        return wrapper

    return wrapped_func
