"""
WebSocket routing configuration.
"""
from django.urls import re_path
from tracking.consumers import LiveTrackingConsumer

websocket_urlpatterns = [
    re_path(r'^ws/live/?$', LiveTrackingConsumer.as_asgi()),
]
