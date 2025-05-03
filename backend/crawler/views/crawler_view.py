"""
crawler_view.py

This module defines the CrawlerViewSet, a Django REST Framework ViewSet responsible for handling
web crawl initiation requests. It accepts user input such as a starting URL, depth limits,
domain restrictions, and file type blacklists, then spawns a background thread to perform
a breadth-first crawl using the configured settings.

Logging is used extensively for observability, debugging, and traceability.
"""

import logging
from threading import Thread
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from crawler.services.crawler_service import WebCrawler, CrawlerConfig

logger = logging.getLogger(__name__)


class CrawlerViewSet(ViewSet):
    """A ViewSet that provides an API endpoint to initiate a web crawling process.

    This class exposes a `POST /api/crawler/start/` endpoint, which starts a background web crawl
    using the provided URL and optional configuration parameters like crawl depth, allowed
    domains, and URL path blacklists.
    """

    @action(detail=False, methods=["post"], url_path="start")
    def start(self, request: Request) -> Response:
        """Handle POST requests to start a web crawl in the background.

        Expects a JSON body with the following keys:
        - url (str): The starting point for the crawl. (required)
        - max_depth (int): Maximum depth to crawl from the start URL. Default is 2.
        - domains (list): List of domain names to restrict crawling to.
        - blacklist (list): List of URL suffixes to avoid crawling (e.g. images, scripts).

        Returns:
            Response: A success message if the thread was started, or an error message.
        """

        logger.info("Received crawl request", extra={"request_data": request.data})

        url = request.data.get("url")
        max_depth = int(request.data.get("max_depth", 2))
        domains = request.data.get("domains", [])
        blacklist = request.data.get("blacklist", [".jpg", ".png", ".css", ".js", ".pdf"])

        if not url:
            logger.warning("Missing 'url' in crawl request")
            return Response({"error": "URL is required."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Initializing crawler config", extra={
            "url": url,
            "max_depth": max_depth,
            "domains": domains,
            "blacklist": blacklist
        })

        try:
            config = CrawlerConfig(max_depth=max_depth, domains=domains, blacklist=blacklist)
            crawler = WebCrawler(config)

            logger.info("Starting crawler thread", extra={"start_url": url})
            thread = Thread(target=crawler.crawl, args=(url,))
            thread.start()

            logger.info("Crawl thread started successfully", extra={"thread_name": thread.name})
            return Response({"message": "Crawl started."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Exception occurred while starting crawler: %s", e)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
