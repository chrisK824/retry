from retry_reloaded import (
    retry,
    callback_factory,
    CallbackFactory,
    FixedBackOff,
    LinearBackOff,
    ExponentialBackOff,
    RandomUniformBackOff,
    MaxRetriesException,
    RetriesTimeoutException,
    RetriesDeadlineException
)
from time import sleep
import logging

# get the package logger if you don't intend to use your own
logger = logging.getLogger("retry_reloaded")


# Retry until maximum retries are reached
# no backoff strategy means the default will apply,
# which is 0 delay between retries
@retry((AssertionError,), max_retries=3)
def cause_max_retries_error():
    assert False


# Retry until timeout error after 2 seconds
# fixed backoff strategy for 1 second delay between retries
@retry((ValueError,), timeout=2, backoff=FixedBackOff(base_delay=1))
def cause_timeout_error():
    raise ValueError


# Retry until deadline error after 2 seconds
# not really retrying here, it will just execute once
# as the execution will take longer than deadline
@retry(deadline=3)
def cause_deadline_error():
    sleep(4)


# Retry until deadline error after 2 seconds
# fixed backoff strategy for 1 second delay between retries
# expected to retry twice and then succeed but restricted by deadline
@retry(
        (ValueError,),
        deadline=2,
        backoff=FixedBackOff(base_delay=1)
)
def cause_deadline_error_after_retries():
    if not hasattr(cause_deadline_error_after_retries, "call_count"):
        cause_deadline_error_after_retries.call_count = 0
    cause_deadline_error_after_retries.call_count += 1
    if cause_deadline_error_after_retries.call_count < 2:
        raise ValueError
    else:
        sleep(1)


# Retry until maximum retries are reached
# Random backoff strategy with an initial delay and
# limits for min and max delay in next retries
# callback function between retries by passing a callable function
def retry_callback():
    logger.debug("Calling between retries")


@retry(
        (ValueError,),
        max_retries=3,
        backoff=RandomUniformBackOff(base_delay=0.3, min_delay=0.1, max_delay=0.5),
        retry_callback=retry_callback
)
def retry_with_callback():
    raise ValueError


# Retry indefinetely as there is no max retries, timeout
# or deadline specified
# Exponential backoff strategy with an initial delay of 1 second
# parametrized callback with utility of package to call after successful retry
# successful callback is expected after successful retry on 3rd round
def successful_retry_callback(value):
    logger.debug(f"Calling on successful retry with value: {value}")


successful_retry_callback_ = callback_factory(successful_retry_callback, "phew")


@retry(
        (ValueError,),
        backoff=ExponentialBackOff(base_delay=1),
        successful_retry_callback=successful_retry_callback_
)
def successful_retry_with_callback():
    if not hasattr(successful_retry_with_callback, "call_count"):
        successful_retry_with_callback.call_count = 0
    successful_retry_with_callback.call_count += 1
    if successful_retry_with_callback.call_count < 3:
        raise ValueError


# Retry until maximum retries are reached
# Linear backoff strategy with an initial delay of 0.1 second and 0.1 second as step
# parametrized callback with utility of package to call after failure of all retries
# failure callback is expected after failing all 3 retries
def failure_callback(value):
    logger.debug(f"Calling after failure of all retries with value: {value}")


failure_callback_ = CallbackFactory(failure_callback, value="wasted")


@retry(
        max_retries=3,
        backoff=LinearBackOff(base_delay=0.1, step=0.1),
        failure_callback=failure_callback_
)
def fail_with_callback():
    raise ValueError


# Retry with re-raising the original exception after all retries
# Retry 2 times and then raise the original exception (ValueError)
@retry(
        (ValueError,),
        max_retries=2,
        reraise_exception=True
)
def retry_with_reraise():
    raise ValueError("Original exception to be re-raised")


if __name__ == "__main__":

    # propagate the exception raised here just
    # to display how it would look like
    try:
        cause_max_retries_error()
    except MaxRetriesException as e:
        logger.exception(e)

    try:
        cause_timeout_error()
    except RetriesTimeoutException:
        pass

    try:
        cause_deadline_error()
    except RetriesDeadlineException:
        pass

    try:
        cause_deadline_error_after_retries()
    except RetriesDeadlineException:
        pass

    try:
        retry_with_callback()
    except MaxRetriesException:
        pass

    successful_retry_with_callback()

    try:
        fail_with_callback()
    except MaxRetriesException:
        pass

    try:
        retry_with_reraise()
    except ValueError as e:
        logger.error(f"Caught re-raised exception: {e}")
