from abc import ABC, abstractmethod
import random
from typing import Optional, Tuple


class BackOff(ABC):
    """
    Base class for implementing backoff strategies.
    """
    def __init__(
        self, base_delay: float = 0, jitter: Optional[Tuple[float, float]] = None
    ):
        """
        Initialize BackOff object.

        Args:
            base_delay (float): Initial delay value, applies on
                first round of delay and calculations of next rounds.
                Defaults to 0.
            jitter (Optional[Tuple[float, float]]): Tuple specifying
                the range for jitter (random delay on top of
                the calculated delay), applying after the first round.
                If provided, it should be a tuple of two floats in sorted order.
                Defaults to None.
        Raises:
            TypeError: If the `jitter` is provided and not a tuple of two floats,
                or if the values are not of type float.
            ValueError: If the `jitter` values are not in sorted order.
        """
        self._base_delay = self._validate_base_delay(base_delay)
        self._delay = base_delay
        self._jitter = self._validate_jitter(jitter)
        self._round = 0

    def _validate_base_delay(self, base_delay: float) -> Optional[Tuple[float, float]]:
        """
        Validate the base delay of backoff strategy.

        Args:
            base_delay (float): Initial delay value, applies on
                first round of delay and calculations of next rounds.

        Returns:
            float: The validated base delay of backoff strategy.

        Raises:
            TypeError: If the `base_delay` is not a positive float,
                or if the values are not of type float.
            ValueError: If the `jitter` values are not in sorted order.
        """
        if not isinstance(base_delay, (int, float)):
            raise TypeError("Base delay must be a float.")

        if base_delay < 0:
            raise ValueError("Base delay must be a positive or zero float.")

        return base_delay

    def _validate_jitter(self, jitter: Optional[Tuple[float, float]]) -> Optional[Tuple[float, float]]:
        """
        Validate the jitter values.

        Args:
            jitter (Optional[Tuple[float, float]]): Tuple specifying
                the range for jitter (random delay on top of
                the calculated delay), applying after the first round.

        Returns:
            Optional[Tuple[float, float]]: The validated jitter values.

        Raises:
            TypeError: If the `jitter` is not a tuple of two floats,
                or if the values are not of type float.
            ValueError: If the `jitter` values are not in sorted order.
        """
        if jitter is None:
            return None

        if not isinstance(jitter, tuple) or len(jitter) != 2:
            raise TypeError("Jitter must be a tuple of two float values.")

        min_val, max_val = jitter
        if not (isinstance(min_val, (int, float)) and isinstance(max_val, (int, float))):
            raise TypeError("Jitter values must be of type float.")

        if min_val < 0 or max_val < 0:
            raise ValueError(
                "Jitter values must be positive values."
                )

        if min_val > max_val:
            raise ValueError(
                "Jitter values must be in sorted order as they represent minimum and maximum values."
            )

        return min_val, max_val

    @abstractmethod
    def _calculate_next_delay(self):
        """
        Abstract method to calculate the delay
        for the next round of backoff.
        """
        pass

    @property
    def delay(self) -> float:
        """
        Property to get the current delay.

        Returns:
            float: Current delay value.
        """
        self._calculate_next_delay()
        return self._delay


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
    def __init__(
        self,
        base_delay: float,
        step: float,
        jitter: Optional[Tuple[float, float]] = None,
    ):
        """
        Initialize LinearBackOff object.

        Args:
            initial_delay (float): Initial delay value, applies on
            first round of delay.
            step (float): Step value to increment delay.
            jitter (Optional[Tuple[float, float]]): Tuple specifying
                the range for jitter (random delay on top of
                the calculated delay), applying after the first round.
        """
        super().__init__(base_delay=base_delay, jitter=jitter)
        self.step = step if step else base_delay

    def _calculate_next_delay(self):
        """
        Calculate the next round's delay for linear backoff strategy.
        """
        self._delay = self._base_delay + self.step * self._round
        if self._round > 0 and self._jitter:
            self._delay += random.uniform(self._jitter[0], self._jitter[1])
        self._round += 1


class RandomUniformBackOff(BackOff):
    """
    Random uniform backoff strategy.
    """
    def __init__(self, base_delay: float, min_delay: float, max_delay: float):
        """
        Initialize RandomUniformBackOff object.

        Args:
            initial_delay (float): Initial delay value, applies on
            first round of delay.
            min_delay (float): Minimum delay value.
            max_delay (float): Maximum delay value.
            jitter (Optional[Tuple[float, float]]): Tuple specifying
                the range for jitter (random delay on top of
                the calculated delay), applying after the first round.
        """
        super().__init__(base_delay=base_delay)
        self.min_delay = min_delay
        self.max_delay = max_delay

    def _calculate_next_delay(self):
        """
        Calculate the next round's delay for linear backoff strategy.
        """
        if self._round > 0:
            self._delay = random.uniform(self.min_delay, self.max_delay)
        self._round += 1


class ExponentialBackOff(BackOff):
    """
    Exponential backoff strategy.
    """
    def _calculate_next_delay(self):
        """
        Calculate the next round's delay for linear backoff strategy.
        """
        self._delay = self._base_delay * 2**self._round
        if self._jitter and self._round > 0:
            self._delay += random.uniform(self._jitter[0], self._jitter[1])
        self._round += 1
