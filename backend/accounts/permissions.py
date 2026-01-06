from rest_framework import permissions
from .models import User
from vehicles.models import Vehicle
from planning.models import VehicleUserPermission


class IsAdminRole(permissions.BasePermission):
    """Permission to check if user has ADMIN role."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.ADMIN
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission to allow read-only for all authenticated users, write for admins only."""
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed for admins
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.ADMIN
        )


class VehicleAccessPermission(permissions.BasePermission):
    """Permission to check if user can access a vehicle."""
    
    def has_permission(self, request, view):
        # Must be authenticated
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admins can access all vehicles
        if request.user.role == User.Role.ADMIN:
            return True
        
        # For read operations, check if user has permission
        if request.method in permissions.SAFE_METHODS:
            return True  # Will check object-level permission
        
        # For write operations, only admins
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permission."""
        # Admins can access all vehicles
        if request.user.role == User.Role.ADMIN:
            return True
        
        # Users can only access vehicles they have permission for
        if isinstance(obj, Vehicle):
            return VehicleUserPermission.objects.filter(
                user=request.user,
                vehicle=obj
            ).exists()
        
        # For VehicleLocation, check the vehicle
        if hasattr(obj, 'vehicle'):
            return VehicleUserPermission.objects.filter(
                user=request.user,
                vehicle=obj.vehicle
            ).exists()
        
        return False


class PlanAccessPermission(permissions.BasePermission):
    """Permission to check if user can access a plan."""
    
    def has_permission(self, request, view):
        # Must be authenticated
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admins can access all plans
        if request.user.role == User.Role.ADMIN:
            return True
        
        # Users can view plans (read-only)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Users cannot create/modify plans (only admins)
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permission."""
        # Admins can access all plans
        if request.user.role == User.Role.ADMIN:
            return True
        
        # Users can only view plans (read-only)
        return request.method in permissions.SAFE_METHODS

