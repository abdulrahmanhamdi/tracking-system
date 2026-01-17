from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    صلاحية تسمح للمسؤولين (ADMIN) أو الـ Superuser أو الـ Staff بالوصول.
    يتم استخدامها في العمليات الحساسة مثل الإضافة والحذف الكلي.
    """
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        
        # التحقق من الصلاحيات الإدارية بكافة أشكالها لضمان الوصول
        is_admin = (
            user.is_superuser or 
            user.is_staff or 
            getattr(user, 'role', '').upper() == 'ADMIN'
        )
        return is_admin

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    تسمح بالقراءة لجميع المستخدمين المسجلين، 
    ولكن عمليات الكتابة (إضافة، تعديل، حذف) محصورة بالمسؤولين فقط.
    """
    def has_permission(self, request, view):
        # السماح بالقراءة (GET, HEAD, OPTIONS) لأي مستخدم مسجل
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        
        # العمليات الأخرى تتطلب صلاحيات مسؤول
        user = request.user
        if not (user and user.is_authenticated):
            return False
            
        is_admin = (
            user.is_superuser or 
            user.is_staff or 
            getattr(user, 'role', '').upper() == 'ADMIN'
        )
        return is_admin

class VehicleAccessPermission(permissions.BasePermission):
    """
    صلاحية مخصصة للمركبات:
    - تسمح لجميع المستخدمين المسجلين بعرض القائمة (GET).
    - تمنع الإضافة والتعديل والحذف لغير المسؤولين.
    """
    def has_permission(self, request, view):
        # التحقق من أن المستخدم مسجل دخول أولاً
        user = request.user
        if not (user and user.is_authenticated):
            return False
        
        # السماح بالقراءة لجميع المسجلين
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # أي عملية تغيير تتطلب صلاحيات مسؤول
        is_admin = (
            user.is_superuser or 
            user.is_staff or 
            getattr(user, 'role', '').upper() == 'ADMIN'
        )
        return is_admin

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # المسؤول لديه صلاحية كاملة على أي كائن مركبة
        is_admin = (
            user.is_superuser or 
            user.is_staff or 
            getattr(user, 'role', '').upper() == 'ADMIN'
        )
        if is_admin:
            return True
        
        # المستخدم العادي لديه صلاحية القراءة فقط للمركبات التي تظهر له
        return request.method in permissions.SAFE_METHODS

class PlanAccessPermission(permissions.BasePermission):
    """
    صلاحية الوصول للخطط:
    - المسؤول يدير كل الخطط.
    - المستخدم العادي يدير الخطط التي أنشأها فقط ويشاهد البقية.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # الأدمن لديه صلاحية مطلقة
        is_admin = (
            user.is_superuser or 
            user.is_staff or 
            getattr(user, 'role', '').upper() == 'ADMIN'
        )
        if is_admin:
            return True
        
        # السماح للمالك فقط بالتعديل أو الحذف
        if hasattr(obj, 'created_by') and obj.created_by == user:
            return True
            
        # الآخرون يمكنهم القراءة فقط
        return request.method in permissions.SAFE_METHODS