from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'role', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'username', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'username', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'expires_at', 'used_at', 'is_valid_display', 'created_at')
    list_filter = ('expires_at', 'used_at', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'token_hash')
    readonly_fields = ('token_hash', 'created_at')
    ordering = ('-created_at',)

    def is_valid_display(self, obj):
        """Display if token is valid."""
        return obj.is_valid()
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Is Valid'
