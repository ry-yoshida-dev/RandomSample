import math
from collections.abc import Iterable

from array_sampling.exceptions import InvalidSampleSizeError
from array_sampling.random_generator import RandomGenerator
from array_sampling.sample_result import SampleResult


class UniformReservoir[T]:
    """Incremental uniform fixed-size sample of a stream of unknown length.

    Implements Li's Algorithm L: after the reservoir is filled, the number of
    elements to skip is drawn directly, so random numbers are consumed only
    ``O(k * (1 + log(n / k)))`` times and memory stays ``O(k)``. Use it when
    elements arrive one by one; ``ReservoirSampler`` wraps it for a single
    pass over an iterable.

    Parameters
    ----------
    capacity : int
        Maximum number of elements kept in the reservoir.
    random_generator : RandomGenerator | None
        Random number generator. A non-deterministic one is created when omitted.

    Raises
    ------
    InvalidSampleSizeError
        If ``capacity`` is negative.
    """

    def __init__(self, capacity: int, random_generator: RandomGenerator | None = None) -> None:
        if capacity < 0:
            raise InvalidSampleSizeError(f"Capacity must be non-negative, got {capacity}.")
        self._capacity: int = capacity
        self._random_generator: RandomGenerator = (
            random_generator if random_generator is not None else RandomGenerator()
        )
        self._items: list[T] = []
        self._positions: list[int] = []
        self._seen_count: int = 0
        self._log_weight: float = 0.0
        self._next_accept_position: int = capacity

    @property
    def capacity(self) -> int:
        """Maximum number of elements kept in the reservoir."""
        return self._capacity

    @property
    def seen_count(self) -> int:
        """Number of elements observed so far."""
        return self._seen_count

    def add(self, item: T) -> None:
        """Observe one element of the stream.

        Parameters
        ----------
        item : T
            Next element of the stream.
        """
        position: int = self._seen_count
        self._seen_count += 1
        if self._capacity == 0:
            return
        if position < self._capacity:
            self._items.append(item)
            self._positions.append(position)
            if position == self._capacity - 1:
                self._advance_weight()
                self._schedule_next_accept(position)
            return
        if position != self._next_accept_position:
            return
        slot: int = self._random_generator.random_index(self._capacity)
        self._items[slot] = item
        self._positions[slot] = position
        self._advance_weight()
        self._schedule_next_accept(position)

    def extend(self, items: Iterable[T]) -> None:
        """Observe every element of an iterable.

        Parameters
        ----------
        items : Iterable[T]
            Elements to observe, consumed lazily.
        """
        for item in items:
            self.add(item)

    def result(self) -> SampleResult[T]:
        """Return the current sample ordered by stream position.

        Returns
        -------
        SampleResult[T]
            Sampled elements with their zero-based stream positions.
        """
        order: list[int] = sorted(range(len(self._items)), key=self._positions.__getitem__)
        return SampleResult(
            items=tuple(self._items[slot] for slot in order),
            indices=tuple(self._positions[slot] for slot in order),
        )

    def _advance_weight(self) -> None:
        self._log_weight += math.log(self._random_generator.open_unit_interval()) / self._capacity

    def _schedule_next_accept(self, position: int) -> None:
        log_skip_base: float = self._log_one_minus_exp(self._log_weight)
        skip: int = math.floor(
            math.log(self._random_generator.open_unit_interval()) / log_skip_base
        )
        self._next_accept_position = position + skip + 1

    @staticmethod
    def _log_one_minus_exp(log_value: float) -> float:
        if log_value > -math.log(2.0):
            return math.log(-math.expm1(log_value))
        return math.log1p(-math.exp(log_value))
