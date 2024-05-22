from typing import Union, Optional
from time import time
import logging


def _init_logger(name: str) -> logging.Logger:
    """
    Initialize logger for retry function.

    Args:
        name (str): Name for the logger.

    Returns:
        logging.Logger: Logger object configured for retry logging.
    """
    _retry_logger = logging.getLogger(name)
    _retry_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    _retry_logger.addHandler(console_handler)
    _retry_logger.propagate = False
    return _retry_logger


def _log_retry(
    logger: Optional[logging.Logger],
    fname: str,
    max_retries: Optional[int],
    retries: int,
    timeout: Optional[float],
    deadline: Optional[float],
    start_time: float,
    delay: float,
    exc_info: Optional[Exception] = None
) -> None:
    """
    Log retry information.

    Args:
        logger (Optional[logging.Logger]): Logger object to use for logging. If None, logging is skipped.
        fname (str): Name of the function being retried.
        max_retries (Optional[int]): Maximum number of retries allowed, or None if unlimited.
        retries (int): Number of retries attempted so far.
        timeout (Optional[float]): Timeout value for the retry operation in seconds.
        deadline (Optional[float]): Deadline for the retry operation in seconds.
        start_time (float): Start time of the retry operation.
        delay (float): Delay until the next retry in seconds.
        exc_info (Optional[Exception]): Information about the exception that triggered the retry.

    Returns:
        None
    """
    if not logger:
        return

    base_message = "Will retry function {fname}."
    remaining_retries_message = "Remaining retries: {remaining_retries}."
    remaining_time_message = "Remaining time: {remaining_time} secs."
    next_delay_message = "Next retry in {delay} secs."

    messages = [base_message.format(fname=fname)]

    if max_retries is not None:
        messages.append(
            remaining_retries_message.format(remaining_retries=max_retries - retries)
        )

    if timeout or deadline:
        min_timeout = min([t for t in (timeout, deadline) if t is not None])
        elapsed_time = time() - start_time
        messages.append(
            remaining_time_message.format(remaining_time=min_timeout - elapsed_time)
        )

    messages.append(next_delay_message.format(delay=delay))

    logger.warning(" ".join(messages), exc_info=exc_info)
