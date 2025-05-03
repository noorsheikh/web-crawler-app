"""
Unit tests for the CrawlerViewSet's 'start' action.

This test suite verifies the behavior of the crawl start endpoint under various conditions:
- When required fields like 'url' are missing.
- When valid minimal input is provided.
- When custom max_depth, domains, and blacklist filters are used.
- When an internal exception occurs during crawler initialization.

The tests use pytest fixtures, Django's APIRequestFactory for request simulation,
and unittest.mock for patching dependencies (like threading, crawler config, and services).

Usage:
    pytest crawler/tests/views/test_crawler_view.py
"""

from unittest.mock import patch
import pytest
import django
from rest_framework.test import APIRequestFactory
from rest_framework import status

from crawler.views.crawler_view import CrawlerViewSet

django.setup()


@pytest.fixture(name="factory")
def fixture_factory():
    """Returns an instance of APIRequestFactory for simulating HTTP requests."""

    return APIRequestFactory()


@pytest.fixture(name="view")
def fixture_view():
    """Returns the 'start' view from the CrawlerViewSet bound to POST method."""

    return CrawlerViewSet.as_view({"post": "start"})


def test_start_missing_url(factory, view):
    """Test that a missing 'url' field returns a 400 response with an appropriate error message."""

    request = factory.post("/api/crawler/start/", data={}, format="json")
    response = view(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "URL is required."


@patch("crawler.views.crawler_view.Thread")
@patch("crawler.views.crawler_view.WebCrawler")
@patch("crawler.views.crawler_view.CrawlerConfig")
def test_start_with_minimal_valid_data(mock_config, mock_crawler, mock_thread, factory, view):
    """Test crawl starts successfully with only the required URL field."""

    request = factory.post(
        "/api/crawler/start/",
        data={"url": "https://example.com"},
        format="json",
    )
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Crawl started."
    mock_config.assert_called_once()
    mock_crawler.assert_called_once()
    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()


@patch("crawler.views.crawler_view.Thread")
@patch("crawler.views.crawler_view.WebCrawler")
@patch("crawler.views.crawler_view.CrawlerConfig")
def test_start_with_custom_depth_and_filters(mock_config, mock_crawler, mock_thread, factory, view):
    """Test crawl starts correctly when custom depth, domains, and blacklist are provided."""

    request = factory.post("/api/crawler/start/", data={
        "url": "https://example.com",
        "max_depth": 3,
        "domains": ["example.com"],
        "blacklist": [".jpg", ".gif"]
    }, format="json")
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    mock_config.assert_called_once_with(
        max_depth=3,
        domains=["example.com"],
        blacklist=[".jpg", ".gif"]
    )
    mock_crawler.assert_called_once()
    mock_thread.assert_called_once()


@patch("crawler.views.crawler_view.Thread")
@patch("crawler.views.crawler_view.WebCrawler")
@patch("crawler.views.crawler_view.CrawlerConfig", side_effect=Exception("Config error"))
def test_start_internal_exception(mock_config, mock_crawler, mock_thread, factory, view):
    """Test that an internal exception during configuration returns a 500 error response."""

    request = factory.post(
        "/api/crawler/start/",
        data={"url": "https://example.com"},
        format="json",
    )
    response = view(request)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data["error"] == "Internal server error"
    mock_config.assert_called_once()
    mock_crawler.assert_not_called()
    mock_thread.assert_not_called()
