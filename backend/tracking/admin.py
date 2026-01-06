from django.contrib import admin
from .models import VehicleLocation


@admin.register(VehicleLocation)
class VehicleLocationAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'lat', 'lng', 'speed', 'heading', 'source', 'recorded_at')
    list_filter = ('source', 'recorded_at', 'vehicle')
    search_fields = ('vehicle__plate', 'vehicle__brand', 'vehicle__model')
    readonly_fields = ('recorded_at',)
    ordering = ('-recorded_at',)
    date_hierarchy = 'recorded_at'
