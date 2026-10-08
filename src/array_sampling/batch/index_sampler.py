from typing import Final

import numpy as np
from numpy.typing import NDArray

from array_sampling.batch.batch_strategy import BatchStrategy
from array_sampling.exceptions import InsufficientPopulationError, InvalidSampleSizeError


class BatchIndexSampler:
    """Draw many uniform index samples without replacement at once.

    ``numpy.random.Generator.choice(..., replace=False)`` draws one sample per
    call, so a batch of samples costs one Python round trip each. The
    vectorised strategy instead draws the whole batch in ``count`` steps. Step
    ``j`` draws a rank ``r`` uniformly from the ``population - j`` indices not
    chosen yet, then walks it past the indices already chosen, in ascending
    order, so that it lands on the ``r``-th unchosen index. Every subset of
    size ``count`` is therefore equally likely, exactly as with ``choice``.
    Each step costs ``O(j)`` NumPy calls, so with ``BatchStrategy.AUTOMATIC``
    the sampler falls back to one ``choice`` call per row whenever that is
    estimated to be faster.

    Parameters
    ----------
    generator : numpy.random.Generator
        Source of randomness.
    strategy : BatchStrategy, default BatchStrategy.AUTOMATIC
        How each batch is drawn.
    """

    _VECTORISED_CALL_NANOSECONDS: Final[int] = 1300
    _VECTORISED_ELEMENT_NANOSECONDS: Final[int] = 2
    _PER_ROW_NANOSECONDS: Final[int] = 3500

    def __init__(
        self,
        generator: np.random.Generator,
        strategy: BatchStrategy = BatchStrategy.AUTOMATIC,
    ) -> None:
        self._generator: np.random.Generator = generator
        self._strategy: BatchStrategy = strategy

    def sample(self, population_sizes: NDArray[np.integer], count: int) -> NDArray[np.intp]:
        """Draw ``count`` distinct indices from ``range(population)`` for every row.

        Parameters
        ----------
        population_sizes : NDArray[np.integer]
            Population size per row, with shape ``(B,)``.
        count : int
            Number of indices per row.

        Returns
        -------
        NDArray[np.intp]
            Array with shape ``(B, count)``, each row sorted ascending.

        Raises
        ------
        TypeError
            If ``population_sizes`` does not have an integer dtype.
        ValueError
            If ``population_sizes`` is not one-dimensional, holds a negative size,
            or holds a size larger than ``numpy.intp`` can represent.
        InvalidSampleSizeError
            If ``count`` is negative or a boolean.
        InsufficientPopulationError
            If ``count`` exceeds a population size.
        """
        sizes: NDArray[np.intp] = self._validate_population_sizes(population_sizes)
        if isinstance(count, bool) or count < 0:
            raise InvalidSampleSizeError(f"count must be a non-negative integer, got {count!r}.")
        if sizes.size > 0:
            smallest_size: int = int(np.min(sizes))
            if smallest_size < count:
                raise InsufficientPopulationError(requested=count, available=smallest_size)
        match self._strategy:
            case BatchStrategy.VECTORISED:
                return self._sample_vectorised(sizes, count)
            case BatchStrategy.PER_ROW:
                return self._sample_per_row(sizes, count)
            case BatchStrategy.AUTOMATIC:
                if self._is_vectorised_faster(len(sizes), count):
                    return self._sample_vectorised(sizes, count)
                return self._sample_per_row(sizes, count)

    @staticmethod
    def _validate_population_sizes(population_sizes: NDArray[np.integer]) -> NDArray[np.intp]:
        if not np.issubdtype(population_sizes.dtype, np.integer):
            raise TypeError(
                f"population_sizes must have an integer dtype, got {population_sizes.dtype}."
            )
        if population_sizes.ndim != 1:
            raise ValueError(
                f"population_sizes must be one-dimensional, got shape {population_sizes.shape}."
            )
        if population_sizes.size > 0:
            if int(np.min(population_sizes)) < 0:
                raise ValueError("population_sizes must be non-negative.")
            largest_allowed_size: int = int(np.iinfo(np.intp).max)
            if int(np.max(population_sizes)) > largest_allowed_size:
                raise ValueError(f"population_sizes must not exceed {largest_allowed_size}.")
        return population_sizes.astype(np.intp, copy=False)

    @classmethod
    def _is_vectorised_faster(cls, row_count: int, count: int) -> bool:
        vectorised_cost: int = count**2 * (
            cls._VECTORISED_CALL_NANOSECONDS + cls._VECTORISED_ELEMENT_NANOSECONDS * row_count
        )
        per_row_cost: int = cls._PER_ROW_NANOSECONDS * row_count
        return vectorised_cost < per_row_cost

    def _sample_vectorised(self, sizes: NDArray[np.intp], count: int) -> NDArray[np.intp]:
        row_count: int = len(sizes)
        rows: NDArray[np.intp] = np.arange(row_count, dtype=np.intp)
        chosen: NDArray[np.intp] = np.empty((row_count, count), dtype=np.intp)
        for step in range(count):
            candidates: NDArray[np.intp] = self._generator.integers(
                0, sizes - step, size=row_count, dtype=np.intp
            )
            positions: NDArray[np.intp] = np.zeros(row_count, dtype=np.intp)
            for column in range(step):
                is_past_chosen: NDArray[np.bool_] = candidates >= chosen[:, column]
                candidates += is_past_chosen
                positions += is_past_chosen
            for column in range(step, 0, -1):
                chosen[:, column] = np.where(
                    positions < column, chosen[:, column - 1], chosen[:, column]
                )
            chosen[rows, positions] = candidates
        return chosen

    def _sample_per_row(self, sizes: NDArray[np.intp], count: int) -> NDArray[np.intp]:
        row_count: int = len(sizes)
        chosen: NDArray[np.intp] = np.empty((row_count, count), dtype=np.intp)
        for row in range(row_count):
            population_size: int = sizes.item(row)
            chosen[row] = np.sort(
                self._generator.choice(population_size, size=count, replace=False, shuffle=False)
            )
        return chosen
