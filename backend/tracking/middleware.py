"""
Custom middleware for JWT authentication in WebSocket connections.
"""
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from urllib.parse import parse_qs

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    """JWT authentication middleware for WebSocket connections."""
    
    async def __call__(self, scope, receive, send):
        """Process WebSocket connection and add user to scope."""
        # 1. استخراج التوكن من رابط الطلب (Query String) أو الهيدرز
        token = None
        
        # محاولة جلب التوكن من الرابط (مثلاً: ?token=...)
        query_string = scope.get('query_string', b'').decode()
        if query_string:
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]
        
        # إذا لم يوجد في الرابط، نحاول جلب التوكن من الـ Headers
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Bearer '):
                token = auth_header.split('Bearer ')[1]
        
        # 2. التحقق من صحة التوكن وجلب المستخدم
        user = None
        if token:
            try:
                # التحقق الأولي من هيكلية التوكن
                UntypedToken(token)
                # فك تشفير التوكن للحصول على معرف المستخدم (user_id)
                decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_data.get('user_id')
                
                if user_id:
                    user = await self.get_user(user_id)
            except (InvalidToken, TokenError, Exception):
                # في حال كان التوكن منتهياً أو غير صالح، نترك المستخدم None
                user = None
        
        # 3. إضافة كائن المستخدم إلى الـ scope ليكون متاحاً في الـ Consumer
        scope['user'] = user
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, user_id):
        """جلب المستخدم من قاعدة البيانات بشكل غير متزامن."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None