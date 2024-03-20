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
    def __init__(self, logger, message, failure_callback):
        if logger:
            logger.error(message)
        if failure_callback:
            failure_callback()
        super().__init__(message)


class MaxRetriesException(BaseRetryException):
    def __init__(self, logger, fname, failure_callback, max_retries):
        message = MAX_RETRIES_MESSAGE_TEMPLATE.format(
            fname=fname, max_retries=max_retries
        )
        super().__init__(logger, message, failure_callback)


class RetriesTimeoutException(BaseRetryException):
    def __init__(self, logger, fname, failure_callback, elapsed_time: float, timeout: float):
        message = TIMEOUT_MESSAGE_TEMPLATE.format(
            fname=fname, elapsed_time=elapsed_time, timeout=timeout
        )
        super().__init__(logger, message, failure_callback)


class RetriesDeadlineException(BaseRetryException):
    def __init__(self, logger, fname, failure_callback, elapsed_time: float, deadline: float):
        message = DEADLINE_MESSAGE_TEMPLATE.format(
            fname=fname, elapsed_time=elapsed_time, deadline=deadline
        )
        super().__init__(logger, message, failure_callback)
