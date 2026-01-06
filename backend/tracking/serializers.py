from rest_framework import serializers
from .models import VehicleLocation
from vehicles.serializers import VehicleSerializer


class VehicleLocationSerializer(serializers.ModelSerializer):
    """Vehicle location serializer."""
    vehicle_info = VehicleSerializer(source='vehicle', read_only=True)

    class Meta:
        model = VehicleLocation
        fields = ('id', 'vehicle', 'vehicle_info', 'lat', 'lng', 'speed', 'heading', 'recorded_at', 'source')
        read_only_fields = ('id',)
