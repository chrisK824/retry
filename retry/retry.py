import logging
from time import sleep
from functools import wraps
from typing import Union, Callable
from time import time
from _logging import _init_logger, _log_retry
from _exceptions import (
    MaxRetriesException,
    RetriesTimeoutException,
    RetriesDeadlineException,
)
from backoff import FixedBackOff

retry_logger = _init_logger()


def retry(
    exceptions: tuple = (Exception,),
    max_retries: Union[int, None] = None,
    backoff=FixedBackOff(initial_delay=0),
    timeout: Union[float, None] = None,
    deadline: Union[float, None] = None,
    logger: logging.Logger = retry_logger,
    log_retry_traceback: bool = False,
    failure_callback: Callable = None,
    retry_callback: Callable = None,
    successful_retry_callback: Callable = None,
):
    def wrapped_func(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time()
            retries = 0
            fname = f.__name__

            while True:
                try:
                    elapsed_time_before = time() - start_time
                    if timeout and elapsed_time_before > timeout:
                        raise RetriesTimeoutException(
                            logger=logger,
                            fname=fname,
                            failure_callback=failure_callback,
                            elapsed_time=elapsed_time_before,
                            timeout=timeout,
                        )

                    result = f(*args, **kwargs)

                    elapsed_time_after = time() - start_time
                    if deadline and elapsed_time_after > deadline:
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
                    exc_info = original_exc if log_retry_traceback else None

                    if max_retries is not None:
                        if retries == max_retries:
                            raise MaxRetriesException(
                                logger=logger,
                                fname=fname,
                                failure_callback=failure_callback,
                                max_retries=max_retries,
                            ) from original_exc

                    if retry_callback:
                        retry_callback()

                    delay = backoff.delay
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
                    sleep(delay)
                    retries += 1

        return wrapper

    return wrapped_func


@retry((AssertionError,), max_retries=3)
def cause_trouble():
    assert False


cause_trouble()
