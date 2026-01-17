from rest_framework import serializers
from .models import Plan, Personnel, VehicleUserPermission
from vehicles.serializers import VehicleSerializer


class PersonnelSerializer(serializers.ModelSerializer):
    """Personnel serializer."""
    class Meta:
        model = Personnel
        fields = ('id', 'full_name', 'title', 'phone', 'email')
        read_only_fields = ('id',)


class PlanSerializer(serializers.ModelSerializer):
    """Plan serializer."""
    vehicle_info = VehicleSerializer(source='vehicle', read_only=True)
    personnel_info = PersonnelSerializer(source='personnel', read_only=True)
    # حقل جديد لحساب رقم الخطة الخاص بالمستخدم
    user_plan_number = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = (
            'id', 'user_plan_number', 'vehicle', 'vehicle_info', 
            'personnel', 'personnel_info', 'created_by', 'start_at', 
            'end_at', 'description', 'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user_plan_number', 'created_by', 'created_at', 'updated_at')

    def get_user_plan_number(self, obj):
        """
        حساب رقم الخطة التسلسلي للمستخدم الذي أنشأها فقط.
        """
        if obj.created_by:
            # نقوم بعدّ الخطط التي أنشأها نفس المستخدم والتي لها معرف (ID) أصغر من أو يساوي المعرف الحالي
            return Plan.objects.filter(
                created_by=obj.created_by, 
                id__lte=obj.id
            ).count()
        return None


class VehicleUserPermissionSerializer(serializers.ModelSerializer):
    """Vehicle user permission serializer."""
    vehicle_info = VehicleSerializer(source='vehicle', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = VehicleUserPermission
        fields = ('id', 'user', 'user_email', 'vehicle', 'vehicle_info', 'created_at')
        read_only_fields = ('id', 'created_at')