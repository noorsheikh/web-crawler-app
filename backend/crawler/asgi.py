"""
ASGI config for crawler project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from .urls import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crawler.settings")
django.setup()

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": URLRouter(websocket_urlpatterns),
})
