from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Plan, Personnel, VehicleUserPermission
from .serializers import PlanSerializer, PersonnelSerializer, VehicleUserPermissionSerializer
from accounts.permissions import IsAdminRole, PlanAccessPermission


class PersonnelViewSet(viewsets.ModelViewSet):
    """Personnel viewset - Admin CRUD only."""
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer
    permission_classes = [IsAdminRole]  # Admin-only CRUD


class PlanViewSet(viewsets.ModelViewSet):
    """Plan viewset."""
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [PlanAccessPermission]

    def get_queryset(self):
        """Filter plans based on user permissions."""
        user = self.request.user
        
        # Admins can see all plans
        if user.role == 'ADMIN':
            return Plan.objects.all()
        
        # Users can only see plans for vehicles they have permission for
        from planning.models import VehicleUserPermission
        permitted_vehicle_ids = VehicleUserPermission.objects.filter(
            user=user
        ).values_list('vehicle_id', flat=True)
        
        return Plan.objects.filter(vehicle_id__in=permitted_vehicle_ids)

    def get_permissions(self):
        """Override permissions for write operations."""
        # Admin can CRUD, User can only view (read-only)
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminRole()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Create a new plan with conflict detection."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # serializer.save() calls model.save() which calls full_clean() (includes conflict detection)
            serializer.save()
        except DjangoValidationError as e:
            # Convert Django ValidationError to DRF ValidationError
            raise DRFValidationError(e.message_dict)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Update a plan with conflict detection."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            # serializer.save() calls model.save() which calls full_clean() (includes conflict detection)
            serializer.save()
        except DjangoValidationError as e:
            # Convert Django ValidationError to DRF ValidationError
            raise DRFValidationError(e.message_dict)
        
        return Response(serializer.data)


class VehicleUserPermissionViewSet(viewsets.ModelViewSet):
    """Vehicle user permission viewset."""
    queryset = VehicleUserPermission.objects.all()
    serializer_class = VehicleUserPermissionSerializer
    permission_classes = [IsAdminRole]  # Only admins can manage permissions

    def get_queryset(self):
        """Return all vehicle user permissions."""
        return VehicleUserPermission.objects.all()
