from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleLocationViewSet,
    set_simulation_route,
    start_streaming,
    stop_streaming
)

router = DefaultRouter()
router.register(r'locations', VehicleLocationViewSet, basename='vehicle-location')

urlpatterns = [
    path('', include(router.urls)),
    path('start/<int:vehicle_id>/', start_streaming, name='start-streaming'),
    path('stop/<int:vehicle_id>/', stop_streaming, name='stop-streaming'),
]
