from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate', 'brand', 'model', 'year', 'status', 'is_streaming', 'created_at')
    list_filter = ('status', 'is_streaming', 'brand', 'year', 'created_at')
    search_fields = ('plate', 'brand', 'model', 'year')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('plate', 'brand', 'model', 'year', 'status')
        }),
        ('Live Tracking', {
            'fields': ('is_streaming', 'simulation_route')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
