from collections.abc import Callable, Hashable, Mapping
from typing import override

from array_sampling.internal.index_drawer import IndexDrawer
from array_sampling.internal.random_access_array import RandomAccessArray
from array_sampling.internal.strata import Strata
from array_sampling.random_generator import RandomGenerator
from array_sampling.replacement_mode import ReplacementMode
from array_sampling.sampler.sampler import Sampler
from array_sampling.sizing.sample_size import SampleSize
from array_sampling.stratified_sample_result import StratifiedSampleResult


class QuotaSampler[T, K: Hashable](Sampler[T]):
    """Draw an explicit sample size from each stratum.

    Each quota is resolved against its own stratum size, so
    ``SampleFraction(0.1)`` means ten percent of that stratum.

    Parameters
    ----------
    stratum_of : Callable[[T], K]
        Function that returns the stratum label of an element.
    quotas : Mapping[K, SampleSize]
        Sample size per stratum. Strata without a quota are not sampled.
    replacement : ReplacementMode
        Whether an element may be drawn more than once.
    random_generator : RandomGenerator | None
        Random number generator. A non-deterministic one is created when omitted.
    """

    def __init__(
        self,
        stratum_of: Callable[[T], K],
        quotas: Mapping[K, SampleSize],
        *,
        replacement: ReplacementMode = ReplacementMode.SWOR,
        random_generator: RandomGenerator | None = None,
    ) -> None:
        super().__init__(random_generator)
        self._stratum_of: Callable[[T], K] = stratum_of
        self._quotas: dict[K, SampleSize] = dict(quotas)
        self._replacement: ReplacementMode = replacement
        self._index_drawer: IndexDrawer = IndexDrawer(self._random_generator)

    @override
    def sample(self, population: RandomAccessArray[T]) -> StratifiedSampleResult[T, K]:
        """Draw every stratum's quota.

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
        KeyError
            If a quota refers to a stratum that does not occur in the population.
        InsufficientPopulationError
            If a stratum cannot supply its quota.
        """
        strata: Strata[K] = Strata[K].from_population(population, self._stratum_of)
        stratum_sizes: dict[K, int] = strata.sizes
        unknown_strata: list[K] = [
            stratum for stratum in self._quotas if stratum not in stratum_sizes
        ]
        if unknown_strata:
            raise KeyError(
                f"Quotas refer to strata absent from the population: {unknown_strata!r}."
            )
        counts: dict[K, int] = {
            stratum: self._quotas[stratum].resolve(stratum_size) if stratum in self._quotas else 0
            for stratum, stratum_size in stratum_sizes.items()
        }
        return strata.draw(population, counts, self._replacement, self._index_drawer)
