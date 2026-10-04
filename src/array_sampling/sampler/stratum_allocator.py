from collections.abc import Hashable, Mapping
from fractions import Fraction

from array_sampling.exceptions import InsufficientPopulationError, InvalidSampleSizeError
from array_sampling.replacement_mode import ReplacementMode
from array_sampling.sampler.allocation_strategy import AllocationStrategy


class StratumAllocator:
    """Split a total sample size into per-stratum counts.

    Fractional shares are rounded with the largest remainder (Hamilton)
    method, so the counts always add up to the requested total. When sampling
    without replacement, strata are capped at their size and the overflow is
    redistributed among the remaining strata. Empty strata always receive
    zero.

    Parameters
    ----------
    strategy : AllocationStrategy
        Rule used to compute each stratum's share.
    minimum_per_stratum : int
        Count guaranteed to every stratum before the remainder is shared. It
        is capped at the stratum size when sampling without replacement.

    Raises
    ------
    InvalidSampleSizeError
        If ``minimum_per_stratum`` is negative.
    """

    def __init__(self, strategy: AllocationStrategy, minimum_per_stratum: int = 0) -> None:
        if minimum_per_stratum < 0:
            raise InvalidSampleSizeError(
                f"minimum_per_stratum must be non-negative, got {minimum_per_stratum}."
            )
        self._strategy: AllocationStrategy = strategy
        self._minimum_per_stratum: int = minimum_per_stratum

    def allocate[K: Hashable](
        self,
        stratum_sizes: Mapping[K, int],
        total: int,
        replacement: ReplacementMode,
    ) -> dict[K, int]:
        """Compute the number of elements to draw from each stratum.

        Parameters
        ----------
        stratum_sizes : Mapping[K, int]
            Non-negative number of population elements in each stratum.
            Iteration order is used to break ties deterministically.
        total : int
            Total number of elements to draw.
        replacement : ReplacementMode
            Whether strata are capped at their size.

        Returns
        -------
        dict[K, int]
            Per-stratum counts that sum to ``total``.

        Raises
        ------
        InvalidSampleSizeError
            If ``total`` or a stratum size is negative, or ``total`` is smaller
            than the guaranteed minimums.
        InsufficientPopulationError
            If ``total`` exceeds the population size without replacement, or
            every stratum is empty.
        """
        if total < 0:
            raise InvalidSampleSizeError(f"Total sample size must be non-negative, got {total}.")
        negative_strata: list[K] = [stratum for stratum, size in stratum_sizes.items() if size < 0]
        if negative_strata:
            raise InvalidSampleSizeError(
                f"Stratum sizes must be non-negative, got negative sizes for {negative_strata!r}."
            )
        capacities: dict[K, int] = self._capacities(stratum_sizes, total, replacement)
        allocation: dict[K, int] = {
            stratum: min(self._minimum_per_stratum, capacity)
            for stratum, capacity in capacities.items()
        }
        remaining: int = total - sum(allocation.values())
        if remaining < 0:
            raise InvalidSampleSizeError(
                f"Total sample size {total} is smaller than the guaranteed minimum "
                + f"{sum(allocation.values())} across {len(allocation)} strata."
            )
        open_strata: list[K] = [
            stratum for stratum in allocation if allocation[stratum] < capacities[stratum]
        ]
        while remaining > 0 and open_strata:
            quotas: dict[K, int] = self._largest_remainder(
                self._shares(open_strata, stratum_sizes), remaining
            )
            for stratum in open_strata:
                granted: int = min(quotas[stratum], capacities[stratum] - allocation[stratum])
                allocation[stratum] += granted
                remaining -= granted
            open_strata = [
                stratum for stratum in open_strata if allocation[stratum] < capacities[stratum]
            ]
        return allocation

    @staticmethod
    def _capacities[K: Hashable](
        stratum_sizes: Mapping[K, int], total: int, replacement: ReplacementMode
    ) -> dict[K, int]:
        match replacement:
            case ReplacementMode.SWR:
                if total > 0 and not any(stratum_sizes.values()):
                    raise InsufficientPopulationError(requested=total, available=0)
                return {
                    stratum: total if size > 0 else 0 for stratum, size in stratum_sizes.items()
                }
            case ReplacementMode.SWOR:
                population_size: int = sum(stratum_sizes.values())
                if total > population_size:
                    raise InsufficientPopulationError(requested=total, available=population_size)
                return dict(stratum_sizes)

    def _shares[K: Hashable](
        self, strata: list[K], stratum_sizes: Mapping[K, int]
    ) -> dict[K, Fraction]:
        match self._strategy:
            case AllocationStrategy.PROPORTIONAL:
                combined_size: int = sum(stratum_sizes[stratum] for stratum in strata)
                return {
                    stratum: Fraction(stratum_sizes[stratum], combined_size) for stratum in strata
                }
            case AllocationStrategy.EQUAL:
                return dict.fromkeys(strata, Fraction(1, len(strata)))

    @staticmethod
    def _largest_remainder[K: Hashable](shares: dict[K, Fraction], total: int) -> dict[K, int]:
        exact_quotas: dict[K, Fraction] = {
            stratum: share * total for stratum, share in shares.items()
        }
        quotas: dict[K, int] = {
            stratum: int(exact_quota) for stratum, exact_quota in exact_quotas.items()
        }
        leftover: int = total - sum(quotas.values())
        ranked_strata: list[K] = sorted(
            exact_quotas,
            key=lambda stratum: exact_quotas[stratum] - quotas[stratum],
            reverse=True,
        )
        for stratum in ranked_strata[:leftover]:
            quotas[stratum] += 1
        return quotas
