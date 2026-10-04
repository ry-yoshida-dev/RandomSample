import pytest

from array_sampling import (
    InsufficientPopulationError,
    QuotaSampler,
    RandomGenerator,
    SampleCount,
    SampleFraction,
    StratifiedSampler,
)

type Record = tuple[str, int]


def plan_of(record: Record) -> str:
    return record[0]


POPULATION: list[Record] = [("free", index) for index in range(90)] + [
    ("pro", index) for index in range(10)
]


class TestStratifiedSampler:
    def test_proportional_sample_respects_strata(self) -> None:
        sampler = StratifiedSampler(
            plan_of, SampleFraction(0.2), random_generator=RandomGenerator.from_seed(0)
        )
        result = sampler.sample(POPULATION)
        assert result.allocation == {"free": 18, "pro": 2}
        assert all(record[0] == "pro" for record in result.strata["pro"].items)
        assert len(set(result.indices)) == len(result) == 20
        assert all(
            POPULATION[index] == item
            for index, item in zip(result.indices, result.items, strict=True)
        )

    def test_minimum_per_stratum_is_applied(self) -> None:
        sampler = StratifiedSampler(
            plan_of,
            SampleCount(10),
            minimum_per_stratum=3,
            random_generator=RandomGenerator.from_seed(0),
        )
        assert sampler.sample(POPULATION).allocation["pro"] >= 3


class TestQuotaSampler:
    def test_quotas_resolve_against_each_stratum(self) -> None:
        sampler = QuotaSampler(
            plan_of,
            {"free": SampleFraction(0.1), "pro": SampleCount(10)},
            random_generator=RandomGenerator.from_seed(1),
        )
        assert sampler.sample(POPULATION).allocation == {"free": 9, "pro": 10}

    def test_strata_without_quota_are_not_sampled(self) -> None:
        sampler = QuotaSampler(plan_of, {"pro": SampleCount(2)})
        assert sampler.sample(POPULATION).allocation == {"free": 0, "pro": 2}

    def test_unknown_quota_stratum_is_rejected(self) -> None:
        sampler = QuotaSampler(plan_of, {"enterprise": SampleCount(1)})
        with pytest.raises(KeyError):
            _ = sampler.sample(POPULATION)

    def test_quota_above_stratum_size_is_rejected(self) -> None:
        sampler = QuotaSampler(plan_of, {"pro": SampleCount(11)})
        with pytest.raises(InsufficientPopulationError):
            _ = sampler.sample(POPULATION)
