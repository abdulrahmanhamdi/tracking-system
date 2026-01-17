"""
WebSocket routing configuration.
"""
from django.urls import re_path
from tracking.consumers import LiveTrackingConsumer

# تعريف قائمة المسارات الخاصة ببروتوكول WebSocket
websocket_urlpatterns = [
    # توجيه طلبات التتبع الحي إلى LiveTrackingConsumer
    # المسار المستخدم في الواجهة الأمامية سيكون: ws://domain/ws/tracking/live/?vehicle_id=ID
    re_path(r'^ws/tracking/live/$', LiveTrackingConsumer.as_asgi()),
]