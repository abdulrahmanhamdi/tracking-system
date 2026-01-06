from django.db import models
from django.core.exceptions import ValidationError
from vehicles.models import Vehicle


class VehicleLocation(models.Model):
    """Vehicle location tracking model."""
    
    class Source(models.TextChoices):
        SIMULATED = 'SIMULATED', 'Simulated'
        REAL = 'REAL', 'Real'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='locations')
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.FloatField(null=True, blank=True)
    heading = models.FloatField(null=True, blank=True)
    recorded_at = models.DateTimeField(db_index=True)
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.REAL)
    
    def save(self, *args, **kwargs):
        """Set recorded_at to now if not provided."""
        if not self.recorded_at:
            from django.utils import timezone
            self.recorded_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['vehicle', '-recorded_at']),
            models.Index(fields=['recorded_at']),
        ]

    def __str__(self):
        return f"{self.vehicle.plate} - {self.recorded_at}"

    def clean(self):
        """Validate location data."""
        super().clean()
        if self.lat < -90 or self.lat > 90:
            raise ValidationError({'lat': 'Latitude must be between -90 and 90'})
        if self.lng < -180 or self.lng > 180:
            raise ValidationError({'lng': 'Longitude must be between -180 and 180'})
        if self.speed is not None and self.speed < 0:
            raise ValidationError({'speed': 'Speed cannot be negative'})
        if self.heading is not None:
            if self.heading < 0 or self.heading >= 360:
                raise ValidationError({'heading': 'Heading must be between 0 and 360 degrees'})
