from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from typing import Self

from array_sampling.sample_result import SampleResult


@dataclass(frozen=True, slots=True)
class StratifiedSampleResult[T, K: Hashable](SampleResult[T]):
    """Sample result that also keeps the per-stratum breakdown.

    ``items`` and ``indices`` hold every selected element, concatenated
    stratum by stratum, so the result can be used wherever a
    ``SampleResult`` is expected.

    Parameters
    ----------
    items : tuple[T, ...]
        All selected elements, concatenated stratum by stratum.
    indices : tuple[int, ...]
        Population indices aligned with ``items``.
    strata : Mapping[K, SampleResult[T]]
        Sample drawn from each stratum, keyed by stratum label. Strata that
        received no allocation are present with an empty result.
    """

    strata: Mapping[K, SampleResult[T]]

    @classmethod
    def from_strata(cls, strata: Mapping[K, SampleResult[T]]) -> Self:
        """Build a result by concatenating per-stratum samples.

        Parameters
        ----------
        strata : Mapping[K, SampleResult[T]]
            Sample drawn from each stratum.

        Returns
        -------
        Self
            Result whose flat view follows the iteration order of ``strata``.
        """
        return cls(
            items=tuple(item for result in strata.values() for item in result.items),
            indices=tuple(index for result in strata.values() for index in result.indices),
            strata=strata,
        )

    @property
    def allocation(self) -> dict[K, int]:
        """Number of elements drawn from each stratum."""
        return {stratum: len(result) for stratum, result in self.strata.items()}
