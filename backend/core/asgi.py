"""
ASGI config for core project.
"""

import os
import django

# 1. ضبط متغير البيئة لملف الإعدادات أولاً وقبل أي استيراد آخر من Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 2. تهيئة Django بالكامل لضمان تحميل جميع التطبيقات (INSTALLED_APPS)
# هذا السطر ضروري جداً قبل استيراد الـ Routing أو الـ Consumers
django.setup()

# 3. الآن يمكننا استيراد get_asgi_application وتفعيل تطبيق HTTP
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# 4. استيراد مكونات Channels و Middleware التتبع بعد تهيئة Django
from channels.routing import ProtocolTypeRouter, URLRouter
from tracking.middleware import JWTAuthMiddleware
from core import routing

# 5. تعريف مكدس الـ WebSocket مع حماية JWT وتوجيه المسارات
# المسارات مستخرجة من core/routing.py
websocket_middleware_stack = JWTAuthMiddleware(
    URLRouter(
        routing.websocket_urlpatterns
    )
)

# 6. التوجيه النهائي للبروتوكولات (HTTP و WebSocket)
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": websocket_middleware_stack,
})