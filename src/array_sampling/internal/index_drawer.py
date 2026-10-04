import heapq
from collections.abc import Sequence

from array_sampling.exceptions import InsufficientPopulationError
from array_sampling.random_generator import RandomGenerator
from array_sampling.replacement_mode import ReplacementMode


class IndexDrawer:
    """Draw population indices uniformly or by weight.

    Parameters
    ----------
    random_generator : RandomGenerator
        Source of randomness.
    """

    def __init__(self, random_generator: RandomGenerator) -> None:
        self._random_generator: RandomGenerator = random_generator

    def draw_uniform(
        self, population_size: int, sample_count: int, replacement: ReplacementMode
    ) -> tuple[int, ...]:
        """Draw indices with equal probability.

        Parameters
        ----------
        population_size : int
            Number of elements in the population.
        sample_count : int
            Number of indices to draw.
        replacement : ReplacementMode
            Whether an index may be drawn more than once.

        Returns
        -------
        tuple[int, ...]
            Selected indices in draw order.

        Raises
        ------
        InsufficientPopulationError
            If the population cannot supply the requested sample.
        """
        match replacement:
            case ReplacementMode.SWR:
                if sample_count > 0 and population_size == 0:
                    raise InsufficientPopulationError(requested=sample_count, available=0)
                return tuple(
                    self._random_generator.random_index(population_size)
                    for _ in range(sample_count)
                )
            case ReplacementMode.SWOR:
                if sample_count > population_size:
                    raise InsufficientPopulationError(
                        requested=sample_count, available=population_size
                    )
                return tuple(
                    self._random_generator.backend.sample(range(population_size), sample_count)
                )

    def draw_weighted(
        self, weights: Sequence[float], sample_count: int, replacement: ReplacementMode
    ) -> tuple[int, ...]:
        """Draw indices with probability proportional to their weight.

        Parameters
        ----------
        weights : Sequence[float]
            Validated non-negative weights, one per index. Zero-weight indices
            are never selected.
        sample_count : int
            Number of indices to draw.
        replacement : ReplacementMode
            Whether an index may be drawn more than once.

        Returns
        -------
        tuple[int, ...]
            Selected indices in draw order.

        Raises
        ------
        InsufficientPopulationError
            If too few indices have a positive weight.
        """
        eligible_indices: list[int] = [
            index for index, weight in enumerate(weights) if weight > 0.0
        ]
        if sample_count == 0:
            return ()
        match replacement:
            case ReplacementMode.SWR:
                if not eligible_indices:
                    raise InsufficientPopulationError(requested=sample_count, available=0)
                return tuple(
                    self._random_generator.backend.choices(
                        range(len(weights)), weights=weights, k=sample_count
                    )
                )
            case ReplacementMode.SWOR:
                if sample_count > len(eligible_indices):
                    raise InsufficientPopulationError(
                        requested=sample_count, available=len(eligible_indices)
                    )
                keyed_indices: list[tuple[float, int]] = [
                    (self._random_generator.weighted_key(weights[index]), index)
                    for index in eligible_indices
                ]
                return tuple(index for _, index in heapq.nlargest(sample_count, keyed_indices))
