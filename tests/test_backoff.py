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
    "base_delay, step, jitter, max_delay",
    [
        (1.0, 0.5, None, None),
        (1.0, 0.5, (0.1, 0.5), None),
        (0.0, 0.0, None, None),
        (0.0, 0.0, (0.0, 0.0), None),
        (1.0, 0.5, None, 2.0),
        (1.0, 0.5, (0.1, 0.5), 2.0),
    ],
)
def test_linear_backoff(base_delay, step, jitter, max_delay):
    backoff = LinearBackOff(base_delay, step, jitter, max_delay)

    for _round in range(5):
        delay = backoff.delay
        assert isinstance(delay, float)

        if max_delay is not None:
            expected_delay = min(base_delay + (step * _round), max_delay)
        else:
            expected_delay = base_delay + (step * _round)

        if jitter is None:
            assert delay == expected_delay
        else:
            low_jitter = jitter[0] if _round else 0
            high_jitter = jitter[1] if _round else 0
            if max_delay is None:
                assert expected_delay + low_jitter <= delay
                assert delay <= expected_delay + high_jitter
            else:
                assert delay <= max_delay

    backoff.reset()
    delay = backoff.delay
    assert delay == base_delay


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
    "base_delay, base, jitter, max_delay",
    [
        (1.0, None, None, None),
        (1.0, None, (0.1, 0.5), None),
        (0.0, None, None, None),
        (0.0, None, (0.0, 0.0), None),
        (1.0, None, None, 10.0),
        (1.0, None, (0.1, 0.5), 10.0),
    ],
)
def test_exponential_backoff(base_delay, base, jitter, max_delay):
    backoff = ExponentialBackOff(base_delay, base, jitter, max_delay)

    for _round in range(5):
        delay = backoff.delay
        assert isinstance(delay, float)
        base_value = base if base is not None else 2

        if max_delay is not None:
            expected_delay = min(base_delay * (base_value**_round), max_delay)
        else:
            expected_delay = base_delay * (base_value**_round)

        if jitter is None:
            assert delay == expected_delay
        else:
            low_jitter = jitter[0] if _round else 0
            high_jitter = jitter[1] if _round else 0
            if max_delay is None:
                assert expected_delay + low_jitter <= delay
                assert delay <= expected_delay + high_jitter
            else:
                assert delay <= max_delay

    backoff.reset()
    delay = backoff.delay
    assert delay == base_delay


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
        ExponentialBackOff(1.0, jitter=(0.5, 0.1))

    with pytest.raises(TypeError):
        ExponentialBackOff(1.0, jitter=(0.5,))

    with pytest.raises(TypeError):
        ExponentialBackOff(1.0, jitter=(0.5, 0.1, 0.2))

    with pytest.raises(TypeError):
        ExponentialBackOff(1.0, jitter=(0.5, 'a'))

    with pytest.raises(TypeError):
        ExponentialBackOff(1.0, jitter=('a', 0.5))

    with pytest.raises(TypeError):
        ExponentialBackOff(1.0, jitter=('a', 'b'))


def test_backoff_invalid_base_delay():
    with pytest.raises(ValueError):
        ExponentialBackOff(-1)

    with pytest.raises(TypeError):
        LinearBackOff("not float")

    with pytest.raises(TypeError):
        RandomUniformBackOff(None)
