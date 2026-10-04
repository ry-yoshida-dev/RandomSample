import pytest

from array_sampling import (
    AllocationStrategy,
    InsufficientPopulationError,
    InvalidSampleSizeError,
    ReplacementMode,
    StratumAllocator,
)


class TestStratumAllocator:
    def test_proportional_allocation_sums_to_total(self) -> None:
        allocation = StratumAllocator(AllocationStrategy.PROPORTIONAL).allocate(
            {"a": 1, "b": 1, "c": 1}, 2, ReplacementMode.SWOR
        )
        assert sum(allocation.values()) == 2
        assert allocation == {"a": 1, "b": 1, "c": 0}

    def test_proportional_allocation_follows_sizes(self) -> None:
        allocation = StratumAllocator(AllocationStrategy.PROPORTIONAL).allocate(
            {"large": 800, "medium": 150, "small": 50}, 100, ReplacementMode.SWOR
        )
        assert allocation == {"large": 80, "medium": 15, "small": 5}

    def test_equal_allocation_redistributes_capped_overflow(self) -> None:
        allocation = StratumAllocator(AllocationStrategy.EQUAL).allocate(
            {"tiny": 2, "big": 100}, 30, ReplacementMode.SWOR
        )
        assert allocation == {"tiny": 2, "big": 28}

    def test_minimum_per_stratum_protects_small_strata(self) -> None:
        allocation = StratumAllocator(
            AllocationStrategy.PROPORTIONAL, minimum_per_stratum=3
        ).allocate({"large": 990, "small": 10}, 20, ReplacementMode.SWOR)
        assert allocation["small"] >= 3
        assert sum(allocation.values()) == 20

    def test_total_below_minimums_is_rejected(self) -> None:
        with pytest.raises(InvalidSampleSizeError):
            _ = StratumAllocator(AllocationStrategy.EQUAL, minimum_per_stratum=5).allocate(
                {"a": 10, "b": 10}, 6, ReplacementMode.SWOR
            )

    def test_total_above_population_is_rejected(self) -> None:
        with pytest.raises(InsufficientPopulationError):
            _ = StratumAllocator(AllocationStrategy.EQUAL).allocate(
                {"a": 1, "b": 1}, 3, ReplacementMode.SWOR
            )

    def test_with_replacement_is_not_capped(self) -> None:
        allocation = StratumAllocator(AllocationStrategy.EQUAL).allocate(
            {"a": 1, "b": 1}, 10, ReplacementMode.SWR
        )
        assert allocation == {"a": 5, "b": 5}
