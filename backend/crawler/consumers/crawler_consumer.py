"""
WebSocket consumer for broadcasting real-time web crawling statistics to connected clients.

This module defines `CrawlerConsumer`, a Django Channels consumer that handles WebSocket
connections, listens to a crawl-related group, and sends live updates (e.g., total URLs crawled,
error counts, etc.) to the front-end.
"""

import json
from typing import Dict, Any
from channels.generic.websocket import AsyncWebsocketConsumer

class CrawlerConsumer(AsyncWebsocketConsumer):
  """WebSocket consumer to handle real-time communication for crawler stats.
  Clients connect to this consumer to receive periodic crawl updates.
  """

  async def connect(self) -> None:
    """Handles new WebSocket connections by joining a shared group and sending a welcome message."""

    self.group_name = "crawl_group"
    await self.channel_layer.group_add(self.group_name, self.channel_name)
    await self.accept()
    await self.send(text_data=json.dumps({
      "message": "Connected to crawl WebSocket."
    }))

  async def disconnect(self, close_code: int) -> None:
    """Handles disconnection from the WebSocket by leaving the group.

    Args:
        close_code (int): The code representing the disconnection reason.
    """

    await self.channel_layer.group_discard(self.group_name, self.channel_name)

  async def send_crawl_stats(self, event: Dict[str, Any]) -> None:
    """Receives crawl stats from the group and sends them to the WebSocket client.

    Args:
        event (Dict[str, Any]): The event containing `stats_data` to be sent.
    """
    await self.send(text_data=json.dumps(event["stats_data"]))
