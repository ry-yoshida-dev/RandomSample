from collections.abc import Iterable
from typing import override

from array_sampling.exceptions import InvalidSampleSizeError
from array_sampling.random_generator import RandomGenerator
from array_sampling.reservoir import UniformReservoir
from array_sampling.sample_result import SampleResult
from array_sampling.sampler.base import Sampler


class ReservoirSampler[T](Sampler[T]):
    """Uniform fixed-size sample from a single pass over an iterable.

    Each call to ``sample`` feeds a fresh ``UniformReservoir``, so memory stays
    ``O(k)`` regardless of the input length.

    Parameters
    ----------
    capacity : int
        Maximum number of elements to keep.
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
        super().__init__(random_generator)
        self._capacity: int = capacity

    @property
    def capacity(self) -> int:
        """Maximum number of elements to keep."""
        return self._capacity

    @override
    def sample(self, population: Iterable[T]) -> SampleResult[T]:
        """Draw a uniform sample in a single pass.

        Parameters
        ----------
        population : Iterable[T]
            Elements to sample from, consumed lazily.

        Returns
        -------
        SampleResult[T]
            Sampled elements with their zero-based positions, in input order.
        """
        reservoir: UniformReservoir[T] = UniformReservoir(self._capacity, self._random_generator)
        reservoir.extend(population)
        return reservoir.result()
