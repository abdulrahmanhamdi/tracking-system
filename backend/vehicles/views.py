from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Vehicle
from .serializers import VehicleSerializer
from accounts.permissions import VehicleAccessPermission, IsAdminRole


class VehicleViewSet(viewsets.ModelViewSet):
    """Vehicle viewset."""
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [VehicleAccessPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'plate', 'brand']
    search_fields = ['plate', 'brand', 'model']
    ordering_fields = ['created_at', 'plate', 'brand', 'model']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter vehicles based on user permissions and query parameters."""
        user = self.request.user
        queryset = Vehicle.objects.all()
        
        # Admins can see all vehicles
        if user.role != 'ADMIN':
            # Users can only see vehicles they have permission for
            from planning.models import VehicleUserPermission
            permitted_vehicles = VehicleUserPermission.objects.filter(
                user=user
            ).values_list('vehicle_id', flat=True)
            queryset = queryset.filter(id__in=permitted_vehicles)
        
        # Apply search filter
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(plate__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search)
            )
        
        # Apply individual filters
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        plate = self.request.query_params.get('plate', None)
        if plate:
            queryset = queryset.filter(plate__icontains=plate)
        
        brand = self.request.query_params.get('brand', None)
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        
        return queryset

    def get_permissions(self):
        """Override permissions for write operations."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminRole()]
        return super().get_permissions()
