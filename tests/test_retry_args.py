import pytest
from retry_reloaded import retry


def test_valid_arguments():
    @retry()
    def valid_function():
        return "Valid function"

    assert callable(valid_function)


def test_invalid_exceptions():
    with pytest.raises(TypeError):
        @retry(exceptions=(ValueError, "not_an_exception_subclass"))
        def invalid_exceptions_function():
            pass


def test_invalid_max_retries():
    with pytest.raises(TypeError):
        @retry(max_retries="not_an_integer")
        def invalid_max_retries_function():
            pass


def test_invalid_backoff():
    with pytest.raises(TypeError):
        @retry(backoff="not_a_backoff_instance")
        def invalid_backoff_function():
            pass


def test_invalid_timeout():
    with pytest.raises(TypeError):
        @retry(timeout="not_a_float")
        def invalid_timeout_function():
            pass


def test_invalid_deadline():
    with pytest.raises(TypeError):
        @retry(deadline="not_a_float")
        def invalid_deadline_function():
            pass


def test_invalid_logger():
    with pytest.raises(TypeError):
        @retry(logger="not_a_logger_instance")
        def invalid_logger_function():
            pass


def test_invalid_log_retry_traceback():
    with pytest.raises(TypeError):
        @retry(log_retry_traceback="not_a_boolean")
        def invalid_log_retry_traceback_function():
            pass


def test_invalid_failure_callback():
    with pytest.raises(TypeError):
        @retry(failure_callback="not_a_callable")
        def invalid_failure_callback_function():
            pass


def test_invalid_retry_callback():
    with pytest.raises(TypeError):
        @retry(retry_callback="not_a_callable")
        def invalid_retry_callback_function():
            pass


def test_invalid_successful_retry_callback():
    with pytest.raises(TypeError):
        @retry(successful_retry_callback="not_a_callable")
        def invalid_successful_retry_callback_function():
            pass


def test_invalid_reraise_exception():
    with pytest.raises(TypeError):
        @retry(reraise_exception="not_a_boolean")
        def invalid_reraise_exception_function():
            pass
