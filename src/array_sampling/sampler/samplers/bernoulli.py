import math
from collections.abc import Iterable, Iterator
from itertools import islice
from typing import override

from array_sampling.exceptions import InvalidSampleSizeError
from array_sampling.random_generator import RandomGenerator
from array_sampling.sample_result import SampleResult
from array_sampling.sampler.sampler import Sampler


class BernoulliSampler[T](Sampler[T]):
    """Keep each element independently with a fixed probability.

    Suitable when a sampling *rate* rather than a fixed size is required.
    Gaps between selected elements are drawn from a geometric distribution
    and skipped with ``itertools.islice``, so the cost per skipped element is
    close to that of plain iteration. ``sample`` collects the selection,
    while ``stream`` yields it lazily with ``O(1)`` memory and also works on
    infinite iterables.

    Parameters
    ----------
    probability : float
        Inclusion probability in ``[0, 1]``.
    random_generator : RandomGenerator | None
        Random number generator. A non-deterministic one is created when omitted.

    Raises
    ------
    InvalidSampleSizeError
        If ``probability`` lies outside ``[0, 1]``.
    """

    def __init__(self, probability: float, random_generator: RandomGenerator | None = None) -> None:
        if not 0.0 <= probability <= 1.0:
            raise InvalidSampleSizeError(f"Probability must lie in [0, 1], got {probability!r}.")
        super().__init__(random_generator)
        self._probability: float = probability

    @property
    def probability(self) -> float:
        """Inclusion probability of every element."""
        return self._probability

    @override
    def sample(self, population: Iterable[T]) -> SampleResult[T]:
        """Collect the selected elements of a finite iterable.

        Parameters
        ----------
        population : Iterable[T]
            Elements to sample from.

        Returns
        -------
        SampleResult[T]
            Selected elements with their zero-based positions, in input order.
        """
        selected: list[tuple[int, T]] = list(self._select(population))
        return SampleResult(
            items=tuple(item for _, item in selected),
            indices=tuple(position for position, _ in selected),
        )

    def stream(self, population: Iterable[T]) -> Iterator[T]:
        """Lazily yield the selected elements.

        Parameters
        ----------
        population : Iterable[T]
            Elements to sample from, possibly infinite.

        Yields
        ------
        T
            Selected elements in input order.
        """
        for _, item in self._select(population):
            yield item

    def _select(self, population: Iterable[T]) -> Iterator[tuple[int, T]]:
        if self._probability == 0.0:
            return
        positioned_items: Iterator[tuple[int, T]] = enumerate(population)
        if self._probability == 1.0:
            yield from positioned_items
            return
        log_rejection_probability: float = math.log1p(-self._probability)
        while True:
            skip: int = math.floor(
                math.log(self._random_generator.open_unit_interval()) / log_rejection_probability
            )
            selected: list[tuple[int, T]] = list(islice(positioned_items, skip, skip + 1))
            if not selected:
                return
            yield selected[0]
