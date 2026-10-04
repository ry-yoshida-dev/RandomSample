import pytest

from array_sampling import (
    ArraySampler,
    BernoulliSampler,
    QuotaSampler,
    RandomGenerator,
    ReservoirSampler,
    SampleCount,
    Sampler,
    SampleResult,
    StratifiedSampler,
    WeightedReservoirSampler,
)


def parity_of(value: int) -> int:
    return value % 2


def weight_of(value: int) -> float:
    return float(value + 1)


def sampler_id(sampler: object) -> str:
    return type(sampler).__name__


def build_samplers() -> list[Sampler[int]]:
    random_generator: RandomGenerator = RandomGenerator.from_seed(0)
    return [
        ArraySampler(SampleCount(10), random_generator=random_generator),
        ArraySampler(SampleCount(10), weight_of=weight_of, random_generator=random_generator),
        BernoulliSampler(0.1, random_generator),
        ReservoirSampler(10, random_generator),
        WeightedReservoirSampler(10, weight_of, random_generator),
        StratifiedSampler(parity_of, SampleCount(10), random_generator=random_generator),
        QuotaSampler(
            parity_of,
            {0: SampleCount(5), 1: SampleCount(5)},
            random_generator=random_generator,
        ),
    ]


class TestSampler:
    @pytest.mark.parametrize("sampler", build_samplers(), ids=sampler_id)
    def test_every_sampler_returns_aligned_sample_result(self, sampler: Sampler[int]) -> None:
        population: list[int] = list(range(100, 200))
        result: SampleResult[int] = sampler.sample(population)
        assert len(result) > 0
        assert all(
            population[index] == item
            for index, item in zip(result.indices, result.items, strict=True)
        )
