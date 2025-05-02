from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

class CrawlerJobViewSet(ViewSet):
  def list(self, request, pk=None):
    return Response({'message': 'Hello there'})
