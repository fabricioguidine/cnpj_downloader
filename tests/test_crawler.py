"""Tests for `src.crawler.Crawler` URL handling and link extraction."""
from unittest.mock import MagicMock, patch

from src.crawler import Crawler


def test_build_full_url_joins_relative_link():
    crawler = Crawler("https://example.com/root/")
    assert (
        crawler.build_full_url("https://example.com/root/", "sub/")
        == "https://example.com/root/sub/"
    )


def test_build_full_url_handles_file():
    crawler = Crawler("https://example.com/")
    assert (
        crawler.build_full_url("https://example.com/dir/", "file.zip")
        == "https://example.com/dir/file.zip"
    )


@patch("src.crawler.requests.get")
def test_get_links_filters_navigation_entries(mock_get):
    html = """
    <html><body>
      <a href="?C=N;O=D">Sort</a>
      <a href="/">Root</a>
      <a href="../">Parent Directory</a>
      <a href="2025-01/">2025-01/</a>
      <a href="readme.txt">readme.txt</a>
    </body></html>
    """
    response = MagicMock()
    response.text = html
    response.raise_for_status = MagicMock()
    mock_get.return_value = response

    crawler = Crawler("https://example.com/")
    links = crawler.get_links("https://example.com/")

    assert "2025-01/" in links
    assert "readme.txt" in links
    assert "?C=N;O=D" not in links
    assert "/" not in links
    assert "../" not in links


@patch("src.crawler.requests.get")
def test_get_links_returns_empty_on_error(mock_get):
    mock_get.side_effect = Exception("network down")

    crawler = Crawler("https://example.com/")
    assert crawler.get_links("https://example.com/") == []
