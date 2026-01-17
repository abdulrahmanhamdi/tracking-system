from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Vehicle
from .serializers import VehicleSerializer
from accounts.permissions import VehicleAccessPermission, IsAdminRole

class VehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة المركبات.
    - العرض متاح للمستخدمين حسب ملكيتهم، وللمسؤولين بشكل كامل.
    - الإضافة، التعديل، والحذف محصور فقط بالمسؤولين (ADMIN).
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    
    # الصلاحية الافتراضية للتحكم بالوصول العام
    permission_classes = [VehicleAccessPermission]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # تعريف الحقول التي يمكن الفلترة والبحث من خلالها
    filterset_fields = ['status', 'plate', 'brand']
    search_fields = ['plate', 'brand', 'model']
    ordering_fields = ['created_at', 'plate', 'brand', 'model']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        تصفية قائمة المركبات بناءً على هوية المستخدم ودوره الإداري.
        """
        user = self.request.user
        
        # التأكد من أن المستخدم مسجل دخول
        if not user.is_authenticated:
            return Vehicle.objects.none()
            
        # 1. المسؤول (ADMIN/Superuser/Staff) يرى جميع المركبات دون قيود
        is_admin = (
            user.is_superuser or 
            user.is_staff or 
            (hasattr(user, 'role') and str(user.role).upper() == 'ADMIN')
        )
        
        if is_admin:
            return Vehicle.objects.all()
        
        # 2. المستخدم العادي (USER): يرى المركبات التي يملكها فقط
        return Vehicle.objects.filter(owner=user).filter(
            status__in=['ACTIVE', 'INACTIVE']
        ).distinct()

    def get_permissions(self):
        """
        تحديد الصلاحية المطلوبة بناءً على نوع العملية.
        """
        # فرض صلاحية IsAdminRole لعمليات (إضافة، تعديل، حذف)
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminRole()]
        
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        عند إنشاء مركبة جديدة بواسطة المسؤول:
        - إذا تم إرسال معرف مالك (owner) في الطلب، يتم استخدامه.
        - إذا لم يتم إرساله، يتم تعيين المسؤول الحالي كمالك افتراضي.
        """
        owner_id = self.request.data.get('owner')
        if owner_id:
            serializer.save(owner_id=owner_id)
        else:
            serializer.save(owner=self.request.user)