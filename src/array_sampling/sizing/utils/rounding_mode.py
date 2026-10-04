import math
from enum import Enum
from fractions import Fraction


class RoundingMode(Enum):
    """Rule that converts a fractional sample size into an element count."""

    FLOOR = "floor"
    CEIL = "ceil"
    NEAREST = "nearest"

    def apply(self, value: Fraction) -> int:
        """Round an exact rational value to an integer.

        Parameters
        ----------
        value : Fraction
            Exact value to round.

        Returns
        -------
        int
            Rounded value. ``NEAREST`` rounds halves up.
        """
        match self:
            case RoundingMode.FLOOR:
                return math.floor(value)
            case RoundingMode.CEIL:
                return math.ceil(value)
            case RoundingMode.NEAREST:
                return math.floor(value + Fraction(1, 2))
