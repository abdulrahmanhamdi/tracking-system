from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonnelViewSet

router = DefaultRouter()
router.register(r'', PersonnelViewSet, basename='personnel')

urlpatterns = [
    path('', include(router.urls)),
]

