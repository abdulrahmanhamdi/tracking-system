from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Max
from .models import VehicleLocation
from .serializers import VehicleLocationSerializer
from accounts.permissions import VehicleAccessPermission, IsAdminRole
from vehicles.models import Vehicle


class VehicleLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """Vehicle location viewset."""
    queryset = VehicleLocation.objects.all()
    serializer_class = VehicleLocationSerializer
    permission_classes = [VehicleAccessPermission]

    def get_queryset(self):
        """Filter locations based on user vehicle permissions."""
        user = self.request.user
        
        # Admins can see all locations
        if user.role == 'ADMIN':
            queryset = VehicleLocation.objects.all()
        else:
            # Users can only see locations for vehicles they have permission for
            from planning.models import VehicleUserPermission
            permitted_vehicles = VehicleUserPermission.objects.filter(
                user=user
            ).values_list('vehicle_id', flat=True)
            queryset = VehicleLocation.objects.filter(vehicle_id__in=permitted_vehicles)
        
        # Apply date range filters
        from_date = self.request.query_params.get('from', None)
        to_date = self.request.query_params.get('to', None)
        
        if from_date:
            try:
                from_datetime = parse_datetime(from_date)
                if from_datetime:
                    queryset = queryset.filter(recorded_at__gte=from_datetime)
            except (ValueError, TypeError):
                pass
        
        if to_date:
            try:
                to_datetime = parse_datetime(to_date)
                if to_datetime:
                    queryset = queryset.filter(recorded_at__lte=to_datetime)
            except (ValueError, TypeError):
                pass
        
        return queryset.order_by('-recorded_at')


class VehicleLocationNestedViewSet(viewsets.ReadOnlyModelViewSet):
    """Nested vehicle location viewset for specific vehicle."""
    serializer_class = VehicleLocationSerializer
    permission_classes = [VehicleAccessPermission]
    lookup_field = 'id'

    def get_queryset(self):
        """Get locations for a specific vehicle."""
        vehicle_id = self.kwargs.get('vehicle_pk')
        
        if not vehicle_id:
            return VehicleLocation.objects.none()
        
        # Check if user has permission to access this vehicle
        user = self.request.user
        
        if user.role != 'ADMIN':
            from planning.models import VehicleUserPermission
            has_permission = VehicleUserPermission.objects.filter(
                user=user,
                vehicle_id=vehicle_id
            ).exists()
            if not has_permission:
                return VehicleLocation.objects.none()
        
        queryset = VehicleLocation.objects.filter(vehicle_id=vehicle_id)
        
        # Apply date range filters
        from_date = self.request.query_params.get('from', None)
        to_date = self.request.query_params.get('to', None)
        
        if from_date:
            try:
                from_datetime = parse_datetime(from_date)
                if from_datetime:
                    queryset = queryset.filter(recorded_at__gte=from_datetime)
            except (ValueError, TypeError):
                pass
        
        if to_date:
            try:
                to_datetime = parse_datetime(to_date)
                if to_datetime:
                    queryset = queryset.filter(recorded_at__lte=to_datetime)
            except (ValueError, TypeError):
                pass
        
        return queryset.order_by('-recorded_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def last_locations_view(request):
    """Get last known location for each permitted vehicle."""
    from .serializers import VehicleLocationSerializer
    from vehicles.serializers import VehicleSerializer
    
    user = request.user
    
    # Get permitted vehicles
    if user.role == 'ADMIN':
        vehicles = Vehicle.objects.all()
    else:
        from planning.models import VehicleUserPermission
        permitted_vehicle_ids = VehicleUserPermission.objects.filter(
            user=user
        ).values_list('vehicle_id', flat=True)
        vehicles = Vehicle.objects.filter(id__in=permitted_vehicle_ids)
    
    # Get last location for each vehicle
    last_locations = []
    for vehicle in vehicles:
        last_location = VehicleLocation.objects.filter(
            vehicle=vehicle
        ).order_by('-recorded_at').first()
        
        if last_location:
            serializer = VehicleLocationSerializer(last_location)
            last_locations.append(serializer.data)
        else:
            # Include vehicle info even if no location exists
            vehicle_data = VehicleSerializer(vehicle).data
            last_locations.append({
                **vehicle_data,
                'lat': None,
                'lng': None,
                'speed': None,
                'heading': None,
                'recorded_at': None,
                'source': None
            })
    
    return Response(last_locations)


@api_view(['PUT'])
@permission_classes([IsAdminRole])
def set_simulation_route(request, vehicle_id):
    """Set simulation route for a vehicle (admin only)."""
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return Response(
            {'error': 'Vehicle not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    route = request.data.get('route', [])
    
    # Validate route format
    if not isinstance(route, list):
        return Response(
            {'error': 'Route must be a list of [lat, lng] coordinates'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    for point in route:
        if not isinstance(point, list) or len(point) != 2:
            return Response(
                {'error': 'Each route point must be [lat, lng]'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(point[0], (int, float)) or not isinstance(point[1], (int, float)):
            return Response(
                {'error': 'Coordinates must be numbers'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    vehicle.simulation_route = route
    vehicle.save()
    
    return Response({
        'message': 'Simulation route updated',
        'vehicle_id': vehicle_id,
        'route': route
    })


@api_view(['POST'])
@permission_classes([IsAdminRole])
def start_streaming(request, vehicle_id):
    """Start live tracking stream for a vehicle (admin only)."""
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return Response(
            {'error': 'Vehicle not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    vehicle.is_streaming = True
    vehicle.save()
    
    return Response({
        'message': 'Streaming started',
        'vehicle_id': vehicle_id,
        'streaming': True
    })


@api_view(['POST'])
@permission_classes([IsAdminRole])
def stop_streaming(request, vehicle_id):
    """Stop live tracking stream for a vehicle (admin only)."""
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return Response(
            {'error': 'Vehicle not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    vehicle.is_streaming = False
    vehicle.save()
    
    return Response({
        'message': 'Streaming stopped',
        'vehicle_id': vehicle_id,
        'streaming': False
    })
