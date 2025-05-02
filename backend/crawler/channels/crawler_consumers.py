import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CrawlerConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    self.group_name = "crawler_group"
    await self.channel_layer.group_add(self.group_name, self.channel_name)
    await self.accept()
    await self.send(text_data=json.dumps({
      "message": "Connected to crawl WebSocket."
    }))

  async def disconnect(self, close_code):
    await self.channel_layer.group_discard(self.group_name, self.channel_name)

  async def send_crawl_stats(self, event):
    await self.send(text_data=json.dumps(event["stats_data"]))
