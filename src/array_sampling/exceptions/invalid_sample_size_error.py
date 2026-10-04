from array_sampling.exceptions.sampling_error import SamplingError


class InvalidSampleSizeError(SamplingError):
    """Raised when a sample size, fraction, capacity, or probability is invalid."""
