class SamplingError(ValueError):
    """Base class for every error raised by the sampling library.

    It derives from ``ValueError`` so that callers who only care about invalid
    input can keep catching the built-in exception.
    """
