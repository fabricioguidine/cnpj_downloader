"""Tests for src.utils formatting/calculation helpers."""
import pytest

from src.utils import calculate_average_speed, format_file_size, format_seconds


@pytest.mark.parametrize(
    "seconds,expected",
    [
        (0, "00:00:00"),
        (59, "00:00:59"),
        (60, "00:01:00"),
        (3661, "01:01:01"),
        (3600 * 25, "25:00:00"),
        (90.9, "00:01:30"),
    ],
)
def test_format_seconds(seconds, expected):
    assert format_seconds(seconds) == expected


def test_calculate_average_speed_empty():
    assert calculate_average_speed([]) == 0.0


def test_calculate_average_speed_values():
    assert calculate_average_speed([2.0, 4.0, 6.0]) == 4.0


@pytest.mark.parametrize(
    "size,expected",
    [
        (0, "0.00 B"),
        (512, "512.00 B"),
        (1024, "1.00 KB"),
        (1536, "1.50 KB"),
        (1024 ** 2, "1.00 MB"),
        (1024 ** 3, "1.00 GB"),
        (1024 ** 4, "1.00 TB"),
        (1024 ** 5, "1.00 PB"),
    ],
)
def test_format_file_size(size, expected):
    assert format_file_size(size) == expected
