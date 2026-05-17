"""Tests for `src.utils` pure helper functions."""

import pytest

from src.utils import calculate_average_speed, format_file_size, format_seconds


class TestFormatSeconds:
    def test_zero(self):
        assert format_seconds(0) == "00:00:00"

    def test_under_one_minute(self):
        assert format_seconds(45) == "00:00:45"

    def test_one_minute(self):
        assert format_seconds(60) == "00:01:00"

    def test_one_hour_with_change(self):
        assert format_seconds(3661) == "01:01:01"

    def test_float_truncates_to_int(self):
        assert format_seconds(59.9) == "00:00:59"


class TestCalculateAverageSpeed:
    def test_empty_returns_zero(self):
        assert calculate_average_speed([]) == 0.0

    def test_single_value(self):
        assert calculate_average_speed([5.0]) == 5.0

    def test_multiple_values(self):
        assert calculate_average_speed([2.0, 4.0, 6.0]) == pytest.approx(4.0)


class TestFormatFileSize:
    def test_bytes(self):
        assert format_file_size(512) == "512.00 B"

    def test_kilobytes(self):
        assert format_file_size(2048) == "2.00 KB"

    def test_megabytes(self):
        assert format_file_size(5 * 1024 * 1024) == "5.00 MB"

    def test_gigabytes(self):
        result = format_file_size(3 * 1024**3)
        assert result.endswith("GB")
        assert result.startswith("3.")
