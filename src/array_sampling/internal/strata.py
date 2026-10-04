from collections.abc import Callable, Hashable, Mapping
from typing import Self

from array_sampling.internal.index_drawer import IndexDrawer
from array_sampling.internal.random_access_array import RandomAccessArray
from array_sampling.replacement_mode import ReplacementMode
from array_sampling.sample_result import SampleResult
from array_sampling.stratified_sample_result import StratifiedSampleResult


class Strata[K: Hashable]:
    """Population indices grouped by stratum label.

    Parameters
    ----------
    indices_by_stratum : dict[K, list[int]]
        Population indices of each stratum, in order of first appearance.
    """

    def __init__(self, indices_by_stratum: dict[K, list[int]]) -> None:
        self._indices_by_stratum: dict[K, list[int]] = indices_by_stratum

    @classmethod
    def from_population[T](
        cls, population: RandomAccessArray[T], stratum_of: Callable[[T], K]
    ) -> Self:
        """Group a population by the label of each element.

        Parameters
        ----------
        population : RandomAccessArray[T]
            Array to group.
        stratum_of : Callable[[T], K]
            Function that returns the stratum label of an element.

        Returns
        -------
        Self
            Strata in order of first appearance.
        """
        indices_by_stratum: dict[K, list[int]] = {}
        for index, item in enumerate(population):
            indices_by_stratum.setdefault(stratum_of(item), []).append(index)
        return cls(indices_by_stratum)

    @property
    def sizes(self) -> dict[K, int]:
        """Number of population elements in each stratum."""
        return {stratum: len(indices) for stratum, indices in self._indices_by_stratum.items()}

    def draw[T](
        self,
        population: RandomAccessArray[T],
        counts: Mapping[K, int],
        replacement: ReplacementMode,
        index_drawer: IndexDrawer,
    ) -> StratifiedSampleResult[T, K]:
        """Draw a uniform sample of the given size from every stratum.

        Parameters
        ----------
        population : RandomAccessArray[T]
            Array the strata were built from.
        counts : Mapping[K, int]
            Number of elements to draw from each stratum.
        replacement : ReplacementMode
            Whether an element may be drawn more than once.
        index_drawer : IndexDrawer
            Drawer used within each stratum.

        Returns
        -------
        StratifiedSampleResult[T, K]
            Per-stratum samples in order of first appearance of each stratum.

        Raises
        ------
        InsufficientPopulationError
            If a stratum cannot supply its count.
        """
        results: dict[K, SampleResult[T]] = {}
        for stratum, stratum_indices in self._indices_by_stratum.items():
            selected_indices: tuple[int, ...] = tuple(
                stratum_indices[position]
                for position in index_drawer.draw_uniform(
                    len(stratum_indices), counts[stratum], replacement
                )
            )
            results[stratum] = SampleResult(
                items=tuple(population[index] for index in selected_indices),
                indices=selected_indices,
            )
        return StratifiedSampleResult[T, K].from_strata(results)
