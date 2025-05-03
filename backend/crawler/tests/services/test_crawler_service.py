"""
Unit tests for crawler_service.py

This module contains pytest-based unit tests for the web crawler defined in
crawler_service.py. The tests cover edge cases including:
- Successful crawling with links
- Handling non-200 status codes
- Exception handling on network errors
- Depth limiting
- Deduplication of visited URLs
- Domain and file extension filtering
- Redis caching of crawled URLs

Test methods use mocking to simulate HTTP responses with varying HTML content
and to mock Redis cache behaviors.

Usage:
    pytest crawler/tests/services/test_crawler_service.py
"""

from unittest.mock import patch, Mock, AsyncMock
import pytest
import requests
from crawler.services.crawler_service import WebCrawler, CrawlerConfig

# Mock HTML content
HTML_PAGE = """
<html>
  <head><title>Test Page</title></head>
  <body>
    <a href="http://example.com/page1">Page 1</a>
    <a href="http://example.com/page2">Page 2</a>
  </body>
</html>
"""


@pytest.fixture(name="crawler_config")
def fixture_crawler_config():
    """Returns a configured CrawlerConfig instance with:
    - max_depth = 1
    - allowed_domains = ['example.com']
    - blacklist = ['.jpq=g', '.png']
    """

    return CrawlerConfig(
        max_depth=1, domains=["example.com"], blacklist=[".jpq=g", ".png"]
    )


@pytest.fixture(name="crawler")
def fixture_crawler(crawler_config):
    """Returns a WebCrawler instance initialized with the crawler_config fixture."""

    return WebCrawler(config=crawler_config)


@patch("requests.get")
@patch("django.core.cache.cache.get", return_value=None)
@patch("django.core.cache.cache.set")
def test_successful_crawl(mock_cache_set, mock_cache_get, mock_get, crawler):
    """Tests successful crawl of one page and two child links.
    Validates total URL count, domain aggregation, status codes, and title extraction.
    Also verifies caching set call.
    """

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = HTML_PAGE.encode("utf-8")
    mock_response.text = HTML_PAGE
    mock_get.return_value = mock_response

    stats = crawler.crawl("http://example.com")

    assert stats.total_urls == 3
    assert stats.errors == 0
    assert stats.status_code_counts[200] == 3
    assert stats.domain_counts["example.com"] == 3
    assert stats.results[0]["title"] == "Test Page"
    assert mock_cache_set.call_count == 3


@patch("requests.get")
@patch("django.core.cache.cache.get", return_value=None)
@patch("django.core.cache.cache.set")
def test_non_200_status(mock_cache_set, mock_cache_get, mock_get, crawler):
    """Simulates a 404 HTTP response.
    Verifies that errors are tracked, status code is recorded, and cache is used.
    """

    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.text = ""
    mock_get.return_value = mock_response

    stats = crawler.crawl("http://example.com/404")

    assert stats.total_urls == 1
    assert stats.errors == 1
    assert stats.status_code_counts[404] == 1
    assert stats.domain_counts["example.com"] == 1
    assert stats.results[0]["status"] == 404
    assert mock_cache_set.call_count == 1


@patch("requests.get", side_effect=requests.exceptions.RequestException)
@patch("django.core.cache.cache.get", return_value=None)
@patch("django.core.cache.cache.set")
def test_network_exception(mock_cache_set, mock_cache_get, mock_get, crawler):
    """Simulates a network failure to test error handling and stat recording."""

    stats = crawler.crawl("http://example.com/error")

    assert stats.total_urls == 1
    assert stats.errors == 1
    assert stats.results[0]["status"] == 0
    assert stats.results[0]["title"] == "ERROR"
    assert mock_cache_set.call_count == 0


@patch("requests.get")
@patch("django.core.cache.cache.get", return_value=None)
@patch("django.core.cache.cache.set")
def test_depth_limit(mock_cache_set, mock_cache_get, mock_get, crawler_config):
    """Ensures crawler respects depth limits and avoids deeper levels."""

    html_with_deep_links = """
    <html>
      <body>
        <a href="http://example.com/deep1">Deep 1</a>
        <a href="http://example.com/deep2">Deep 2</a>
      </body>
    </html>
    """

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = html_with_deep_links.encode("utf-8")
    mock_response.text = html_with_deep_links
    mock_get.return_value = mock_response

    crawler = WebCrawler(crawler_config)
    stats = crawler.crawl("http://example.com")

    assert stats.total_urls == 3
    for url_stat in stats.results:
        assert url_stat["url"].startswith("http://example.com")


@patch("requests.get")
@patch("django.core.cache.cache.get")
@patch("django.core.cache.cache.set")
def test_cache_hit_skips_network(mock_cache_set, mock_cache_get, mock_get, crawler):
    """Verifies that cached responses bypass network calls."""

    mock_cache_get.return_value = {
        "status": 200,
        "size": 1234,
        "title": "Cached Page",
    }

    stats = crawler.crawl("http://example.com")

    assert stats.total_urls == 1
    assert stats.results[0]["title"] == "Cached Page"
    mock_get.assert_not_called()
    mock_cache_set.assert_not_called()


@patch("requests.get")
@patch("django.core.cache.cache.get", return_value=None)
@patch("django.core.cache.cache.set")
def test_blacklisted_extension(mock_cache_set, mock_cache_get, mock_get, crawler_config):
    """Ensures URLs with disallowed file extensions are skipped."""

    crawler = WebCrawler(crawler_config)
    stats = crawler.crawl("http://example.com/file.png")

    assert stats.total_urls == 0
    assert mock_get.call_count == 0
    assert mock_cache_set.call_count == 0


@patch("requests.get")
@patch("django.core.cache.cache.get", return_value=None)
@patch("django.core.cache.cache.set")
def test_domain_restriction(mock_cache_set, mock_cache_get, mock_get, crawler_config):
    """Ensures only allowed domains are crawled."""

    crawler = WebCrawler(crawler_config)
    stats = crawler.crawl("http://notallowed.com")

    assert stats.total_urls == 0
    mock_get.assert_not_called()
    mock_cache_set.assert_not_called()
