from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    """
    سيريالايزر المستخدم الكامل.
    يتم إرسال كافة حقول الصلاحيات لضمان تعرف الواجهة الأمامية (React) على الأدمن.
    """
    class Meta:
        model = User
        # الحقول الضرورية للتحقق من الصلاحيات في الواجهة والخلفية
        fields = (
            'id', 
            'email', 
            'username', 
            'first_name', 
            'last_name', 
            'phone', 
            'role', 
            'is_active', 
            'is_superuser', 
            'is_staff', 
            'created_at'
        )
        # تم إبقاء id وتاريخ الإنشاء فقط كحقول للقراءة فقط
        # تم السماح بتعديل 'role' و 'is_active' لكي يتمكن الأدمن من إدارتها
        read_only_fields = ('id', 'created_at')

class RegisterSerializer(serializers.ModelSerializer):
    """Registration serializer."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'first_name', 'last_name', 'phone')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        # إنشاء مستخدم جديد مع تعيين البيانات الأساسية
        user = User.objects.create_user(**validated_data)
        return user

class ForgotPasswordSerializer(serializers.Serializer):
    """Forgot password serializer."""
    email = serializers.EmailField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    """Reset password serializer."""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    تخصيص التوكن (JWT) ليشمل بيانات الصلاحيات فور تسجيل الدخول.
    هذا يضمن أن التطبيق سيعرف أن المستخدم أدمن بمجرد استلام التوكن.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # إضافة بيانات المستخدم الإضافية داخل التوكن
        token['email'] = user.email
        token['role'] = user.role
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        token['full_name'] = user.full_name
        
        return token