"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from accounts.views import me_view, admin_users_list_view, admin_users_update_view


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({"status": "ok"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health'),
    path('api/me/', me_view, name='me'),
    path('api/auth/', include('accounts.urls')),
    path('api/admin/users/', admin_users_list_view, name='admin_users'),
    path('api/admin/users/<int:user_id>/', admin_users_update_view, name='admin_user_detail'),
    path('api/vehicles/', include('vehicles.urls')),
    path('api/tracking/', include('tracking.urls')),
    path('api/plans/', include('planning.plans_urls')),
    path('api/personnel/', include('planning.personnel_urls')),
    path('api/live/', include('tracking.urls')),  # Live tracking endpoints
]
