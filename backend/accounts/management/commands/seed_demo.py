"""
Django management command to seed demo data.
Full version - Detailed coordinates and logic for mu.alhardan@gmail.com
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle
from planning.models import Personnel, Plan, VehicleUserPermission
from django.utils import timezone
from datetime import timedelta
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo data for development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to seed demo data...'))

        # ------------------------------------------------------------------
        # 1. Cleanup Section (Important for re-runs)
        # ------------------------------------------------------------------
        self.stdout.write(self.style.WARNING('Cleaning up existing plans and permissions to avoid conflicts...'))
        Plan.objects.all().delete()
        VehicleUserPermission.objects.all().delete()

        # ------------------------------------------------------------------
        # 2. Users Section
        # ------------------------------------------------------------------
        # Admin User
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('Admin1234!')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin user already exists: {admin_user.email}'))

        # Normal User (Linked to your account for Live Tracking)
        normal_user, created = User.objects.get_or_create(
            email='mu.alhardan@gmail.com',
            defaults={
                'username': 'mu_alhardan',
                'first_name': 'Mu',
                'last_name': 'Alhardan',
                'role': User.Role.USER,
            }
        )
        if created:
            normal_user.set_password('User1234!')
            normal_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created normal user: {normal_user.email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Normal user already exists: {normal_user.email}'))

        # ------------------------------------------------------------------
        # 3. Vehicles Section (Full Coordinates Mapping)
        # ------------------------------------------------------------------
        vehicles_data = [
            {
                'plate': 'ABC-123',
                'brand': 'Toyota',
                'model': 'Camry',
                'year': 2020,
                'status': Vehicle.Status.ACTIVE,
                'is_streaming': True,
                'simulation_route': [
                    [41.0082, 28.9784],
                    [41.0122, 28.9844],
                    [41.0150, 28.9790],
                    [41.0200, 28.9700],
                    [41.0150, 28.9790],
                    [41.0122, 28.9844],
                    [41.0082, 28.9784],
                ]
            },
            {
                'plate': 'XYZ-789',
                'brand': 'Honda',
                'model': 'Civic',
                'year': 2021,
                'status': Vehicle.Status.ACTIVE,
                'is_streaming': True,
                'simulation_route': [
                    [41.0367, 28.9850],
                    [41.0400, 28.9900],
                    [41.0450, 28.9950],
                    [41.0480, 29.0000],
                    [41.0450, 28.9950],
                    [41.0400, 28.9900],
                    [41.0367, 28.9850],
                ]
            },
            {
                'plate': 'DEF-456',
                'brand': 'Ford',
                'model': 'F-150',
                'year': 2019,
                'status': Vehicle.Status.ACTIVE,
                'is_streaming': True,
                'simulation_route': [
                    [41.0000, 28.9000],
                    [41.0010, 28.9010],
                    [41.0020, 28.9020],
                    [41.0030, 28.9030],
                    [41.0040, 28.9040],
                    [41.0020, 28.9020],
                    [41.0000, 28.9000],
                ]
            },
            {
                'plate': 'GHI-321',
                'brand': 'Tesla',
                'model': 'Model 3',
                'year': 2022,
                'status': Vehicle.Status.ACTIVE,
                'is_streaming': True,
                'simulation_route': [
                    [40.9900, 29.0200],
                    [40.9920, 29.0220],
                    [40.9950, 29.0250],
                    [41.0000, 29.0300],
                    [40.9950, 29.0250],
                    [40.9920, 29.0220],
                    [40.9900, 29.0200],
                ]
            },
            {
                'plate': 'JKL-654',
                'brand': 'BMW',
                'model': 'X5',
                'year': 2021,
                'status': Vehicle.Status.MAINTENANCE,
                'is_streaming': False,
                'simulation_route': [
                    [41.0600, 29.0100],
                    [41.0620, 29.0120],
                    [41.0650, 29.0150],
                    [41.0700, 29.0200],
                    [41.0650, 29.0150],
                    [41.0620, 29.0120],
                    [41.0600, 29.0100],
                ]
            },
        ]

        vehicles_list = []
        for v_data in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                plate=v_data['plate'],
                defaults={
                    'owner': admin_user,
                    'brand': v_data['brand'],
                    'model': v_data['model'],
                    'year': v_data['year'],
                    'status': v_data['status'],
                    'is_streaming': v_data['is_streaming'],
                    'simulation_route': v_data['simulation_route'],
                }
            )
            if not created:
                vehicle.is_streaming = v_data['is_streaming']
                vehicle.simulation_route = v_data['simulation_route']
                vehicle.status = v_data['status']
                vehicle.save()
            vehicles_list.append(vehicle)

        # ------------------------------------------------------------------
        # 4. Personnel Section
        # ------------------------------------------------------------------
        personnel_data = [
            {'full_name': 'John Doe', 'title': 'Driver', 'phone': '555-0101', 'email': 'john@example.com'},
            {'full_name': 'Jane Smith', 'title': 'Driver', 'phone': '555-0102', 'email': 'jane@example.com'},
            {'full_name': 'Bob Johnson', 'title': 'Supervisor', 'phone': '555-0103', 'email': 'bob@example.com'},
            {'full_name': 'Alice Williams', 'title': 'Driver', 'phone': '555-0104', 'email': 'alice@example.com'},
            {'full_name': 'Charlie Brown', 'title': 'Manager', 'phone': '555-0105', 'email': 'charlie@example.com'},
        ]

        personnel_objs = []
        for p_data in personnel_data:
            person, created = Personnel.objects.get_or_create(
                email=p_data['email'],
                defaults=p_data
            )
            personnel_objs.append(person)

        # ------------------------------------------------------------------
        # 5. Permissions Section (Linking vehicles to your mu account)
        # ------------------------------------------------------------------
        for vehicle in vehicles_list:
            VehicleUserPermission.objects.get_or_create(
                user=normal_user,
                vehicle=vehicle
            )
        self.stdout.write(self.style.SUCCESS(f'Granted permissions for: {normal_user.email}'))

        # ------------------------------------------------------------------
        # 6. Plans Section (Active and Future Plans)
        # ------------------------------------------------------------------
        now = timezone.now()
        active_start = now - timedelta(minutes=20)
        
        # We ensure Vehicle ID 3 (Index 2) has an active plan NOW
        plans_data = [
            {
                'vehicle': vehicles_list[0],
                'personnel': personnel_objs[0],
                'start_at': active_start,
                'end_at': active_start + timedelta(hours=4),
                'description': 'Route for ABC-123',
                'status': Plan.Status.ACTIVE,
                'created_by': normal_user,
            },
            {
                'vehicle': vehicles_list[1],
                'personnel': personnel_objs[1],
                'start_at': active_start,
                'end_at': active_start + timedelta(hours=4),
                'description': 'Route for XYZ-789',
                'status': Plan.Status.ACTIVE,
                'created_by': normal_user,
            },
            {
                'vehicle': vehicles_list[2], # IMPORTANT: Vehicle 3 (DEF-456)
                'personnel': personnel_objs[2],
                'start_at': active_start,
                'end_at': active_start + timedelta(hours=4),
                'description': 'Test Route for Vehicle 3',
                'status': Plan.Status.ACTIVE,
                'created_by': normal_user,
            },
            {
                'vehicle': vehicles_list[3],
                'personnel': personnel_objs[3],
                'start_at': now + timedelta(hours=2),
                'end_at': now + timedelta(hours=6),
                'description': 'Evening Route',
                'status': Plan.Status.PLANNED,
                'created_by': normal_user,
            },
            {
                'vehicle': vehicles_list[0],
                'personnel': personnel_objs[4],
                'start_at': now + timedelta(days=1),
                'end_at': now + timedelta(days=1, hours=3),
                'description': 'Tomorrow Delivery',
                'status': Plan.Status.PLANNED,
                'created_by': normal_user,
            },
        ]

        for p_data in plans_data:
            Plan.objects.create(
                vehicle=p_data['vehicle'],
                personnel=p_data['personnel'],
                start_at=p_data['start_at'],
                end_at=p_data['end_at'],
                description=p_data['description'],
                status=p_data['status'],
                created_by=p_data['created_by']
            )

        self.stdout.write(self.style.SUCCESS('\nFinished seeding! Vehicle 3 is now ACTIVE and Tracking should work.'))