from collections import Counter

import pytest

from array_sampling import (
    ArraySampler,
    InsufficientPopulationError,
    InvalidWeightError,
    RandomGenerator,
    ReplacementMode,
    SampleCount,
    SampleFraction,
)


class TestArraySampler:
    def test_without_replacement_returns_distinct_aligned_items(self) -> None:
        population: list[str] = [f"item-{index}" for index in range(50)]
        sampler: ArraySampler[str] = ArraySampler(
            SampleCount(20), random_generator=RandomGenerator.from_seed(1)
        )
        result = sampler.sample(population)
        assert len(set(result.indices)) == 20
        assert all(
            population[index] == item
            for index, item in zip(result.indices, result.items, strict=True)
        )

    def test_same_seed_is_reproducible(self) -> None:
        first: ArraySampler[int] = ArraySampler(
            SampleCount(10), random_generator=RandomGenerator.from_seed(5)
        )
        second: ArraySampler[int] = ArraySampler(
            SampleCount(10), random_generator=RandomGenerator.from_seed(5)
        )
        assert first.sample(range(1000)) == second.sample(range(1000))

    def test_huge_lazy_population_is_not_materialized(self) -> None:
        sampler: ArraySampler[int] = ArraySampler(
            SampleCount(5), random_generator=RandomGenerator.from_seed(0)
        )
        assert len(sampler.sample(range(10**15))) == 5

    def test_with_replacement_allows_fraction_above_one(self) -> None:
        sampler: ArraySampler[int] = ArraySampler(
            SampleFraction(2.0),
            replacement=ReplacementMode.SWR,
            random_generator=RandomGenerator.from_seed(2),
        )
        assert len(sampler.sample([1, 2, 3])) == 6

    def test_oversampling_without_replacement_fails(self) -> None:
        sampler: ArraySampler[int] = ArraySampler(SampleCount(4))
        with pytest.raises(InsufficientPopulationError) as error:
            _ = sampler.sample([1, 2, 3])
        assert (error.value.requested, error.value.available) == (4, 3)

    def test_weighted_without_replacement_skips_zero_weights(self) -> None:
        weights: dict[str, float] = {"a": 0.0, "b": 1.0, "c": 0.0, "d": 2.0}
        sampler = ArraySampler(
            SampleCount(2),
            weight_of=weights.__getitem__,
            random_generator=RandomGenerator.from_seed(3),
        )
        assert sorted(sampler.sample(["a", "b", "c", "d"]).items) == ["b", "d"]

    def test_weighted_without_replacement_fails_when_positive_weights_are_scarce(self) -> None:
        weights: dict[str, float] = {"a": 1.0, "b": 0.0}
        sampler = ArraySampler(SampleCount(2), weight_of=weights.__getitem__)
        with pytest.raises(InsufficientPopulationError):
            _ = sampler.sample(["a", "b"])

    def test_weighted_with_replacement_follows_weights(self) -> None:
        weights: dict[str, float] = {"a": 1.0, "b": 3.0}
        sampler = ArraySampler(
            SampleCount(20_000),
            replacement=ReplacementMode.SWR,
            weight_of=weights.__getitem__,
            random_generator=RandomGenerator.from_seed(4),
        )
        result = sampler.sample(["a", "b"])
        frequency: float = Counter(result.items)["b"] / len(result)
        assert frequency == pytest.approx(0.75, abs=0.02)

    def test_weighted_without_replacement_first_draw_follows_weights(self) -> None:
        weights: dict[str, float] = {"a": 1.0, "b": 3.0}
        sampler = ArraySampler(
            SampleCount(1),
            weight_of=weights.__getitem__,
            random_generator=RandomGenerator.from_seed(6),
        )
        first_draws: Counter[str] = Counter(
            sampler.sample(["a", "b"]).items[0] for _ in range(20_000)
        )
        assert first_draws["b"] / 20_000 == pytest.approx(0.75, abs=0.02)

    @pytest.mark.parametrize("invalid_weight", [-1.0, float("nan"), float("inf")])
    def test_invalid_weights_are_rejected(self, invalid_weight: float) -> None:
        weights: dict[str, float] = {"a": 1.0, "b": invalid_weight}
        sampler = ArraySampler(SampleCount(1), weight_of=weights.__getitem__)
        with pytest.raises(InvalidWeightError):
            _ = sampler.sample(["a", "b"])

    def test_zero_sample_from_empty_population(self) -> None:
        sampler: ArraySampler[int] = ArraySampler(SampleCount(0))
        assert len(sampler.sample(range(0))) == 0
