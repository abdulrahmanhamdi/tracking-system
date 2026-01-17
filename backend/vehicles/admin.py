from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # إضافة 'owner' إلى قائمة العرض لمشاهدة مالك كل سيارة
    list_display = ('plate', 'brand', 'model', 'year', 'status', 'owner', 'is_streaming', 'created_at')
    
    # إضافة 'owner' للفلاتر لتسهيل البحث عن سيارات مستخدم معين
    list_filter = ('status', 'owner', 'is_streaming', 'brand', 'year', 'created_at')
    
    search_fields = ('plate', 'brand', 'model', 'year')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Vehicle Information', {
            # تم إضافة حقل 'owner' هنا لكي تتمكن من اختياره عند إضافة سيارة جديدة
            'fields': ('owner', 'plate', 'brand', 'model', 'year', 'status')
        }),
        ('Live Tracking', {
            'fields': ('is_streaming', 'simulation_route')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )