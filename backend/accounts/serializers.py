from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'phone', 'role', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at', 'role')


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
    Custom JWT Token serializer to include extra user info in the token.
    This fixes the ImportError in views.py.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        
        return token