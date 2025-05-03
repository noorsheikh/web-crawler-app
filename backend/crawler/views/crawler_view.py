import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from threading import Thread

from crawler.services.crawler_service import WebCrawler, CrawlerConfig

logger = logging.getLogger(__name__)


class CrawlerViewSet(ViewSet):
    @action(detail=False, methods=["post"], url_path="start")
    def start(self, request):
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
            logger.exception("Exception occurred while starting crawler")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
