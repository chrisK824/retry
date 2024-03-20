from abc import ABC, abstractmethod
import random
from typing import Optional, Tuple


class BackOff(ABC):
    """
    Base class for implementing backoff strategies.
    """
    def __init__(self,
                 initial_delay: float,
                 jitter: Optional[Tuple[float, float]] = None):
        """
        Initialize BackOff object.

        Args:
            initial_delay (float): Initial delay value, applies on
            first round of delay.
            jitter (Optional[Tuple[float, float]]): Tuple specifying
                the range for jitter (random delay on top of
                the calculated delay), applying after the first round.
        """
        self._base_delay = initial_delay
        self._delay = initial_delay
        self._jitter = jitter
        self._round = 0

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
    def __init__(self,
                 initial_delay: float,
                 step: float,
                 jitter: Optional[Tuple[float, float]] = None):
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
        super().__init__(initial_delay=initial_delay, jitter=jitter)
        self.step = step

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

    def __init__(self,
                 initial_delay: float,
                 min_delay: float,
                 max_delay: float):
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
        super().__init__(initial_delay=initial_delay)
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
        self._delay = self._base_delay * 2 ** self._round
        if self._jitter and self._round > 0:
            self._delay += random.uniform(self._jitter[0], self._jitter[1])
        self._round += 1
