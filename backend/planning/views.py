from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Plan, Personnel, VehicleUserPermission
from .serializers import PlanSerializer, PersonnelSerializer, VehicleUserPermissionSerializer
from accounts.permissions import IsAdminRole, PlanAccessPermission, IsAdminOrReadOnly
from vehicles.models import Vehicle


class PersonnelViewSet(viewsets.ModelViewSet):
    """Personnel viewset - Admin CRUD, Users Read-Only."""
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer
    permission_classes = [IsAdminOrReadOnly] 


class PlanViewSet(viewsets.ModelViewSet):
    """Plan viewset."""
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [PlanAccessPermission]

    def get_queryset(self):
        """Filter plans so users only see the ones they created."""
        user = self.request.user
        
        # المسؤول يرى جميع الخطط في النظام
        if user.role == 'ADMIN':
            return Plan.objects.all()
        
        # المستخدم العادي يرى فقط الخطط التي قام بإنشائها بنفسه (عبر حقل created_by)
        return Plan.objects.filter(created_by=user)

    def get_permissions(self):
        """Override permissions logic."""
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Create a new plan and set the current user as the creator."""
        user = request.user
        vehicle_id = request.data.get('vehicle')

        # التحقق من حالة المركبة قبل السماح بالحجز
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            if vehicle.status == 'MAINTENANCE':
                raise DRFValidationError({
                    "vehicle": "هذه المركبة في وضع التصليح حالياً ولا يمكن حجزها."
                })
        except Vehicle.DoesNotExist:
            raise DRFValidationError({"vehicle": "المركبة غير موجودة."})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # حفظ الخطة مع ربطها بالمستخدم الحالي كمنشئ لها
            serializer.save(created_by=user)
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Update a plan with ownership and vehicle status check."""
        user = request.user
        instance = self.get_object()
        vehicle_id = request.data.get('vehicle')
        
        # التأكد من أن المستخدم هو المالك أو مسؤول (Admin)
        if user.role != 'ADMIN' and instance.created_by != user:
            return Response(
                {"detail": "ليس لديك صلاحية لتعديل هذه الخطة."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # في حال تغيير المركبة، نتأكد أنها ليست في حالة صيانة
        if vehicle_id:
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
                if vehicle.status == 'MAINTENANCE' and user.role != 'ADMIN':
                    raise DRFValidationError({
                        "vehicle": "لا يمكن نقل الخطة لمركبة في وضع التصليح."
                    })
            except Vehicle.DoesNotExist:
                raise DRFValidationError({"vehicle": "المركبة غير موجودة."})

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Allow admins or the creator of the plan to delete it."""
        instance = self.get_object()
        user = request.user

        # السماح بالحذف إذا كان المستخدم مسؤولاً أو هو من أنشأ الخطة
        if user.role == 'ADMIN' or instance.created_by == user:
            return super().destroy(request, *args, **kwargs)
        
        return Response(
            {"detail": "ليس لديك صلاحية لحذف هذه الخطة."}, 
            status=status.HTTP_403_FORBIDDEN
        )


class VehicleUserPermissionViewSet(viewsets.ModelViewSet):
    """Vehicle user permission viewset."""
    queryset = VehicleUserPermission.objects.all()
    serializer_class = VehicleUserPermissionSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return VehicleUserPermission.objects.all()