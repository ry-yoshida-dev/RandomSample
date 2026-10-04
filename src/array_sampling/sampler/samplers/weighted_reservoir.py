from collections.abc import Callable, Iterable
from typing import override

from array_sampling.exceptions import InvalidSampleSizeError
from array_sampling.random_generator import RandomGenerator
from array_sampling.reservoir import WeightedReservoir
from array_sampling.sample_result import SampleResult
from array_sampling.sampler.base import Sampler


class WeightedReservoirSampler[T](Sampler[T]):
    """Weighted fixed-size sample without replacement from a single pass.

    Each call to ``sample`` feeds a fresh ``WeightedReservoir``, so memory
    stays ``O(k)`` regardless of the input length.

    Parameters
    ----------
    capacity : int
        Maximum number of elements to keep.
    weight_of : Callable[[T], float]
        Function that returns the non-negative weight of an element. Elements
        with zero weight are never selected.
    random_generator : RandomGenerator | None
        Random number generator. A non-deterministic one is created when omitted.

    Raises
    ------
    InvalidSampleSizeError
        If ``capacity`` is negative.
    """

    def __init__(
        self,
        capacity: int,
        weight_of: Callable[[T], float],
        random_generator: RandomGenerator | None = None,
    ) -> None:
        if capacity < 0:
            raise InvalidSampleSizeError(f"Capacity must be non-negative, got {capacity}.")
        super().__init__(random_generator)
        self._capacity: int = capacity
        self._weight_of: Callable[[T], float] = weight_of

    @property
    def capacity(self) -> int:
        """Maximum number of elements to keep."""
        return self._capacity

    @override
    def sample(self, population: Iterable[T]) -> SampleResult[T]:
        """Draw a weighted sample in a single pass.

        Parameters
        ----------
        population : Iterable[T]
            Elements to sample from, consumed lazily.

        Returns
        -------
        SampleResult[T]
            Sampled elements with their zero-based positions, in input order.

        Raises
        ------
        InvalidWeightError
            If a weight is negative or not finite.
        """
        reservoir: WeightedReservoir[T] = WeightedReservoir(self._capacity, self._random_generator)
        reservoir.extend(population, self._weight_of)
        return reservoir.result()
