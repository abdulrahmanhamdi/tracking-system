from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanViewSet, PersonnelViewSet, VehicleUserPermissionViewSet

router = DefaultRouter()
router.register(r'', PlanViewSet, basename='plan')
router.register(r'', PersonnelViewSet, basename='personnel')

# Separate router for vehicle permissions (kept under planning for organization)
permissions_router = DefaultRouter()
permissions_router.register(r'vehicle-permissions', VehicleUserPermissionViewSet, basename='vehicle-permission')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(permissions_router.urls)),
]
