import pytest
from time import sleep
from retry.retry import retry
from retry.utils._exceptions import (
    MaxRetriesException,
    RetriesTimeoutException,
    RetriesDeadlineException
)
from retry.utils.backoff import FixedBackOff


def test_successful_execution():
    retries = 0

    @retry(max_retries=3)
    def successful_function():
        nonlocal retries
        retries += 1
        if retries < 3:
            raise ValueError("Simulating failure")
        return "Success"

    result = successful_function()
    assert result == "Success"
    assert retries == 3


def test_maximum_retries_reached():
    retries = 0

    @retry(max_retries=2)
    def failure_function():
        nonlocal retries
        retries += 1
        raise ValueError("Simulating failure")

    with pytest.raises(MaxRetriesException):
        failure_function()

    assert retries == 3


def test_timeout(time_patch, sleep_patch):
    retries = 0
    timeout = 2

    @retry(timeout=timeout, backoff=FixedBackOff(base_delay=1))
    def timeout_function():
        nonlocal retries
        retries += 1
        raise ValueError("Simulating failure")

    with pytest.raises(RetriesTimeoutException):
        timeout_function()

    assert sleep_patch.call_count == timeout
    assert retries == timeout


def test_deadline():
    retries = 0
    deadline = 2

    @retry(deadline=deadline, backoff=FixedBackOff(base_delay=1))
    def deadline_function():
        nonlocal retries
        retries += 1
        if retries < deadline:
            raise ValueError("Simulating failure")
        else:
            sleep(deadline)

    with pytest.raises(RetriesDeadlineException):
        deadline_function()

    assert retries == deadline


def test_failure_callback_called(failure_callback):
    @retry(max_retries=1, failure_callback=failure_callback)
    def fail_with_callback():
        raise ValueError("Simulating failure")

    with pytest.raises(MaxRetriesException):
        fail_with_callback()

    failure_callback.assert_called_once()


def test_successful_retry_callback_called(successful_retry_callback):
    retries = 0
    max_retries = 2

    @retry(max_retries=max_retries, successful_retry_callback=successful_retry_callback)
    def successful_retry_with_callback():
        nonlocal retries
        retries += 1
        if retries < max_retries:
            raise ValueError("Simulating failure")

    successful_retry_with_callback()

    successful_retry_callback.assert_called_once()


def test_retry_callback_called(retry_callback):
    max_retries = 2

    @retry(max_retries=max_retries, retry_callback=retry_callback)
    def retry_with_callback():
        raise ValueError("Simulating failure")

    with pytest.raises(MaxRetriesException):
        retry_with_callback()

    retry_callback.call_count = max_retries
