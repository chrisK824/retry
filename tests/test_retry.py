import pytest
from retry.retry import retry
from retry.utils._exceptions import (
    MaxRetriesException,
    RetriesTimeoutException,
    RetriesDeadlineException
)
from retry.utils.backoff import (
    FixedBackOff,
    RandomUniformBackOff,
    ExponentialBackOff,
    LinearBackOff
)
from time import time, sleep


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


# def test_timeout():
#     retries = 0

#     @retry(timeout=2, backoff=FixedBackOff(initial_delay=1))
#     def timeout_function():
#         nonlocal retries
#         retries += 1
#         print(retries)
#         raise Exception("Simulating failure")

#     with pytest.raises(RetriesTimeoutException):
#         timeout_function()

#     assert len(retries) == 3


# def test_deadline():
#     start_time = None
#     retries = []

#     @retry(deadline=2, backoff=FixedBackOff(initial_delay=1))
#     def deadline_function():
#         nonlocal start_time
#         nonlocal retries
#         if start_time is None:
#             start_time = time.time()
#         retries.append(time.time() - start_time)
#         sleep(1)
#         raise Exception("Simulating failure")

#     with pytest.raises(RetriesDeadlineException):
#         deadline_function()

#     assert len(retries) == 3
