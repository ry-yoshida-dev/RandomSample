import math
from collections.abc import Sequence

from array_sampling.exceptions import InvalidWeightError


class WeightValidator:
    """Fail-fast validation of sampling weights."""

    @staticmethod
    def validate_weight(weight: float, position: int) -> float:
        """Validate a single weight.

        Parameters
        ----------
        weight : float
            Weight to validate.
        position : int
            Position of the weighted element, used in the error message.

        Returns
        -------
        float
            The weight as a ``float``.

        Raises
        ------
        InvalidWeightError
            If the weight is negative or not finite.
        """
        if not math.isfinite(weight) or weight < 0.0:
            raise InvalidWeightError(
                f"Weight at position {position} must be finite and non-negative, got {weight!r}."
            )
        return float(weight)

    @staticmethod
    def validate_weights(weights: Sequence[float]) -> list[float]:
        """Validate a weight vector aligned with a population.

        Parameters
        ----------
        weights : Sequence[float]
            One weight per population element.

        Returns
        -------
        list[float]
            Validated weights.

        Raises
        ------
        InvalidWeightError
            If any weight is invalid or the total overflows.
        """
        validated_weights: list[float] = [
            WeightValidator.validate_weight(weight, position)
            for position, weight in enumerate(weights)
        ]
        if not math.isfinite(math.fsum(validated_weights)):
            raise InvalidWeightError("The sum of weights must be finite.")
        return validated_weights
