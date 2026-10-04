from array_sampling.exceptions.sampling_error import SamplingError


class InsufficientPopulationError(SamplingError):
    """Raised when the population cannot supply the requested number of elements.

    Parameters
    ----------
    requested : int
        Number of elements the caller asked for.
    available : int
        Number of eligible elements actually available.
    """

    def __init__(self, requested: int, available: int) -> None:
        super().__init__(
            f"Cannot draw {requested} elements: only {available} eligible elements are available."
        )
        self.requested: int = requested
        self.available: int = available
