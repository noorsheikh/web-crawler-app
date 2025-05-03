"""
crawler_service.py

This module defines a simple, configurable web crawler using Python's standard libraries
and BeautifulSoup.
It includes the following components:

- `CrawlerConfig`: Configuration options for allowed domains, blacklisted file extensions,
and maximum crawl depth.
- `CrawlStats`: Collects and summarizes statistics from the crawl, including status codes,
content sizes, and titles.
- `WebCrawler`: Core class that performs a breadth-first crawl of web pages starting from
a given URL.

The crawler respects domain restrictions and avoids crawling URLs with disallowed file extensions.
It extracts titles from HTML pages and gathers analytics while handling failures gracefully.

Typical usage:
--------------
config = CrawlerConfig(max_depth=2, domains=["example.com"], blacklist=[".pdf", ".jpg"])
crawler = WebCrawler(config)
stats = crawler.crawl("https://example.com")

Returns a `CrawlStats` object with metadata about each visited page.
"""

import mimetypes
from urllib.parse import urlparse, urljoin
from collections import deque, defaultdict
from bs4 import BeautifulSoup
import requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class CrawlerConfig:
    """Configuration class for the web crawler.

    Attributes:
        max_depth (int): Maximum depth to crawl from the starting URL.
        allowed_domains (list): List of domains allowed to be crawled.
        blacklist (list): List of file extensions or patterns to avoid.
    """

    def __init__(self, max_depth=2, domains=None, blacklist=None):
        """Initialize CrawlerConfig.

        Args:
            max_depth (int): Maximum crawl depth.
            domains (list): Allowed domains.
            blacklist (list): Disallowed file extensions.
        """
        self.max_depth = max_depth
        self.allowed_domains = domains or []
        self.blacklist = blacklist or []

    def is_allowed_domain(self, url: str) -> list:
        """Check if the domain of the given URL is allowed.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the domain is allowed or no domain restrictions are
            set.
        """

        if not self.allowed_domains:
            return True

        domain = urlparse(url).netloc

        return domain in self.allowed_domains

    def is_blacklisted(self, url: str) -> bool:
        """Check if the URL is blacklisted based on file extension.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL is blacklisted.
        """

        ext = mimetypes.guess_extension(urlparse(url).path)
        if not ext:
            ext = "." + url.split(".")[-1]

        return ext.lower() in self.blacklist


class CrawlStats:
    """Collects and maintains statistics of the crawl.

    Attributes:
        total_urls (int): Total number of URLs crawled.
        errors (int): Total number of failed requests.
        status_code_counts (dict): Count of HTTP status codes encountered.
        domain_counts (dict): Count of crawled URLs per domain.
        results (list): List of crawl result metadata.
    """

    def __init__(self):
        """Initialize crawl statistics."""

        self.total_urls = 0
        self.errors = 0
        self.status_code_counts = defaultdict(int)
        self.domain_counts = defaultdict(int)
        self.results = []

    def record(
        self, url: str, status_code: int, content_length: int, title: str
    ) -> list:
        """Record the metadata of a crawled URL.

        Args:
            url (str): The crawled URL.
            status_code (int): HTTP response status code.
            content_length (int): Size of the response in bytes.
            title (str): Title of the page.
        """

        self.total_urls += 1
        if not 200 <= status_code < 300:
            self.errors += 1
        self.status_code_counts[status_code] += 1
        self.domain_counts[urlparse(url).netloc] += 1
        self.results.append(
            {
                "url": url,
                "status": status_code,
                "size": content_length,
                "title": title,
            }
        )


class WebCrawler:
    """Core web crawler that performs a breadth-first crawl of web pages.

    Attributes:
        config (CrawlerConfig): Crawler configuration instance.
        visited (set): Set of already visited URLs.
        stats (CrawlStats): Object to track crawl statistics.
    """

    def __init__(self, config: CrawlerConfig):
        """Initialize the WebCrawler.

        Args:
            config (CrawlerConfig): Configuration for crawling rules.
        """

        self.config = config
        self.visited = set()
        self.stats = CrawlStats()

    def crawl(self, start_url: str) -> CrawlStats:
        """Start crawling from the given URL.
        This is the core method of the crawler that performs a breadth-first
        search (BFS) of web pages starting from a given URL, up to a
        configured depth. It keeps track of visited URLs, collects stats
        (like status codes, apge sizes, and titles), and avoid crawling
        URLs that are outside allowed domains or are blacklisted by extension.

        Args:
            start_url (str): The URL to begin crawling from.

        Returns:
            CrawlStats: Object containing crawl statistics and results.
        """

        queue = deque([(start_url, 0)])

        while queue:
            current_url, depth = queue.popleft()
            if current_url in self.visited or depth > self.config.max_depth:
                continue
            self.visited.add(current_url)

            if not self.config.is_allowed_domain(
                current_url
            ) and self.config.is_blacklisted(current_url):
                continue

            try:
                response = requests.get(current_url, timeout=10)
                content_length = len(response.content)
                soup = BeautifulSoup(response.text, "html.parser")
                title_tag = soup.find("title")
                title = title_tag.get_text(strip=True) if title_tag else ""

                self.stats.record(
                    current_url, response.status_code, content_length, title
                )

                # Live broadcast stats to client.
                async_to_sync(self.broadcast_stats)()

                if depth < self.config.max_depth and response.status_code == 200:
                    for link in soup.find_all("a", href=True):
                        href = urljoin(current_url, link["href"])
                        if href.startswith("http"):
                            queue.append((href, depth + 1))
            except Exception:
                self.stats.record(current_url, 0, 0, "ERROR")
                # Live broadcast stats to client.
                async_to_sync(self.broadcast_stats)()

        return self.stats

    async def broadcast_stats(self):
        """Asynchronously broadcasts the current crawl statistics to all WebSocket clients in the 'crawl_group'.

        This method uses Django Channels to send a message to a channel group named 'crawl_group'. The message
        contains the following crawl statistics:

        - total_urls: Total number of URLs processed during the crawl.
        - errors: Number of URLs that resulted in errors.
        - status_counts: A dictionary mapping HTTP status codes to their frequency.
        - domain_counts: A dictionary mapping domain names to the number of times they were encountered.

        Notes:
            - If the channel layer is not configured or unavailable, the method exits silently.
            - All dictionary keys are converted to strings to ensure JSON serialization compatibility.
        """

        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        await channel_layer.group_send(
            "crawl_group",
            {
                "type": "send_crawl_stats",
                "stats_data": {
                    "total_urls": self.stats.total_urls,
                    "errors": self.stats.errors,
                    "status_counts": {str(k): v for k, v in self.stats.status_code_counts.items()},
                    "domain_counts": {str(k): v for k, v in self.stats.domain_counts.items()},
                },
            },
        )
