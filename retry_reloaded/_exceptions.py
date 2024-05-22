import logging
from typing import Callable, Optional

MAX_RETRIES_MESSAGE_TEMPLATE = (
    "Have reached max number of retries ({max_retries}) for function {fname}, aborting."
)
TIMEOUT_MESSAGE_TEMPLATE = (
    "Have been retrying function {fname} for {elapsed_time} secs. Exceeded timeout of {timeout} secs, aborting."
)
DEADLINE_MESSAGE_TEMPLATE = (
    "Have been retrying function {fname} for {elapsed_time} secs. Exceeded deadline of {deadline} secs, aborting."
)


class BaseRetryException(Exception):
    """
    Base class for retry-related exceptions.

    Args:
        logger (logging.Logger): Logger object to use for logging the exception message.
        message (str): Message describing the exception.
        failure_callback (Optional[Callable]): Callback function to execute upon raising the exception.
    """

    def __init__(
        self,
        logger: logging.Logger,
        message: str,
        failure_callback: Optional[Callable] = None
    ) -> None:
        super().__init__(message)
        if logger:
            logger.error(message)
        if failure_callback:
            failure_callback()


class MaxRetriesException(BaseRetryException):
    """
    Exception raised when the maximum number of retries is reached.

    Args:
        logger (logging.Logger): Logger object to use for logging the exception message.
        fname (str): Name of the function for which maximum retries were reached.
        failure_callback (Optional[Callable]): Callback function to execute upon raising the exception.
        max_retries (int): Maximum number of retries that have been attempted.
    """

    def __init__(
        self,
        logger: logging.Logger,
        fname: str,
        max_retries: int,
        failure_callback: Optional[Callable] = None
    ) -> None:
        message = MAX_RETRIES_MESSAGE_TEMPLATE.format(
            fname=fname, max_retries=max_retries
        )
        super().__init__(logger, message, failure_callback)


class RetriesTimeoutException(BaseRetryException):
    """
    Exception raised when retry operation exceeds the timeout.

    Args:
        logger (logging.Logger): Logger object to use for logging the exception message.
        fname (str): Name of the function for which retry operation exceeded timeout.
        failure_callback (Optional[Callable]): Callback function to execute upon raising the exception.
        elapsed_time (float): Time elapsed during the retry operation in seconds.
        timeout (float): Timeout value in seconds.
    """

    def __init__(
        self,
        logger: logging.Logger,
        fname: str,
        elapsed_time: float,
        timeout: float,
        failure_callback: Optional[Callable] = None
    ) -> None:
        message = TIMEOUT_MESSAGE_TEMPLATE.format(
            fname=fname, elapsed_time=elapsed_time, timeout=timeout
        )
        super().__init__(logger, message, failure_callback)


class RetriesDeadlineException(BaseRetryException):
    """
    Exception raised when retry operation exceeds the deadline.

    Args:
        logger (logging.Logger): Logger object to use for logging the exception message.
        fname (str): Name of the function for which retry operation exceeded deadline.
        failure_callback (Optional[Callable]): Callback function to execute upon raising the exception.
        elapsed_time (float): Time elapsed during the retry operation in seconds.
        deadline (float): Deadline value in seconds.
    """

    def __init__(
        self,
        logger: logging.Logger,
        fname: str,
        elapsed_time: float,
        deadline: float,
        failure_callback: Optional[Callable] = None,
    ) -> None:
        message = DEADLINE_MESSAGE_TEMPLATE.format(
            fname=fname, elapsed_time=elapsed_time, deadline=deadline
        )
        super().__init__(logger, message, failure_callback)
