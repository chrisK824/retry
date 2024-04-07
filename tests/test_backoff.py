from retry_reloaded.backoff import (
    FixedBackOff,
    LinearBackOff,
    RandomUniformBackOff,
    ExponentialBackOff,
)
import pytest


@pytest.mark.parametrize(
    "base_delay, jitter",
    [
        (1.0, None),
        (1.0, (0.1, 0.5)),
        (0.0, None),
        (0.0, (0.0, 0.0)),
    ],
)
def test_fixed_backoff(base_delay, jitter):
    backoff = FixedBackOff(base_delay, jitter)

    for _round in range(5):
        delay = backoff.delay
        assert isinstance(delay, float)
        if jitter is None:
            assert delay == base_delay
        else:
            low_jitter = jitter[0] if _round else 0
            high_jitter = jitter[1] if _round else 0
            assert base_delay + low_jitter <= delay
            assert delay <= base_delay + high_jitter


@pytest.mark.parametrize(
    "base_delay, step, jitter",
    [
        (1.0, 0.5, None),
        (1.0, 0.5, (0.1, 0.5)),
        (0.0, 0.0, None),
        (0.0, 0.0, (0.0, 0.0)),
    ],
)
def test_linear_backoff(base_delay, step, jitter):
    backoff = LinearBackOff(base_delay, step, jitter)

    for _round in range(5):
        delay = backoff.delay
        assert isinstance(delay, float)
        expected_delay = base_delay + (step * _round)
        if jitter is None:
            assert delay == expected_delay
        else:
            low_jitter = jitter[0] if _round else 0
            high_jitter = jitter[1] if _round else 0
            assert expected_delay + low_jitter <= delay
            assert delay <= expected_delay + high_jitter


@pytest.mark.parametrize(
    "base_delay, min_delay, max_delay",
    [
        (1.0, 0.5, 2.0),
        (1.0, 3.4, 5.6),
        (0.0, 0.0, 0.0),
    ],
)
def test_random_uniform_backoff(base_delay, min_delay, max_delay):
    backoff = RandomUniformBackOff(base_delay, min_delay, max_delay)

    delay = backoff.delay
    assert isinstance(delay, float)
    assert delay == base_delay
    for _ in range(5):
        delay = backoff.delay
        assert isinstance(delay, float)
        assert min_delay <= delay <= max_delay


@pytest.mark.parametrize(
    "base_delay, jitter",
    [
        (1.0, None),
        (1.0, (0.1, 0.5)),
        (0.0, None),
        (0.0, (0.0, 0.0)),
    ],
)
def test_exponential_backoff(base_delay, jitter):
    backoff = ExponentialBackOff(base_delay, jitter)

    for _round in range(5):
        delay = backoff.delay
        assert isinstance(delay, float)
        expected_delay = base_delay * (2**_round)
        if jitter is None:
            assert delay == expected_delay
        else:
            low_jitter = jitter[0] if _round else 0
            high_jitter = jitter[1] if _round else 0
            assert expected_delay + low_jitter <= delay
            assert delay <= expected_delay + high_jitter


def test_fixed_backoff_invalid_jitter():
    with pytest.raises(ValueError):
        FixedBackOff(1.0, (0.5, 0.1))

    with pytest.raises(TypeError):
        FixedBackOff(1.0, (0.5,))

    with pytest.raises(TypeError):
        FixedBackOff(1.0, (0.5, 0.1, 0.2))

    with pytest.raises(TypeError):
        FixedBackOff(1.0, (0.5, 'a'))

    with pytest.raises(TypeError):
        FixedBackOff(1.0, ('a', 0.5))

    with pytest.raises(TypeError):
        FixedBackOff(1.0, ('a', 'b'))


def test_linear_backoff_invalid_jitter():
    with pytest.raises(ValueError):
        LinearBackOff(1.0, 0.5, (0.5, 0.1))

    with pytest.raises(TypeError):
        LinearBackOff(1.0, 0.5, (0.5,))

    with pytest.raises(TypeError):
        LinearBackOff(1.0, 0.5, (0.5, 0.1, 0.2))

    with pytest.raises(TypeError):
        LinearBackOff(1.0, 0.5, (0.5, 'a'))

    with pytest.raises(TypeError):
        LinearBackOff(1.0, 0.5, ('a', 0.5))

    with pytest.raises(TypeError):
        LinearBackOff(1.0, 0.5, ('a', 'b'))


def test_exponential_backoff_invalid_jitter():
    with pytest.raises(ValueError):
        ExponentialBackOff(1.0, (0.5, 0.1))

    with pytest.raises(TypeError):
        ExponentialBackOff(1.0, (0.5,))

    with pytest.raises(TypeError):
        ExponentialBackOff(1.0, (0.5, 0.1, 0.2))

    with pytest.raises(TypeError):
        ExponentialBackOff(1.0, (0.5, 'a'))

    with pytest.raises(TypeError):
        ExponentialBackOff(1.0, ('a', 0.5))

    with pytest.raises(TypeError):
        ExponentialBackOff(1.0, ('a', 'b'))


def test_backoff_invalid_base_delay():
    with pytest.raises(ValueError):
        ExponentialBackOff(-1)

    with pytest.raises(TypeError):
        LinearBackOff("not float")

    with pytest.raises(TypeError):
        RandomUniformBackOff(None)
