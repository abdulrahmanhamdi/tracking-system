from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    forgot_password_view,
    reset_password_view,
    logout_view,
    admin_users_list_view,   
    admin_users_update_view  
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset-password/', reset_password_view, name='reset_password'),
    path('logout/', logout_view, name='logout'),
    path('admin/users/', admin_users_list_view, name='admin_users_list'),
    path('admin/users/<int:user_id>/', admin_users_update_view, name='admin_users_update'),
]
