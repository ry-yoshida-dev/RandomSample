from dataclasses import dataclass
from typing import override

from array_sampling.exceptions import InvalidSampleSizeError
from array_sampling.sizing.sample_size import SampleSize


@dataclass(frozen=True, slots=True)
class SampleCount(SampleSize):
    """Absolute number of elements to draw.

    Parameters
    ----------
    value : int
        Non-negative element count.

    Raises
    ------
    InvalidSampleSizeError
        If ``value`` is negative or a boolean.
    """

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or self.value < 0:
            raise InvalidSampleSizeError(
                f"Sample count must be a non-negative integer, got {self.value!r}."
            )

    @override
    def resolve(self, population_size: int) -> int:
        """Return the fixed count regardless of the population size.

        Parameters
        ----------
        population_size : int
            Number of elements in the population.

        Returns
        -------
        int
            The configured count.
        """
        return self.value
