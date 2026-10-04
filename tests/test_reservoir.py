from collections import Counter

import pytest

from array_sampling import (
    InvalidSampleSizeError,
    RandomGenerator,
    ReservoirSampler,
    UniformReservoir,
)


class TestUniformReservoir:
    def test_short_stream_is_kept_entirely(self) -> None:
        reservoir: UniformReservoir[int] = UniformReservoir(10, RandomGenerator.from_seed(0))
        reservoir.extend(range(4))
        assert reservoir.result().items == (0, 1, 2, 3)

    def test_long_stream_keeps_capacity_distinct_positions(self) -> None:
        reservoir: UniformReservoir[int] = UniformReservoir(100, RandomGenerator.from_seed(0))
        reservoir.extend(range(1_000_000))
        result = reservoir.result()
        assert len(result) == 100
        assert result.items == result.indices
        assert list(result.indices) == sorted(set(result.indices))
        assert reservoir.seen_count == 1_000_000

    def test_zero_capacity_only_counts(self) -> None:
        reservoir: UniformReservoir[int] = UniformReservoir(0)
        reservoir.extend(range(10))
        assert len(reservoir.result()) == 0
        assert reservoir.seen_count == 10

    def test_negative_capacity_is_rejected(self) -> None:
        with pytest.raises(InvalidSampleSizeError):
            _ = UniformReservoir[int](-1)


class TestReservoirSampler:
    def test_inclusion_is_uniform(self) -> None:
        sampler: ReservoirSampler[int] = ReservoirSampler(5, RandomGenerator.from_seed(1))
        inclusion_counts: Counter[int] = Counter()
        trial_count: int = 4_000
        for _ in range(trial_count):
            inclusion_counts.update(sampler.sample(range(50)).items)
        for element in range(50):
            assert inclusion_counts[element] / trial_count == pytest.approx(0.1, abs=0.025)

    def test_each_sample_starts_from_an_empty_reservoir(self) -> None:
        sampler: ReservoirSampler[int] = ReservoirSampler(10, RandomGenerator.from_seed(0))
        _ = sampler.sample(range(1_000))
        assert sampler.sample(range(3)).items == (0, 1, 2)

    def test_negative_capacity_is_rejected(self) -> None:
        with pytest.raises(InvalidSampleSizeError):
            _ = ReservoirSampler[int](-1)
