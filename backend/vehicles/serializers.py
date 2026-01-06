from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    """Vehicle serializer."""
    class Meta:
        model = Vehicle
        fields = ('id', 'plate', 'brand', 'model', 'year', 'status', 'created_at')
        read_only_fields = ('id', 'created_at')
