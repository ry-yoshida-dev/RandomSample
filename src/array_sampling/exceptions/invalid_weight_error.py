from array_sampling.exceptions.sampling_error import SamplingError


class InvalidWeightError(SamplingError):
    """Raised when weights are negative, non-finite, or misaligned with the population."""
