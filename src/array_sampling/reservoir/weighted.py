import heapq
from collections.abc import Callable, Iterable

from array_sampling.exceptions import InvalidSampleSizeError
from array_sampling.internal.weight_validator import WeightValidator
from array_sampling.random_generator import RandomGenerator
from array_sampling.sample_result import SampleResult


class WeightedReservoir[T]:
    """Incremental weighted fixed-size sample of a stream, without replacement.

    Implements Efraimidis-Spirakis A-Res: each element receives the key
    ``log(u) / w`` and a min-heap keeps the ``k`` largest keys, giving
    ``O(k)`` memory and ``O(log k)`` time per element. Use it when elements
    arrive one by one; ``WeightedReservoirSampler`` wraps it for a single
    pass over an iterable.

    Parameters
    ----------
    capacity : int
        Maximum number of elements kept in the reservoir.
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
        self._capacity: int = capacity
        self._random_generator: RandomGenerator = (
            random_generator if random_generator is not None else RandomGenerator()
        )
        self._heap: list[tuple[float, int, T]] = []
        self._seen_count: int = 0

    @property
    def capacity(self) -> int:
        """Maximum number of elements kept in the reservoir."""
        return self._capacity

    @property
    def seen_count(self) -> int:
        """Number of elements observed so far, including zero-weight ones."""
        return self._seen_count

    def add(self, item: T, weight: float) -> None:
        """Observe one weighted element of the stream.

        Parameters
        ----------
        item : T
            Next element of the stream.
        weight : float
            Non-negative weight. Zero-weight elements are counted but never kept.

        Raises
        ------
        InvalidWeightError
            If ``weight`` is negative or not finite.
        """
        position: int = self._seen_count
        validated_weight: float = WeightValidator.validate_weight(weight, position)
        self._seen_count += 1
        if self._capacity == 0 or validated_weight == 0.0:
            return
        key: float = self._random_generator.weighted_key(validated_weight)
        if len(self._heap) < self._capacity:
            heapq.heappush(self._heap, (key, position, item))
        elif key > self._heap[0][0]:
            _ = heapq.heapreplace(self._heap, (key, position, item))

    def extend(self, items: Iterable[T], weight_of: Callable[[T], float]) -> None:
        """Observe every element of an iterable.

        Parameters
        ----------
        items : Iterable[T]
            Elements to observe, consumed lazily.
        weight_of : Callable[[T], float]
            Function that returns the weight of an element.
        """
        for item in items:
            self.add(item, weight_of(item))

    def result(self) -> SampleResult[T]:
        """Return the current sample ordered by stream position.

        Returns
        -------
        SampleResult[T]
            Sampled elements with their zero-based stream positions.
        """
        entries: list[tuple[float, int, T]] = sorted(self._heap, key=lambda entry: entry[1])
        return SampleResult(
            items=tuple(item for _, _, item in entries),
            indices=tuple(position for _, position, _ in entries),
        )
