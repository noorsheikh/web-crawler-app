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

Test methods use mocking to simulate HTTP responses with varying HTML content.

Usage:
    pytest crawler/tests/services/test_crawler_service.py
"""

from unittest.mock import patch, Mock
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
def test_successful_crawl(mock_get, crawler):
    """Tests successful crawl of one page and two child links.
    Validates total URL count, domain aggregation, status codes, and title extraction.
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


@patch("requests.get")
def test_non_200_status(mock_get, crawler):
    """Simulates a 404 HTTP response.
    Verifies that errors are tracked and status code is recorded.
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


@patch("requests.get")
def test_exception_handling(mock_get, crawler):
    """Simulates a network error using side_effect.
    Ensures errors are recorded and title is set to 'ERROR'.
    """

    mock_get.side_effect = requests.exceptions.RequestException()

    stats = crawler.crawl("http://example.com")

    assert stats.total_urls == 1
    assert stats.errors == 1
    assert stats.status_code_counts[0] == 1
    assert stats.results[0]["title"] == "ERROR"


@pytest.mark.parametrize(
    "url,expected",
    [
        ("http://example.com/image.jpg", True),
        ("http://example.com/page.html", False),
        ("http://example.com/file.png", True),
        ("http://example.com/article", False),
    ],
)
def test_blacklist(url, expected):
    """Tests the blacklist logic in CrawlerConfig using parameterized extensions."""

    config = CrawlerConfig(blacklist=[".jpg", ".png"])
    assert config.is_blacklisted(url) == expected


@pytest.mark.parametrize(
    "url,domains,expected",
    [
        ("http://example.com", ["example.com"], True),
        ("http://another.com", ["example.com"], False),
        ("http://yetanother.com", [], True),  # No restriction
    ],
)
def test_is_allowed_domain(url, domains, expected):
    """Tests domain filtering logic based on allowed domain list."""

    config = CrawlerConfig(domains=domains)
    assert config.is_allowed_domain(url) == expected


@patch("requests.get")
def test_max_depth_not_exceeded(mock_get, crawler):
    """Verifies that URLs beyond the max_depth are not crawled."""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = HTML_PAGE.encode("utf-8")
    mock_response.text = HTML_PAGE
    mock_get.return_value = mock_response

    crawler.config.max_depth = 0
    stats = crawler.crawl("http://example.com")

    # Only the start URL should be crawled
    assert stats.total_urls == 1
    assert all(url["url"] == "http://example.com" for url in stats.results)


@patch("requests.get")
def test_deduplication(mock_get, crawler):
    """Ensures that the same URL is not crawled more than once."""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = HTML_PAGE.encode("utf-8")
    mock_response.text = HTML_PAGE
    mock_get.return_value = mock_response

    crawler.crawl("http://example.com")
    crawler.crawl("http://example.com")  # Should not crawl again

    # Still only 1 URL should be in stats
    assert len(crawler.visited) == 3
