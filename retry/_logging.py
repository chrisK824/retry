from typing import Union, Optional
from time import time
import logging


RETRY_FUNCTION = "Will retry function {fname}."
RETRY_REMAINING_RETRIES = "Remaining retries: {remaining_retries}."
RETRY_REMAINING_TIME = "Remaining time: {remaining_time} secs."
RETRY_DELAY = "Next retry in {delay} secs."


def _init_logger():
    """
    Initialize logger for retry function.

    Returns:
        logging.Logger: Logger object configured for retry logging.
    """
    _retry_logger = logging.getLogger(__name__)
    _retry_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    _retry_logger.addHandler(console_handler)
    return _retry_logger


def _log_retry(
    logger: logging.Logger,
    fname: str,
    max_retries: Union[int, None],
    retries: int,
    timeout: float,
    deadline: float,
    start_time: float,
    delay: float,
    exc_info: Optional[Exception]
):
    """
    Log retry information.

    Args:
        logger (logging.Logger): Logger object to use for logging.
        fname (str): Name of the function being retried.
        max_retries (Union[int, None]): Maximum number of retries allowed, or None if unlimited.
        retries (int): Number of retries attempted so far.
        timeout (float): Timeout value for the retry operation.
        deadline (float): Deadline for the retry operation.
        start_time (float): Start time of the retry operation.
        delay (float): Delay until the next retry.
        exc_info (Optional[Exception]): Information about the exception that triggered the retry.

    Returns:
        None
    """
    if not logger:
        return

    messages = []

    messages.append(RETRY_FUNCTION.format(fname=fname))

    if max_retries is not None:
        messages.append(
            RETRY_REMAINING_RETRIES.format(remaining_retries=max_retries - retries)
        )

    if timeout or deadline:
        min_timeout = min([t for t in (timeout, deadline) if t is not None])
        elapsed_time = time() - start_time
        messages.append(
            RETRY_REMAINING_TIME.format(remaining_time=min_timeout - elapsed_time)
        )

    messages.append(RETRY_DELAY.format(delay=delay))

    logger.warning(" ".join(messages), exc_info=exc_info)
