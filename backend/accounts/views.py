from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from .models import PasswordResetToken
from .permissions import IsAdminRole
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': 'User registered successfully',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Return a generic message to prevent email enumeration
        return Response({'message': 'If an account with that email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)

    # Generate token
    token = PasswordResetToken.generate_token()
    token_hash = PasswordResetToken.hash_token(token)
    expires_at = timezone.now() + timedelta(minutes=30)

    # Invalidate any existing tokens for this user
    PasswordResetToken.objects.filter(user=user, used_at__isnull=True, expires_at__gt=timezone.now()).update(used_at=timezone.now())

    PasswordResetToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=expires_at
    )

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}&email={user.email}"
    logger.info(f"Password reset link for {user.email}: {reset_link}")

    return Response({'message': 'If an account with that email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    serializer = request.data
    token = serializer.get('token')
    new_password = serializer.get('new_password')
    email = serializer.get('email')

    if not all([token, new_password, email]):
        return Response({'error': 'Token, new_password, and email are required.'}, status=status.HTTP_400_BAD_REQUEST)

    token_hash = PasswordResetToken.hash_token(token)

    try:
        reset_token = PasswordResetToken.objects.get(token_hash=token_hash, user__email=email)
    except PasswordResetToken.DoesNotExist:
        return Response({'error': 'Invalid or expired reset token.'}, status=status.HTTP_400_BAD_REQUEST)

    if not reset_token.is_valid():
        return Response({'error': 'Invalid or expired reset token.'}, status=status.HTTP_400_BAD_REQUEST)

    user = reset_token.user
    user.set_password(new_password)
    user.save()

    reset_token.used_at = timezone.now()
    reset_token.save()

    return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_users_list_view(request):
    """Admin endpoint for listing users."""
    users = User.objects.all().order_by('-created_at')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminRole])
def admin_users_update_view(request, user_id):
    """Admin endpoint for updating user role and is_active."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update role and is_active
    role = request.data.get('role')
    is_active = request.data.get('is_active')
    
    if role:
        if role in [User.Role.ADMIN, User.Role.USER]:
            user.role = role
        else:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
    
    if is_active is not None:
        user.is_active = bool(is_active)
    
    user.save()
    serializer = UserSerializer(user)
    return Response(serializer.data)
