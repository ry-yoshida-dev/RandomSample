import math

import numpy as np
import pytest

from array_sampling import InsufficientPopulationError, InvalidSampleSizeError
from array_sampling.batch import BatchIndexSampler

VECTORISED_ONLY: int = 1_000_000
PER_ROW_ONLY: int = 0


class TestBatchIndexSampler:
    @pytest.mark.parametrize("max_vectorised_count", [VECTORISED_ONLY, PER_ROW_ONLY])
    def test_gives_distinct_sorted_indices_within_each_population(
        self, max_vectorised_count: int
    ) -> None:
        generator = np.random.default_rng(0)
        populations = generator.integers(5, 40, 2000).astype(np.intp)
        samples = BatchIndexSampler(generator, max_vectorised_count).sample(populations, 5)
        assert samples.shape == (2000, 5)
        assert bool(np.all(np.diff(samples, axis=1) > 0))
        assert bool(np.all(samples[:, 0] >= 0))
        assert bool(np.all(samples[:, -1] < populations))

    @pytest.mark.parametrize("max_vectorised_count", [VECTORISED_ONLY, PER_ROW_ONLY])
    def test_is_uniform_over_subsets(self, max_vectorised_count: int) -> None:
        draws = 120_000
        samples = BatchIndexSampler(np.random.default_rng(1), max_vectorised_count).sample(
            np.full(draws, 6, dtype=np.intp), 3
        )
        _, counts = np.unique(samples, axis=0, return_counts=True)
        subset_count = math.comb(6, 3)
        assert counts.shape[0] == subset_count
        expected = draws / subset_count
        chi_square = float(np.sum((counts - expected) ** 2 / expected))
        assert chi_square < 45.0

    def test_vectorised_strategy_is_uniform_for_many_steps(self) -> None:
        draws = 40_000
        population = 50
        count = 20
        samples = BatchIndexSampler(np.random.default_rng(3), VECTORISED_ONLY).sample(
            np.full(draws, population, dtype=np.intp), count
        )
        assert bool(np.all(np.diff(samples, axis=1) > 0))
        frequencies = np.bincount(samples.reshape(-1), minlength=population)
        expected = draws * count / population
        assert bool(np.all(np.abs(frequencies - expected) < 0.05 * expected))

    @pytest.mark.parametrize("max_vectorised_count", [VECTORISED_ONLY, PER_ROW_ONLY])
    def test_can_take_a_whole_population(self, max_vectorised_count: int) -> None:
        samples = BatchIndexSampler(np.random.default_rng(2), max_vectorised_count).sample(
            np.full(10, 4, dtype=np.intp), 4
        )
        assert np.array_equal(samples, np.tile(np.arange(4), (10, 1)))

    def test_handles_an_empty_batch(self) -> None:
        samples = BatchIndexSampler(np.random.default_rng(0)).sample(np.array([], dtype=np.intp), 3)
        assert samples.shape == (0, 3)

    def test_rejects_an_oversized_sample(self) -> None:
        with pytest.raises(InsufficientPopulationError):
            _ = BatchIndexSampler(np.random.default_rng(0)).sample(
                np.array([3, 5], dtype=np.intp), 4
            )

    def test_rejects_a_negative_count(self) -> None:
        with pytest.raises(InvalidSampleSizeError):
            _ = BatchIndexSampler(np.random.default_rng(0)).sample(np.array([3], dtype=np.intp), -1)

    def test_rejects_a_negative_threshold(self) -> None:
        with pytest.raises(InvalidSampleSizeError):
            _ = BatchIndexSampler(np.random.default_rng(0), -1)

    def test_rejects_non_integer_population_sizes(self) -> None:
        with pytest.raises(TypeError):
            _ = BatchIndexSampler(np.random.default_rng(0)).sample(np.array([3.9]), 3)

    def test_rejects_multidimensional_population_sizes(self) -> None:
        with pytest.raises(ValueError, match="one-dimensional"):
            _ = BatchIndexSampler(np.random.default_rng(0)).sample(
                np.array([[5, 6], [7, 8]], dtype=np.intp), 2
            )

    def test_rejects_population_sizes_beyond_intp(self) -> None:
        with pytest.raises(ValueError, match="must not exceed"):
            _ = BatchIndexSampler(np.random.default_rng(0)).sample(
                np.array([2**63 + 5], dtype=np.uint64), 2
            )

    def test_rejects_negative_population_sizes(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            _ = BatchIndexSampler(np.random.default_rng(0)).sample(
                np.array([-5, 3], dtype=np.intp), 0
            )
