import pytest
from unittest.mock import patch, Mock
from itertools import count


def mocked_time():
    for i in count():
        yield i


def mocked_sleep():
    pass


@pytest.fixture
def time_patch():
    with patch('retry.retry.time', side_effect=mocked_time()):
        yield


@pytest.fixture
def sleep_patch():
    with patch('retry.retry.sleep') as mock_sleep:
        yield mock_sleep


@pytest.fixture
def retry_callback():
    yield Mock()


@pytest.fixture
def successfull_retry_callback():
    yield Mock()


@pytest.fixture
def failure_callback():
    yield Mock()
