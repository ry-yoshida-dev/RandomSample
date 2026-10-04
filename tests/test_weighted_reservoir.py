from collections import Counter

import pytest

from array_sampling import (
    InvalidSampleSizeError,
    InvalidWeightError,
    RandomGenerator,
    WeightedReservoir,
    WeightedReservoirSampler,
)


class TestWeightedReservoir:
    def test_zero_weight_elements_are_never_kept(self) -> None:
        reservoir: WeightedReservoir[str] = WeightedReservoir(3, RandomGenerator.from_seed(0))
        reservoir.extend(["a", "b", "c", "d"], lambda item: 0.0 if item in {"a", "c"} else 1.0)
        assert reservoir.result().items == ("b", "d")
        assert reservoir.seen_count == 4

    def test_invalid_weight_is_rejected(self) -> None:
        reservoir: WeightedReservoir[str] = WeightedReservoir(1)
        with pytest.raises(InvalidWeightError):
            reservoir.add("a", -1.0)


class TestWeightedReservoirSampler:
    def test_heavier_elements_are_preferred(self) -> None:
        weights: dict[str, float] = {"light": 1.0, "heavy": 4.0}
        sampler = WeightedReservoirSampler(1, weights.__getitem__, RandomGenerator.from_seed(2))
        selection_counts: Counter[str] = Counter()
        for _ in range(10_000):
            selection_counts.update(sampler.sample(["light", "heavy"]).items)
        assert selection_counts["heavy"] / 10_000 == pytest.approx(0.8, abs=0.02)

    def test_negative_capacity_is_rejected(self) -> None:
        weights: dict[str, float] = {}
        with pytest.raises(InvalidSampleSizeError):
            _ = WeightedReservoirSampler(-1, weights.__getitem__)
