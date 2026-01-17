import json
import asyncio
import math
import random
from datetime import timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from vehicles.models import Vehicle
from .models import VehicleLocation
from planning.models import Plan, VehicleUserPermission

class LiveTrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer لتعقب المركبات حياً مع تفعيل الخطط تلقائياً والتحقق من الصلاحيات.
    """

    async def connect(self):
        """التعامل مع اتصال WebSocket والتحقق من الصلاحيات والخطط."""
        self.vehicle_id = None
        self.user = None
        self.vehicle = None
        self.stream_task = None
        
        # استخراج المعاملات من Query String
        query_string = self.scope.get('query_string', b'').decode()
        params = dict(x.split('=') for x in query_string.split('&') if '=' in x)
        vehicle_id = params.get('vehicle_id')
        
        if not vehicle_id:
            await self.close(code=4000)
            return
        
        try:
            self.vehicle_id = int(vehicle_id)
        except ValueError:
            await self.close(code=4000)
            return
        
        # الحصول على المستخدم والتحقق من هويته
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # جلب بيانات السيارة
        self.vehicle = await self.get_vehicle(self.vehicle_id)
        if not self.vehicle:
            await self.close(code=4004)
            return
        
        # 1. التحقق من الصلاحيات وتفعيل الخطة تلقائياً
        self.active_plan = await self.get_and_activate_plan()
        
        # السماح للآدمن بالتتبع دائماً، أما المستخدم العادي فيحتاج لخطة نشطة وصلاحية
        if self.user.role != 'ADMIN' and not self.active_plan:
            await self.close(code=4003)  
            return
        
        # قبول الاتصال
        await self.accept()
        
        # بدء مهمة بث المواقع
        self.stream_task = asyncio.create_task(self.stream_locations())

    async def disconnect(self, close_code):
        """تنظيف المهام عند قطع الاتصال."""
        if self.stream_task:
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass

    @database_sync_to_async
    def get_vehicle(self, vehicle_id):
        try:
            return Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return None

    @database_sync_to_async
    def get_and_activate_plan(self):
        """
        البحث عن خطة متاحة للمستخدم وتفعيلها (ACTIVE) إذا كان الوقت مناسباً.
        """
        now = timezone.now()
        buffer_time = timedelta(minutes=15)
        
        # التحقق أولاً من وجود صلاحية للمستخدم على هذه السيارة
        has_permission = VehicleUserPermission.objects.filter(
            user=self.user, 
            vehicle_id=self.vehicle_id
        ).exists()
        
        if not has_permission and self.user.role != 'ADMIN':
            return None

        # البحث عن خطة (PLANNED أو ACTIVE) ضمن النافذة الزمنية
        plan = Plan.objects.filter(
            vehicle_id=self.vehicle_id,
            start_at__lte=now + buffer_time,
            end_at__gte=now - buffer_time,
            status__in=['PLANNED', 'ACTIVE']
        ).first()

        # إذا كانت الخطة موجودة ولكنها PLANNED، يتم تفعيلها فوراً
        if plan and plan.status == 'PLANNED':
            plan.status = 'ACTIVE'
            plan.save()
            
        return plan

    async def stream_locations(self):
        """بث تحديثات الموقع الوهمية."""
        route = await database_sync_to_async(self.vehicle.get_simulation_route)()
        
        if not route or len(route) < 2:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'No simulation route found.'
            }))
            return
        
        current_index = 0
        progress = 0.0
        
        while True:
            # تحديث بيانات السيارة لفحص مفتاح البث
            vehicle_obj = await database_sync_to_async(Vehicle.objects.get)(id=self.vehicle_id)
            
            if not vehicle_obj.is_streaming:
                await self.send(text_data=json.dumps({
                    'type': 'status',
                    'message': 'Simulation Paused',
                    'streaming': False
                }))
                await asyncio.sleep(5)
                continue

            # التحقق من استمرار صلاحية الوقت (لغير الآدمن)
            if self.user.role != 'ADMIN':
                is_valid = await self.get_and_activate_plan()
                if not is_valid:
                    await self.send(text_data=json.dumps({
                        'type': 'status',
                        'message': 'Plan expired',
                        'streaming': False
                    }))
                    await self.close(code=4003)
                    break

            # حساب الموقع (بقية المنطق الخاص بك صحيحة)
            start_point = route[current_index]
            end_point = route[(current_index + 1) % len(route)]
            
            lat = start_point[0] + (end_point[0] - start_point[0]) * progress
            lng = start_point[1] + (end_point[1] - start_point[1]) * progress
            
            location_data = {
                'type': 'location',
                'vehicle_id': self.vehicle_id,
                'lat': round(lat, 6),
                'lng': round(lng, 6),
                'speed': round(45.0 + random.uniform(-5, 5), 2),
                'recorded_at': timezone.now().isoformat()
            }
            
            await self.send(text_data=json.dumps(location_data))
            await self.save_location(lat, lng)
            
            progress += 0.1
            if progress >= 1.0:
                progress = 0.0
                current_index = (current_index + 1) % len(route)
            
            await asyncio.sleep(2)

    @database_sync_to_async
    def save_location(self, lat, lng):
        VehicleLocation.objects.create(
            vehicle=self.vehicle,
            lat=lat,
            lng=lng,
            speed=45.0,
            recorded_at=timezone.now(),
            source='SIMULATED'
        )