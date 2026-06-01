"""Tests for src.downloader (network mocked, filesystem under tmp_path)."""
from pathlib import Path

import pytest

from src.downloader import Downloader


class _FakeGetResponse:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size=8192):
        for i in range(0, len(self._payload), chunk_size):
            yield self._payload[i : i + chunk_size]


class _FakeHeadResponse:
    def __init__(self, size):
        self.headers = {"Content-Length": str(size)}

    def raise_for_status(self):
        return None


def test_get_remote_file_size(monkeypatch):
    d = Downloader()
    monkeypatch.setattr(
        "src.downloader.requests.head",
        lambda url, allow_redirects=True, timeout=None: _FakeHeadResponse(4242),
    )
    assert d.get_remote_file_size("https://example.test/f.zip") == 4242


def test_get_remote_file_size_error_returns_none(monkeypatch):
    d = Downloader()

    def boom(url, allow_redirects=True, timeout=None):
        raise ConnectionError("down")

    monkeypatch.setattr("src.downloader.requests.head", boom)
    assert d.get_remote_file_size("https://example.test/f.zip") is None


def test_should_skip_download_missing_file(tmp_path):
    d = Downloader()
    assert d.should_skip_download(tmp_path / "nope.zip", 100) is False


def test_should_skip_download_size_match(tmp_path):
    d = Downloader()
    f = tmp_path / "f.zip"
    f.write_bytes(b"abc")
    assert d.should_skip_download(f, 3) is True


def test_should_skip_download_size_mismatch(tmp_path):
    d = Downloader()
    f = tmp_path / "f.zip"
    f.write_bytes(b"abc")
    assert d.should_skip_download(f, 999) is False


def test_download_file_writes_payload(tmp_path, monkeypatch):
    payload = b"binary-\x00\x01\x02-data" * 10
    d = Downloader()

    monkeypatch.setattr(
        "src.downloader.requests.head",
        lambda url, allow_redirects=True, timeout=None: _FakeHeadResponse(0),
    )
    monkeypatch.setattr(
        "src.downloader.requests.get",
        lambda url, stream=False: _FakeGetResponse(payload),
    )

    dest = tmp_path / "sub" / "deep" / "file.zip"
    ok = d.download_file("https://example.test/file.zip", dest)

    assert ok is True
    assert Path(dest).read_bytes() == payload
    assert len(d.download_speeds) == 1


def test_download_file_skips_when_complete(tmp_path, monkeypatch):
    d = Downloader()
    dest = tmp_path / "file.zip"
    dest.write_bytes(b"already-here")

    monkeypatch.setattr(
        "src.downloader.requests.head",
        lambda url, allow_redirects=True, timeout=None: _FakeHeadResponse(len(b"already-here")),
    )

    def fail_get(*a, **k):
        raise AssertionError("should not download when skipping")

    monkeypatch.setattr("src.downloader.requests.get", fail_get)

    assert d.download_file("https://example.test/file.zip", dest) is True
    assert dest.read_bytes() == b"already-here"


def test_download_file_removes_partial_on_error(tmp_path, monkeypatch):
    d = Downloader()
    dest = tmp_path / "file.zip"

    monkeypatch.setattr(
        "src.downloader.requests.head",
        lambda url, allow_redirects=True, timeout=None: _FakeHeadResponse(0),
    )

    def boom(url, stream=False):
        raise ConnectionError("dropped")

    monkeypatch.setattr("src.downloader.requests.get", boom)

    assert d.download_file("https://example.test/file.zip", dest) is False
    assert not dest.exists()


def test_get_average_speed():
    d = Downloader()
    d.download_speeds = [1.0, 3.0]
    assert d.get_average_speed() == 2.0
