import pytest
import requests
from unittest.mock import patch, Mock
from crawler.services.crawler_service import WebCrawler, CrawlerConfig, CrawlStats

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


@pytest.fixture
def crawler_config():
    return CrawlerConfig(
        max_depth=1, domains=["example.com"], blacklist=[".jpq=g", ".png"]
    )


@pytest.fixture
def crawler(crawler_config):
    return WebCrawler(config=crawler_config)


@patch("requests.get")
def test_successful_crawl(mock_get, crawler):
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
    config = CrawlerConfig(domains=domains)
    assert config.is_allowed_domain(url) == expected


@patch("requests.get")
def test_max_depth_not_exceeded(mock_get, crawler):
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
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = HTML_PAGE.encode("utf-8")
    mock_response.text = HTML_PAGE
    mock_get.return_value = mock_response

    stats = crawler.crawl("http://example.com")
    stats2 = crawler.crawl("http://example.com")  # Should not crawl again

    # Still only 1 URL should be in stats
    assert len(crawler.visited) == 3
