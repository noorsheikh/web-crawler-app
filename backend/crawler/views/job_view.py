from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class CrawlerJobViewSet(ViewSet):
    def list(self):
        return Response({"message": "Hello there"})
