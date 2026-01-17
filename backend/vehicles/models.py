from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
import json
import math

class Vehicle(models.Model):
    """Vehicle model."""
    
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'

    # الحقل الذي تم إضافته لربط السيارة بالمستخدم
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='vehicles',
        null=True,   
        blank=True,
        help_text="The user who owns or manages this vehicle"
    )

    plate = models.CharField(max_length=20, unique=True, db_index=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    simulation_route = models.JSONField(default=list, blank=True, help_text="List of [lat, lng] coordinates for simulation")
    is_streaming = models.BooleanField(default=False, help_text="Whether live tracking is currently streaming")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['plate']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.brand} {self.model} - {self.plate}"

    def clean(self):
        """Validate vehicle data."""
        super().clean()
        if self.year and (self.year < 1900 or self.year > 2100):
            raise ValidationError({'year': 'Year must be between 1900 and 2100'})
        
        # التأكد من صحة تنسيق مسار المحاكاة
        if self.simulation_route:
            if not isinstance(self.simulation_route, list):
                raise ValidationError({'simulation_route': 'Simulation route must be a list'})
            for point in self.simulation_route:
                if not isinstance(point, list) or len(point) != 2:
                    raise ValidationError({'simulation_route': 'Each route point must be [lat, lng]'})
                if not isinstance(point[0], (int, float)) or not isinstance(point[1], (int, float)):
                    raise ValidationError({'simulation_route': 'Coordinates must be numbers'})

    def get_simulation_route(self):
        """Get simulation route or generate default circular route around Istanbul."""
        if self.simulation_route and len(self.simulation_route) > 0:
            return self.simulation_route
        
        # تم تعديل الإحداثيات الافتراضية لتكون في إسطنبول بدلاً من نيويورك
        base_lat = 41.0082  # Istanbul (Sultanahmet)
        base_lng = 28.9784
        radius = 0.01  # ~1km radius
        
        # توليد 8 نقاط في مسار دائري
        route = []
        for i in range(8):
            angle = (2 * math.pi * i) / 8
            lat = base_lat + radius * math.cos(angle)
            lng = base_lng + radius * math.sin(angle)
            route.append([round(lat, 6), round(lng, 6)])
        
        return route