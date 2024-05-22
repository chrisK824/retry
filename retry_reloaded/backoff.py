from abc import ABC, abstractmethod
import random
from typing import Optional, Tuple


class BackOff(ABC):
    """
    Base class for implementing backoff strategies.
    """
    def __init__(self, base_delay: float = 0, jitter: Optional[Tuple[float, float]] = None):
        """
        Initialize BackOff object.

        Args:
            base_delay (float): Initial delay value, applies on the first round of delay and
                calculations of next rounds. Defaults to 0.
            jitter (Optional[Tuple[float, float]]): Tuple specifying the range for jitter (random delay on
                top of the calculated delay), applying after the first round. If provided, it should be a
                tuple of two numbers in sorted order. Defaults to None.

        Raises:
            TypeError: If `jitter` is provided and not a tuple of two numbers.
            ValueError: If the `jitter` values are not in sorted order.
        """
        self._base_delay = self._validate_base_delay(base_delay)
        self._delay = base_delay
        self._jitter = self._validate_jitter(jitter)
        self._round = 0

    def _validate_base_delay(self, base_delay: float) -> float:
        """
        Validate the base delay of backoff strategy.

        Args:
            base_delay (float): Initial delay value, applies on
                first round of delay and calculations of next rounds.

        Returns:
            float: The validated base delay of backoff strategy.

        Raises:
            TypeError: If `base_delay` is not a number.
            ValueError: If `base_delay` is negative.
        """
        if not isinstance(base_delay, (int, float)):
            raise TypeError("Base delay must be a number.")

        if base_delay < 0:
            raise ValueError("Base delay must be a positive number.")

        return float(base_delay)

    def _validate_jitter(self, jitter: Optional[Tuple[float, float]]) -> Optional[Tuple[float, float]]:
        """
        Validate the jitter values.

        Args:
            jitter (Optional[Tuple[float, float]]): Tuple specifying the range for jitter.

        Returns:
            Optional[Tuple[float, float]]: The validated jitter values.

        Raises:
            TypeError: If `jitter` is not a tuple of two numbers.
            ValueError: If `jitter` values are not positive or not in sorted order.
        """
        if jitter is None:
            return None

        if not isinstance(jitter, tuple) or len(jitter) != 2:
            raise TypeError("Jitter must be a tuple of two float values.")

        min_val, max_val = jitter
        if not (isinstance(min_val, (int, float)) and isinstance(max_val, (int, float))):
            raise TypeError("Jitter values must be a number.")

        if min_val < 0 or max_val < 0:
            raise ValueError("Jitter values must be positive numbers.")

        if min_val > max_val:
            raise ValueError("Jitter values must be in sorted order.")

        return float(min_val), float(max_val)

    def _validate_step(self, step: Optional[float]) -> Optional[float]:
        """
        Validate the step delay value. If step is not specified then base delay of backoff
        strategy is used instead.

        Args:
            step (float): Step value to increment delay.

        Returns:
            float: The validated step value.

        Raises:
            TypeError: If `step` is specified and not a number.
            ValueError: If `step` is specified number but not positive one.
        """
        if step is None:
            return self._base_delay

        if not isinstance(step, (int, float)):
            raise TypeError("Step must be number.")

        if step < 0:
            raise ValueError("Step must be a positive number.")

        return float(step)

    def _validate_max(self, max: Optional[float]) -> Optional[float]:
        """
        Validate the max delay value.

        Args:
            max (Optional[float]): Maximum delay value.

        Returns:
            Optional[float]: The validated max delay value.

        Raises:
            TypeError: If `max` is not a number.
            ValueError: If `max` is less than the base delay.
        """
        if max is None:
            return None

        if not isinstance(max, (int, float)):
            raise TypeError("Max must be a number.")

        if max < self._base_delay:
            raise ValueError("Max must be a value equal to or greater than the base delay.")

        return float(max)

    @abstractmethod
    def _calculate_next_delay(self):
        """
        Abstract method to calculate the delay for the next round of backoff.
        """
        pass

    @property
    def delay(self) -> float:
        """
        Get the current delay.

        Returns:
            float: Current delay value.
        """
        self._calculate_next_delay()
        return self._delay

    def reset(self) -> None:
        """
        Reset the current delay.
        """
        self._round = 0


class FixedBackOff(BackOff):
    """
    Fixed backoff strategy.
    """
    def _calculate_next_delay(self):
        """
        Calculate the next round's delay for fixed backoff strategy.
        """
        self._delay = self._base_delay
        if self._round > 0 and self._jitter:
            self._delay += random.uniform(self._jitter[0], self._jitter[1])
        self._round += 1


class LinearBackOff(BackOff):
    """
    Linear backoff strategy.
    """
    def __init__(self, base_delay: float, step: float, jitter: Optional[Tuple[float, float]] = None,
                 max: Optional[float] = None):
        """
        Initialize LinearBackOff object.

        Args:
            base_delay (float): Initial delay value, applies on the first round of delay.
            step (float): Step value to increment delay. If not specified defaults to base_delay.
            jitter (Optional[Tuple[float, float]]): Tuple specifying the range for jitter (random delay on
                top of the calculated delay), applying after the first round. Defaults to None.
            max (Optional[float]): Maximum delay value. Defaults to None.
        """
        super().__init__(base_delay=base_delay, jitter=jitter)
        self._step = self._validate_step(step)
        self._max = self._validate_max(max)

    def _calculate_next_delay(self):
        """
        Calculate the next round's delay for linear backoff strategy.
        """
        self._delay = self._base_delay + self._step * self._round
        if self._round > 0 and self._jitter:
            self._delay += random.uniform(self._jitter[0], self._jitter[1])
        if self._max is not None:
            self._delay = min(self._delay, self._max)
        self._round += 1


class RandomUniformBackOff(BackOff):
    """
    Random uniform backoff strategy.
    """
    def __init__(self, base_delay: float, min_delay: float, max_delay: float):
        """
        Initialize RandomUniformBackOff object.

        Args:
            base_delay (float): Initial delay value, applies on the first round of delay.
            min_delay (float): Minimum delay value.
            max_delay (float): Maximum delay value.
        """
        super().__init__(base_delay=base_delay)
        self._min_delay = min_delay
        self._max_delay = max_delay

    def _calculate_next_delay(self):
        """
        Calculate the next round's delay for random uniform backoff strategy.
        """
        if self._round > 0:
            self._delay = random.uniform(self._min_delay, self._max_delay)
        self._round += 1


class ExponentialBackOff(BackOff):
    """
    Exponential backoff strategy.
    """
    DEFAULT_BASE = 2

    def __init__(self, base_delay: float, base: Optional[float] = None, jitter: Optional[Tuple[float, float]] = None,
                 max: Optional[float] = None):
        """
        Initialize ExponentialBackOff object.

        Args:
            base_delay (float): Initial delay value, applies on the first round of delay.
            base (Optional[float]): Value to use as base for exponentiation. Defaults to 2.
            jitter (Optional[Tuple[float, float]]): Tuple specifying the range for jitter (random delay on
                top of the calculated delay), applying after the first round. Defaults to None.
            max (Optional[float]): Maximum delay value. Defaults to None.
        """
        super().__init__(base_delay=base_delay, jitter=jitter)
        self._base = base if base is not None else ExponentialBackOff.DEFAULT_BASE
        self._max = self._validate_max(max)

    def _calculate_next_delay(self):
        """
        Calculate the next round's delay for exponential backoff strategy.
        """
        self._delay = self._base_delay * self._base**self._round
        if self._jitter and self._round > 0:
            self._delay += random.uniform(self._jitter[0], self._jitter[1])
        if self._max is not None:
            self._delay = min(self._delay, self._max)
        self._round += 1
