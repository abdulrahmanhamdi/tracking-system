from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet
from tracking.views import VehicleLocationNestedViewSet, last_locations_view, set_simulation_route

router = DefaultRouter()
router.register(r'', VehicleViewSet, basename='vehicle')

urlpatterns = [
    path('last-locations/', last_locations_view, name='last-locations'),
    
    path('<int:vehicle_pk>/locations/', VehicleLocationNestedViewSet.as_view({'get': 'list'}), name='vehicle-locations'),
    path('<int:vehicle_id>/simulation-route/', set_simulation_route, name='set-simulation-route'),
    
    path('', include(router.urls)), 
]
