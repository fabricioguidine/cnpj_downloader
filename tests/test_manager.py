"""Tests for src.manager orchestration (network mocked via requests).

Both crawler and downloader do `import requests`, so they share one
`requests` module object. The fakes therefore route on the call site:
listing requests pass a `timeout` kwarg, file downloads pass `stream=True`.
"""

from pathlib import Path

from src.manager import CNPJDownloaderManager


# Synthetic directory tree served by the fake network:
#   root/    -> 2025-05/  Empresas0.zip
#   2025-05/ -> Estabelecimentos0.zip
_LISTINGS = {
    "https://fake.test/cnpj/": (
        '<a href="2025-05/">2025-05/</a><a href="Empresas0.zip">Empresas0.zip</a>'
    ),
    "https://fake.test/cnpj/2025-05/": (
        '<a href="Estabelecimentos0.zip">Estabelecimentos0.zip</a>'
    ),
}

_FILE_BODY = b"synthetic-zip-bytes"


class _ListingResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        return None


class _HeadResponse:
    headers = {"Content-Length": "0"}

    def raise_for_status(self):
        return None


class _GetResponse:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size=8192):
        yield _FILE_BODY


def _fake_get(url, timeout=None, stream=False, **kwargs):
    # Listings are fetched without streaming; files with stream=True.
    if stream:
        return _GetResponse()
    return _ListingResponse(_LISTINGS[url])


def _fake_head(url, allow_redirects=True, timeout=None):
    return _HeadResponse()


def _patch_network(monkeypatch):
    monkeypatch.setattr("src.crawler.requests.get", _fake_get)
    monkeypatch.setattr("src.downloader.requests.get", _fake_get)
    monkeypatch.setattr("src.downloader.requests.head", _fake_head)


def test_manager_creates_output_dir(tmp_path):
    out = tmp_path / "made" / "here"
    CNPJDownloaderManager(base_url="https://fake.test/cnpj/", output_dir=out)
    assert out.is_dir()


def test_manager_recursive_crawl_and_download(tmp_path, monkeypatch):
    out = tmp_path / "data"
    _patch_network(monkeypatch)

    mgr = CNPJDownloaderManager(base_url="https://fake.test/cnpj/", output_dir=out)
    mgr.run()

    top_file = out / "Empresas0.zip"
    nested_file = out / "2025-05" / "Estabelecimentos0.zip"

    assert top_file.is_file()
    assert nested_file.is_file()
    assert top_file.read_bytes() == _FILE_BODY
    assert nested_file.read_bytes() == _FILE_BODY
    # Two files downloaded -> two speed samples recorded.
    assert len(mgr.downloader.download_speeds) == 2


def test_manager_output_dir_is_path(tmp_path):
    mgr = CNPJDownloaderManager(
        base_url="https://fake.test/cnpj/", output_dir=str(tmp_path)
    )
    assert isinstance(mgr.output_dir, Path)
