from time import time
import logging

RETRY_FUNCTION = "Will retry function {fname}."
RETRY_REMAINING_RETRIES = "Remaining retries: {remaining_retries}."
RETRY_REMAINING_TIME = "Remaining time: {remaining_time} secs."
RETRY_DELAY = "Next retry in {delay} secs."


def _init_logger():
    _retry_logger = logging.getLogger(__name__)
    _retry_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    console_handler.setFormatter(formatter)
    _retry_logger.addHandler(console_handler)
    return _retry_logger


def _log_retry(logger, fname, max_retries, retries, timeout, deadline, start_time,  delay, exc_info):
    if not logger:
        return

    messages = []

    messages.append(RETRY_FUNCTION.format(fname=fname))

    if max_retries is not None:
        messages.append(
            RETRY_REMAINING_RETRIES.format(
                remaining_retries=max_retries-retries
            )
        )
    if timeout or deadline:
        min_timeout = min(
            [
                t for t in (timeout, deadline) if t is not None
            ]
        )
        elapsed_time = time() - start_time
        messages.append(
            RETRY_REMAINING_TIME.format(
                remaining_time=min_timeout-elapsed_time
            )
        )
    messages.append(
        RETRY_DELAY.format(delay=delay)
    )

    logger.warning(" ".join(messages), exc_info=exc_info)
