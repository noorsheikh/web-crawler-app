from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from threading import Thread
from crawler.services.crawler_service import CrawlerConfig, WebCrawler


class CrawlerViewSet(ViewSet):
    # def create(self, request):
    #     url = request.data.get("url")
    #     max_depth = int(request.data.get("max_depth", 2))
    #     domains = request.data.get("domains", [])
    #     blacklist = request.data.get("blacklist", [".jpg", ".png", ".css", ".js", ".pdf"])

    #     if not url:
    #         return Response({"error": "URL is required."}, status=status.HTTP_400_BAD_REQUEST)

    #     config = CrawlerConfig(max_depth=max_depth, domains=domains, blacklist=blacklist)
    #     crawler = WebCrawler(config)

    #     # Run crawl in background to avoid blocking the request.
    #     thread = Thread(target=crawler.crawl, args=(url,))
    #     thread.start()

    #     return Response({"message": "Crawl started."}, status=status.HTTP_200_ACCEPTED)

    @action(detail=False, methods=["get"], url_path="list")
    def get(self, request):
        return Response({"message": "Hello there"})
