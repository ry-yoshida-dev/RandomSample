import pytest

from array_sampling import InvalidSampleSizeError, RoundingMode, SampleCount, SampleFraction


class TestSampleSize:
    def test_count_resolves_to_its_value(self) -> None:
        assert SampleCount(7).resolve(100) == 7

    @pytest.mark.parametrize(
        ("rounding_mode", "expected"),
        [(RoundingMode.FLOOR, 3), (RoundingMode.CEIL, 3), (RoundingMode.NEAREST, 3)],
    )
    def test_fraction_uses_exact_decimal_arithmetic(
        self, rounding_mode: RoundingMode, expected: int
    ) -> None:
        assert SampleFraction(0.1, rounding_mode).resolve(30) == expected

    def test_fraction_nearest_rounds_half_up(self) -> None:
        assert SampleFraction(0.5).resolve(5) == 3

    @pytest.mark.parametrize("invalid_count", [-1, True])
    def test_invalid_count_is_rejected(self, invalid_count: int) -> None:
        with pytest.raises(InvalidSampleSizeError):
            _ = SampleCount(invalid_count)

    @pytest.mark.parametrize("invalid_fraction", [-0.1, float("nan"), float("inf"), True])
    def test_invalid_fraction_is_rejected(self, invalid_fraction: float) -> None:
        with pytest.raises(InvalidSampleSizeError):
            _ = SampleFraction(invalid_fraction)
