import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from vehicles.models import Vehicle
from .models import VehicleLocation
from planning.models import VehicleUserPermission


class LiveTrackingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for live vehicle tracking."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.vehicle_id = None
        self.user = None
        self.vehicle = None
        self.stream_task = None
        
        # Get vehicle_id from query string
        vehicle_id = self.scope.get('query_string', b'').decode().split('vehicle_id=')[-1].split('&')[0]
        
        if not vehicle_id:
            await self.close(code=4000)  # Invalid request
            return
        
        try:
            self.vehicle_id = int(vehicle_id)
        except ValueError:
            await self.close(code=4000)
            return
        
        # Get user from scope (set by JWT middleware)
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)  # Unauthorized
            return
        
        # Get vehicle and check permissions
        self.vehicle = await self.get_vehicle(self.vehicle_id)
        if not self.vehicle:
            await self.close(code=4004)  # Not found
            return
        
        # Check permissions
        has_permission = await self.check_permission(self.user, self.vehicle)
        if not has_permission:
            await self.close(code=4003)  # Forbidden
            return
        
        # Accept connection
        await self.accept()
        
        # Start streaming if vehicle is set to stream
        if self.vehicle.is_streaming:
            self.stream_task = asyncio.create_task(self.stream_locations())
        else:
            # Send status message
            await self.send(text_data=json.dumps({
                'type': 'status',
                'message': 'Streaming is paused. Use start endpoint to begin.',
                'streaming': False
            }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if self.stream_task:
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
    
    
    @database_sync_to_async
    def get_vehicle(self, vehicle_id):
        """Get vehicle by ID."""
        try:
            return Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return None
    
    @database_sync_to_async
    def check_permission(self, user, vehicle):
        """Check if user has permission to track vehicle."""
        # Admin always has permission
        if user.role == 'ADMIN':
            return True
        
        # Check VehicleUserPermission
        return VehicleUserPermission.objects.filter(
            user=user,
            vehicle=vehicle
        ).exists()
    
    async def stream_locations(self):
        """Stream location updates every 1-2 seconds."""
        route = await database_sync_to_async(self.vehicle.get_simulation_route)()
        
        if not route or len(route) < 2:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'No simulation route available'
            }))
            return
        
        # Interpolate between route points
        current_index = 0
        progress = 0.0  # Progress between current and next point (0.0 to 1.0)
        points_per_segment = 10  # Number of interpolated points between route points
        
        while True:
            # Check if streaming is still enabled
            await asyncio.sleep(0.1)  # Small delay to prevent tight loop
            vehicle = await database_sync_to_async(Vehicle.objects.get)(id=self.vehicle_id)
            if not vehicle.is_streaming:
                await self.send(text_data=json.dumps({
                    'type': 'status',
                    'message': 'Streaming paused',
                    'streaming': False
                }))
                # Wait until streaming resumes
                while not vehicle.is_streaming:
                    await asyncio.sleep(1)
                    vehicle = await database_sync_to_async(Vehicle.objects.get)(id=self.vehicle_id)
                await self.send(text_data=json.dumps({
                    'type': 'status',
                    'message': 'Streaming resumed',
                    'streaming': True
                }))
            
            # Calculate current position
            start_point = route[current_index]
            end_point = route[(current_index + 1) % len(route)]
            
            # Interpolate
            lat = start_point[0] + (end_point[0] - start_point[0]) * progress
            lng = start_point[1] + (end_point[1] - start_point[1]) * progress
            
            # Calculate speed and heading
            if progress > 0:
                prev_lat = start_point[0] + (end_point[0] - start_point[0]) * max(0, progress - 0.1)
                prev_lng = start_point[1] + (end_point[1] - start_point[1]) * max(0, progress - 0.1)
                
                # Calculate distance (simplified)
                import math
                lat_diff = lat - prev_lat
                lng_diff = lng - prev_lng
                distance = math.sqrt(lat_diff**2 + lng_diff**2) * 111000  # Approximate meters
                speed = distance / 1.5  # m/s (assuming 1.5s interval)
                
                # Calculate heading (degrees from north)
                heading = math.degrees(math.atan2(lng_diff, lat_diff))
                if heading < 0:
                    heading += 360
            else:
                speed = 0.0
                heading = 0.0
            
            # Create location data
            location_data = {
                'type': 'location',
                'vehicle_id': self.vehicle_id,
                'lat': round(lat, 6),
                'lng': round(lng, 6),
                'speed': round(speed, 2),
                'heading': round(heading, 2),
                'recorded_at': timezone.now().isoformat(),
                'source': 'SIMULATED'
            }
            
            # Send to WebSocket
            await self.send(text_data=json.dumps(location_data))
            
            # Save to database
            await self.save_location(lat, lng, speed, heading)
            
            # Update progress
            progress += 1.0 / points_per_segment
            if progress >= 1.0:
                progress = 0.0
                current_index = (current_index + 1) % len(route)
            
            # Wait 1-2 seconds (randomized)
            import random
            await asyncio.sleep(random.uniform(1.0, 2.0))
    
    @database_sync_to_async
    def save_location(self, lat, lng, speed, heading):
        """Save location to database."""
        VehicleLocation.objects.create(
            vehicle=self.vehicle,
            lat=lat,
            lng=lng,
            speed=speed,
            heading=heading,
            recorded_at=timezone.now(),
            source=VehicleLocation.Source.SIMULATED
        )

