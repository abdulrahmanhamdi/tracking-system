from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle

User = get_user_model()


class Personnel(models.Model):
    """Personnel model."""
    full_name = models.CharField(max_length=200)
    title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ['full_name']
        verbose_name_plural = 'Personnel'

    def __str__(self):
        return self.full_name


class Plan(models.Model):
    """Plan model."""
    
    class Status(models.TextChoices):
        PLANNED = 'PLANNED', 'Planned'
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELED = 'CANCELED', 'Canceled'

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='plans')
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='plans')
    # إضافة حقل المستخدم الذي أنشأ الخطة
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_plans',
        null=True, 
        blank=True
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vehicle', '-start_at']),
            models.Index(fields=['personnel', '-start_at']),
            models.Index(fields=['status', '-start_at']),
        ]

    def __str__(self):
        return f"Plan for {self.vehicle.plate} - {self.start_at}"

    def clean(self):
        """Validate plan data."""
        super().clean()
        if self.start_at and self.end_at:
            if self.start_at >= self.end_at:
                raise ValidationError({'end_at': 'End time must be after start time'})
        
        # Check for plan conflicts
        self._check_plan_conflicts()

    def _check_plan_conflicts(self):
        """Check for plan conflicts with overlapping time ranges for the same vehicle.
        
        Overlap logic: (startA < endB) and (endA > startB)
        """
        if not self.start_at or not self.end_at or not self.vehicle_id:
            return
        
        # Find overlapping plans for the same vehicle
        # Exclude canceled and completed plans (they don't conflict)
        # Exclude self if updating
        overlapping_query = Plan.objects.filter(
            vehicle=self.vehicle,
            status__in=[Plan.Status.PLANNED, Plan.Status.ACTIVE]
        ).filter(
            start_at__lt=self.end_at,  # startA < endB
            end_at__gt=self.start_at   # endA > startB
        )
        
        # Exclude self if this is an update
        if self.pk:
            overlapping_query = overlapping_query.exclude(pk=self.pk)
        
        overlapping_plans = overlapping_query
        
        if overlapping_plans.exists():
            conflicting_plan = overlapping_plans.first()
            raise ValidationError({
                'start_at': f'This plan overlaps with an existing plan for vehicle {self.vehicle.plate} '
                           f'({conflicting_plan.start_at} - {conflicting_plan.end_at}). '
                           f'Please choose a different time range.',
                'end_at': f'This plan overlaps with an existing plan for vehicle {self.vehicle.plate} '
                         f'({conflicting_plan.start_at} - {conflicting_plan.end_at}). '
                         f'Please choose a different time range.'
            })

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)


class VehicleUserPermission(models.Model):
    """Vehicle user permission model."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicle_permissions')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='user_permissions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'vehicle']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['vehicle', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.vehicle.plate}"