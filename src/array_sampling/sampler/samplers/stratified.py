from collections.abc import Callable, Hashable
from typing import override

from array_sampling.internal.index_drawer import IndexDrawer
from array_sampling.internal.random_access_array import RandomAccessArray
from array_sampling.internal.strata import Strata
from array_sampling.random_generator import RandomGenerator
from array_sampling.replacement_mode import ReplacementMode
from array_sampling.sampler.allocation_strategy import AllocationStrategy
from array_sampling.sampler.sampler import Sampler
from array_sampling.sampler.stratum_allocator import StratumAllocator
from array_sampling.sizing.sample_size import SampleSize
from array_sampling.stratified_sample_result import StratifiedSampleResult


class StratifiedSampler[T, K: Hashable](Sampler[T]):
    """Split a total sample size across strata and sample each one uniformly.

    Parameters
    ----------
    stratum_of : Callable[[T], K]
        Function that returns the stratum label of an element.
    size : SampleSize
        Total number or fraction of elements to draw.
    allocation : AllocationStrategy
        Rule used to split the total across strata.
    minimum_per_stratum : int
        Count guaranteed to every stratum, capped at the stratum size when
        sampling without replacement.
    replacement : ReplacementMode
        Whether an element may be drawn more than once.
    random_generator : RandomGenerator | None
        Random number generator. A non-deterministic one is created when omitted.

    Raises
    ------
    InvalidSampleSizeError
        If ``minimum_per_stratum`` is negative.
    """

    def __init__(
        self,
        stratum_of: Callable[[T], K],
        size: SampleSize,
        *,
        allocation: AllocationStrategy = AllocationStrategy.PROPORTIONAL,
        minimum_per_stratum: int = 0,
        replacement: ReplacementMode = ReplacementMode.SWOR,
        random_generator: RandomGenerator | None = None,
    ) -> None:
        super().__init__(random_generator)
        self._stratum_of: Callable[[T], K] = stratum_of
        self._size: SampleSize = size
        self._allocator: StratumAllocator = StratumAllocator(allocation, minimum_per_stratum)
        self._replacement: ReplacementMode = replacement
        self._index_drawer: IndexDrawer = IndexDrawer(self._random_generator)

    @override
    def sample(self, population: RandomAccessArray[T]) -> StratifiedSampleResult[T, K]:
        """Draw a stratified sample.

        Parameters
        ----------
        population : RandomAccessArray[T]
            Array to sample from.

        Returns
        -------
        StratifiedSampleResult[T, K]
            Per-stratum samples in order of first appearance of each stratum.

        Raises
        ------
        InvalidSampleSizeError
            If the total is smaller than the guaranteed minimums.
        InsufficientPopulationError
            If the population cannot supply the requested sample.
        """
        strata: Strata[K] = Strata[K].from_population(population, self._stratum_of)
        counts: dict[K, int] = self._allocator.allocate(
            strata.sizes, self._size.resolve(len(population)), self._replacement
        )
        return strata.draw(population, counts, self._replacement, self._index_drawer)
