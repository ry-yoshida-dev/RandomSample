from collections.abc import Hashable, Sequence

from array_sampling.exceptions.sampling_error import SamplingError


class UnknownStratumError(SamplingError):
    """Raised when a quota refers to a stratum that does not occur in the population.

    Parameters
    ----------
    strata : Sequence[Hashable]
        Stratum labels that are absent from the population.
    """

    def __init__(self, strata: Sequence[Hashable]) -> None:
        super().__init__(f"Quotas refer to strata absent from the population: {list(strata)!r}.")
        self.strata: tuple[Hashable, ...] = tuple(strata)
