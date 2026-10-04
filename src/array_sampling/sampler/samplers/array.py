from collections.abc import Callable
from typing import override

from array_sampling.internal.index_drawer import IndexDrawer
from array_sampling.internal.random_access_array import RandomAccessArray
from array_sampling.internal.weight_validator import WeightValidator
from array_sampling.random_generator import RandomGenerator
from array_sampling.replacement_mode import ReplacementMode
from array_sampling.sample_result import SampleResult
from array_sampling.sampler.sampler import Sampler
from array_sampling.sizing.sample_size import SampleSize


class ArraySampler[T](Sampler[T]):
    """Uniform or weighted sample from a random-access array.

    Indices are drawn first and elements are fetched afterwards, so uniform
    sampling touches only the selected elements and uses ``O(k)`` memory.
    Weighted sampling evaluates ``weight_of`` on every element and uses
    ``O(n)`` memory.

    Parameters
    ----------
    size : SampleSize
        Number or fraction of elements to draw.
    replacement : ReplacementMode
        Whether an element may be drawn more than once.
    weight_of : Callable[[T], float] | None
        Function that returns the non-negative weight of an element. Sampling
        is uniform when omitted. Elements with zero weight are never selected.
    random_generator : RandomGenerator | None
        Random number generator. A non-deterministic one is created when omitted.
    """

    def __init__(
        self,
        size: SampleSize,
        *,
        replacement: ReplacementMode = ReplacementMode.SWOR,
        weight_of: Callable[[T], float] | None = None,
        random_generator: RandomGenerator | None = None,
    ) -> None:
        super().__init__(random_generator)
        self._size: SampleSize = size
        self._replacement: ReplacementMode = replacement
        self._weight_of: Callable[[T], float] | None = weight_of
        self._index_drawer: IndexDrawer = IndexDrawer(self._random_generator)

    @override
    def sample(self, population: RandomAccessArray[T]) -> SampleResult[T]:
        """Draw elements from an array.

        Parameters
        ----------
        population : RandomAccessArray[T]
            Array to sample from.

        Returns
        -------
        SampleResult[T]
            Selected elements and their indices, in draw order.

        Raises
        ------
        InvalidWeightError
            If a weight is negative or not finite.
        InsufficientPopulationError
            If the population cannot supply the requested sample.
        """
        sample_count: int = self._size.resolve(len(population))
        indices: tuple[int, ...] = self._draw_indices(population, sample_count)
        return SampleResult(items=tuple(population[index] for index in indices), indices=indices)

    def _draw_indices(self, population: RandomAccessArray[T], sample_count: int) -> tuple[int, ...]:
        match self._weight_of:
            case None:
                return self._index_drawer.draw_uniform(
                    len(population), sample_count, self._replacement
                )
            case weight_of:
                weights: list[float] = WeightValidator.validate_weights(
                    [weight_of(item) for item in population]
                )
                return self._index_drawer.draw_weighted(weights, sample_count, self._replacement)
