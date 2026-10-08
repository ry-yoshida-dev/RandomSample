import math

import numpy as np
import pytest

from array_sampling import InsufficientPopulationError, InvalidSampleSizeError
from array_sampling.batch import BatchIndexSampler, BatchStrategy

FIXED_STRATEGIES: list[BatchStrategy] = [BatchStrategy.VECTORISED, BatchStrategy.PER_ROW]


class TestBatchIndexSampler:
    @pytest.mark.parametrize("strategy", list(BatchStrategy))
    def test_gives_distinct_sorted_indices_within_each_population(
        self, strategy: BatchStrategy
    ) -> None:
        generator = np.random.default_rng(0)
        populations = generator.integers(5, 40, 2000).astype(np.intp)
        samples = BatchIndexSampler(generator, strategy).sample(populations, 5)
        assert samples.shape == (2000, 5)
        assert bool(np.all(np.diff(samples, axis=1) > 0))
        assert bool(np.all(samples[:, 0] >= 0))
        assert bool(np.all(samples[:, -1] < populations))

    @pytest.mark.parametrize("strategy", FIXED_STRATEGIES)
    def test_is_uniform_over_subsets(self, strategy: BatchStrategy) -> None:
        draws = 120_000
        samples = BatchIndexSampler(np.random.default_rng(1), strategy).sample(
            np.full(draws, 6, dtype=np.intp), 3
        )
        _, counts = np.unique(samples, axis=0, return_counts=True)
        subset_count = math.comb(6, 3)
        assert counts.shape[0] == subset_count
        expected = draws / subset_count
        chi_square = float(np.sum((counts - expected) ** 2 / expected))
        assert chi_square < 45.0

    @pytest.mark.parametrize("strategy", FIXED_STRATEGIES)
    def test_is_uniform_within_each_row_population(self, strategy: BatchStrategy) -> None:
        draws_per_size = 30_000
        count = 2
        populations = np.tile(np.array([3, 10], dtype=np.intp), draws_per_size)
        samples = BatchIndexSampler(np.random.default_rng(4), strategy).sample(populations, count)
        for offset, population in enumerate((3, 10)):
            frequencies = np.bincount(samples[offset::2].reshape(-1), minlength=population)
            assert frequencies.shape[0] == population
            expected = draws_per_size * count / population
            assert bool(np.all(np.abs(frequencies - expected) < 0.05 * expected))

    def test_vectorised_strategy_is_uniform_for_many_steps(self) -> None:
        draws = 40_000
        population = 50
        count = 20
        samples = BatchIndexSampler(np.random.default_rng(3), BatchStrategy.VECTORISED).sample(
            np.full(draws, population, dtype=np.intp), count
        )
        assert bool(np.all(np.diff(samples, axis=1) > 0))
        frequencies = np.bincount(samples.reshape(-1), minlength=population)
        expected = draws * count / population
        assert bool(np.all(np.abs(frequencies - expected) < 0.05 * expected))

    @pytest.mark.parametrize("row_count", [1, 10_000])
    def test_automatic_strategy_handles_small_and_large_batches(self, row_count: int) -> None:
        samples = BatchIndexSampler(np.random.default_rng(5)).sample(
            np.full(row_count, 100, dtype=np.intp), 8
        )
        assert samples.shape == (row_count, 8)
        assert bool(np.all(np.diff(samples, axis=1) > 0))
        assert bool(np.all((samples >= 0) & (samples < 100)))

    @pytest.mark.parametrize("strategy", list(BatchStrategy))
    def test_can_take_a_whole_population(self, strategy: BatchStrategy) -> None:
        samples = BatchIndexSampler(np.random.default_rng(2), strategy).sample(
            np.full(10, 4, dtype=np.intp), 4
        )
        assert np.array_equal(samples, np.tile(np.arange(4), (10, 1)))

    @pytest.mark.parametrize("strategy", list(BatchStrategy))
    def test_handles_an_empty_batch(self, strategy: BatchStrategy) -> None:
        samples = BatchIndexSampler(np.random.default_rng(0), strategy).sample(
            np.array([], dtype=np.intp), 3
        )
        assert samples.shape == (0, 3)

    def test_rejects_an_oversized_sample(self) -> None:
        with pytest.raises(InsufficientPopulationError):
            _ = BatchIndexSampler(np.random.default_rng(0)).sample(
                np.array([3, 5], dtype=np.intp), 4
            )

    def test_rejects_a_negative_count(self) -> None:
        with pytest.raises(InvalidSampleSizeError):
            _ = BatchIndexSampler(np.random.default_rng(0)).sample(np.array([3], dtype=np.intp), -1)

    def test_rejects_a_boolean_count(self) -> None:
        with pytest.raises(InvalidSampleSizeError):
            _ = BatchIndexSampler(np.random.default_rng(0)).sample(
                np.array([3], dtype=np.intp), True
            )

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
