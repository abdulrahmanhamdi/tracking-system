from django.contrib import admin
from .models import Personnel, Plan, VehicleUserPermission


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'title', 'phone', 'email')
    search_fields = ('full_name', 'title', 'phone', 'email')
    ordering = ('full_name',)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'personnel', 'start_at', 'end_at', 'status', 'created_at')
    list_filter = ('status', 'start_at', 'end_at', 'created_at')
    search_fields = ('vehicle__plate', 'personnel__full_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'start_at'
    fieldsets = (
        ('Plan Details', {
            'fields': ('vehicle', 'personnel', 'status')
        }),
        ('Schedule', {
            'fields': ('start_at', 'end_at')
        }),
        ('Additional Information', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VehicleUserPermission)
class VehicleUserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'vehicle__plate')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
