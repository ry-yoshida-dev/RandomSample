from collections.abc import Iterator
from itertools import count

import pytest

from array_sampling import BernoulliSampler, InvalidSampleSizeError, RandomGenerator


class TestBernoulliSampler:
    def test_rate_is_respected_on_large_input(self) -> None:
        sampler: BernoulliSampler[int] = BernoulliSampler(0.01, RandomGenerator.from_seed(0))
        result = sampler.sample(range(1_000_000))
        assert len(result) / 1_000_000 == pytest.approx(0.01, rel=0.05)
        assert result.items == result.indices
        assert list(result.indices) == sorted(set(result.indices))

    def test_indices_are_input_positions(self) -> None:
        sampler: BernoulliSampler[str] = BernoulliSampler(0.5, RandomGenerator.from_seed(2))
        population: list[str] = [f"item-{index}" for index in range(100)]
        result = sampler.sample(population)
        assert all(
            population[index] == item
            for index, item in zip(result.indices, result.items, strict=True)
        )

    def test_boundary_probabilities(self) -> None:
        never: BernoulliSampler[int] = BernoulliSampler(0.0)
        always: BernoulliSampler[int] = BernoulliSampler(1.0)
        assert len(never.sample(range(10))) == 0
        assert always.sample(range(10)).items == tuple(range(10))

    def test_stream_is_lazy(self) -> None:
        sampler: BernoulliSampler[int] = BernoulliSampler(0.5, RandomGenerator.from_seed(1))
        selected: Iterator[int] = sampler.stream(count())
        assert next(selected) < next(selected)

    @pytest.mark.parametrize("probability", [-0.1, 1.1, float("nan")])
    def test_invalid_probability_is_rejected(self, probability: float) -> None:
        with pytest.raises(InvalidSampleSizeError):
            _ = BernoulliSampler[int](probability)
