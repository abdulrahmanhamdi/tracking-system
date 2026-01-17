from rest_framework import serializers
from .models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    """
    سيريالايزر المركبات الكامل والمعدل.
    تم إعداد الحقول لضمان قدرة الأدمن على الإضافة والتحكم الكامل في كافة خصائص المركبة.
    """
    class Meta:
        model = Vehicle
        # إدراج كافة الحقول لضمان ظهورها وتعديلها في الواجهة الأمامية (React)
        fields = (
            'id', 
            'plate', 
            'brand', 
            'model', 
            'year', 
            'status', 
            'owner', 
            'is_streaming', 
            'simulation_route', 
            'created_at'
        )
        
        # حصر حقول القراءة فقط في الحقول التلقائية التي ينشئها النظام (ID وتاريخ الإنشاء)
        # تم التأكد من إزالة 'owner' من هنا لكي يقبل السيرفر بيانات المالك عند الإضافة أو التعديل
        read_only_fields = ('id', 'created_at')

    def validate_plate(self, value):
        """التحقق من أن رقم اللوحة فريد وغير مكرر في النظام."""
        # البحث عن أي مركبة تحمل نفس رقم اللوحة مع استبعاد المركبة الحالية في حالة التعديل
        query = Vehicle.objects.filter(plate=value)
        if self.instance:
            query = query.exclude(id=self.instance.id)
            
        if query.exists():
            raise serializers.ValidationError("رقم اللوحة هذا مسجل بالفعل لمركبة أخرى.")
        return value