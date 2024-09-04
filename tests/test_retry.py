import pytest
from time import sleep
from retry_reloaded import retry
from retry_reloaded._exceptions import (
    MaxRetriesException,
    RetriesTimeoutException,
    RetriesDeadlineException
)
from retry_reloaded.backoff import FixedBackOff


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


def test_timeout():
    retries = 0
    timeout = 2

    @retry(timeout=timeout, backoff=FixedBackOff(base_delay=1))
    def timeout_function():
        nonlocal retries
        retries += 1
        raise ValueError("Simulating failure")

    with pytest.raises(RetriesTimeoutException):
        timeout_function()

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


def test_reraise_exception_true():
    retries = 0
    max_retries = 2

    @retry(max_retries=max_retries, reraise_exception=True)
    def function_that_fails():
        nonlocal retries
        retries += 1
        raise ValueError("Simulating failure")

    with pytest.raises(ValueError, match="Simulating failure"):
        function_that_fails()

    assert retries == max_retries + 1


def test_reraise_exception_false():
    retries = 0
    max_retries = 2

    @retry(max_retries=max_retries, reraise_exception=False)
    def function_that_fails():
        nonlocal retries
        retries += 1
        raise ValueError("Simulating failure")

    with pytest.raises(MaxRetriesException):
        function_that_fails()

    assert retries == max_retries + 1


def test_no_retry_on_excluded_exception():
    retries = 0

    @retry(excluded_exceptions=(ValueError,), max_retries=2)
    def raise_value_error():
        nonlocal retries
        retries += 1
        raise ValueError("Simulating ValueError")

    with pytest.raises(ValueError):
        raise_value_error()

    assert retries == 1


def test_retry_on_mixed_exclusions():
    retries = 0

    @retry(exceptions=(ValueError, TypeError), excluded_exceptions=(ValueError,), max_retries=5)
    def raise_mixed_exceptions():
        nonlocal retries
        retries += 1
        if retries == 5:
            raise ValueError("Simulating excluded ValueError")
        raise TypeError("Simulating TypeError")

    with pytest.raises(ValueError, match="Simulating excluded ValueError"):
        raise_mixed_exceptions()

    assert retries == 5
