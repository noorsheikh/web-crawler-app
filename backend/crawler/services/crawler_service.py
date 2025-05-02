import requests
from urllib.parse import urlparse, urljoin
from collections import deque, defaultdict
import mimetypes
from bs4 import BeautifulSoup

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
          bool: True if the domain is allowed or no domain restrictions are set.
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
      ext = '.' + url.split('.')[-1]

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

  def record(self, url: str, status_code: int, content_length: int, title: str) -> list:
    """Record the metadata of a crawled URL.

    Args:
        url (str): The crawled URL.
        status_code (int): HTTP response status code.
        content_length (int): Size of the response in bytes.
        title (str): Title of the page.
    """

    self.total_urls += 1
    if not (200 <= status_code < 300):
      self.errors += 1
    self.status_code_counts[status_code] += 1
    self.domain_counts[urlparse(url).netloc] += 1
    self.results.append({
       'url': url,
       'status': status_code,
       'size': content_length,
       'title': title,
    })


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
    This is the core method of the crawler that performs a breadth-first search (BFS)
    of web pages starting from a given URL, up to a configured depth. It keeps track of
    visited URLs, collects stats (like status codes, apge sizes, and titles), and avoid
    crawling URLs that are outside allowed domains or are blacklisted by extension.

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

      if not self.config.is_allowed_domain(current_url) and self.config.is_blacklisted(current_url):
        continue

      try:
         response = requests.get(current_url, timeout=10)
         content_length = len(response.content)
         soup = BeautifulSoup(response.text, 'html.parser')
         title_tag = soup.find('title')
         title = title_tag.get_text(strip=True) if title_tag else ''

         self.stats.record(current_url, response.status_code, content_length, title)

         if depth < self.config.max_depth and response.status_code == 200:
            for link in soup.find_all('a', href=True):
               href = urljoin(current_url, link['href'])
               if href.startswith('http'):
                  queue.append((href, depth + 1))
      except Exception as e:
         self.stats.record(current_url, 0, 0, 'ERROR')

    return self.stats


if __name__ == "__main__":
   config = CrawlerConfig(2, ['https://www.specular.ai/', 'https://sst.dev/'], ['.jpeg', '.css'])
   crawler = WebCrawler(config)
   stats = crawler.crawl("https://www.specular.ai/")
   print(stats.domain_counts)
   print(stats.errors)
   print(stats.status_code_counts)
   print(stats.results)
