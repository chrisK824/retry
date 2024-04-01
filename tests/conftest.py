import pytest
from unittest.mock import Mock


@pytest.fixture
def retry_callback():
    yield Mock()


@pytest.fixture
def successful_retry_callback():
    yield Mock()


@pytest.fixture
def failure_callback():
    yield Mock()
