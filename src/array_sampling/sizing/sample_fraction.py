import math
from dataclasses import dataclass
from fractions import Fraction
from typing import override

from array_sampling.exceptions import InvalidSampleSizeError
from array_sampling.sizing.sample_size import SampleSize
from array_sampling.sizing.utils.rounding_mode import RoundingMode


@dataclass(frozen=True, slots=True)
class SampleFraction(SampleSize):
    """Sample size expressed as a ratio of the population size.

    The ratio is interpreted in decimal (``0.1`` means exactly one tenth), so
    ``SampleFraction(0.1, RoundingMode.CEIL)`` on 30 elements yields 3, not 4.

    Parameters
    ----------
    value : float
        Non-negative, finite ratio. Values above 1 are valid only when sampling
        with replacement, which is checked by the sampler.
    rounding_mode : RoundingMode
        Rule used to turn the fractional count into an integer.

    Raises
    ------
    InvalidSampleSizeError
        If ``value`` is negative or not finite.
    """

    value: float
    rounding_mode: RoundingMode = RoundingMode.NEAREST

    def __post_init__(self) -> None:
        if not math.isfinite(self.value) or self.value < 0.0:
            raise InvalidSampleSizeError(
                f"Sample fraction must be a finite non-negative number, got {self.value!r}."
            )

    @override
    def resolve(self, population_size: int) -> int:
        """Scale the ratio by the population size and round it.

        Parameters
        ----------
        population_size : int
            Number of elements in the population.

        Returns
        -------
        int
            Rounded element count.
        """
        exact_count: Fraction = Fraction(repr(self.value)) * population_size
        return self.rounding_mode.apply(exact_count)
