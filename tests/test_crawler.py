"""Tests for src.crawler link discovery (network mocked)."""

from src.crawler import Crawler


class _FakeResponse:
    def __init__(self, text, status_ok=True):
        self.text = text
        self._ok = status_ok

    def raise_for_status(self):
        if not self._ok:
            raise RuntimeError("HTTP error")


LISTING = """
<html><body>
<a href="?C=N;O=D">Name</a>
<a href="/">root</a>
<a href="../">Parent Directory</a>
<a href="2025-05/">2025-05/</a>
<a href="2025-06/">2025-06/</a>
<a href="Empresas0.zip">Empresas0.zip</a>
<a href="readme.txt">readme.txt</a>
</body></html>
"""


def test_get_links_filters_navigation(monkeypatch):
    crawler = Crawler("https://example.test/CNPJ/")
    monkeypatch.setattr(
        "src.crawler.requests.get",
        lambda url, timeout=None: _FakeResponse(LISTING),
    )
    links = crawler.get_links("https://example.test/CNPJ/")
    assert links == ["2025-05/", "2025-06/", "Empresas0.zip", "readme.txt"]


def test_get_links_returns_empty_on_error(monkeypatch):
    crawler = Crawler("https://example.test/CNPJ/")

    def boom(url, timeout=None):
        raise ConnectionError("no network")

    monkeypatch.setattr("src.crawler.requests.get", boom)
    assert crawler.get_links("https://example.test/CNPJ/") == []


def test_build_full_url():
    crawler = Crawler("https://example.test/CNPJ/")
    assert (
        crawler.build_full_url("https://example.test/CNPJ/", "2025-05/")
        == "https://example.test/CNPJ/2025-05/"
    )
    assert (
        crawler.build_full_url("https://example.test/CNPJ/2025-05/", "Empresas0.zip")
        == "https://example.test/CNPJ/2025-05/Empresas0.zip"
    )
