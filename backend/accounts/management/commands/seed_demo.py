"""
Django management command to seed demo data.
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

        # Create admin user
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

        # Create normal user
        normal_user, created = User.objects.get_or_create(
            email='user@example.com',
            defaults={
                'username': 'user',
                'first_name': 'Normal',
                'last_name': 'User',
                'role': User.Role.USER,
            }
        )
        if created:
            normal_user.set_password('User1234!')
            normal_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created normal user: {normal_user.email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Normal user already exists: {normal_user.email}'))

        # Create vehicles with simulation routes
        vehicles_data = [
            {
                'plate': 'ABC-123',
                'brand': 'Toyota',
                'model': 'Camry',
                'year': 2020,
                'status': Vehicle.Status.ACTIVE,
                'simulation_route': [
                    [40.7128, -74.0060],  # NYC
                    [40.7138, -74.0070],
                    [40.7148, -74.0080],
                    [40.7158, -74.0090],
                    [40.7168, -74.0100],
                ]
            },
            {
                'plate': 'XYZ-789',
                'brand': 'Honda',
                'model': 'Civic',
                'year': 2021,
                'status': Vehicle.Status.ACTIVE,
                'simulation_route': [
                    [40.7580, -73.9855],  # Times Square area
                    [40.7590, -73.9865],
                    [40.7600, -73.9875],
                    [40.7610, -73.9885],
                ]
            },
            {
                'plate': 'DEF-456',
                'brand': 'Ford',
                'model': 'F-150',
                'year': 2019,
                'status': Vehicle.Status.INACTIVE,
                'simulation_route': [
                    [40.7505, -73.9934],  # Central Park area
                    [40.7515, -73.9944],
                    [40.7525, -73.9954],
                ]
            },
            {
                'plate': 'GHI-321',
                'brand': 'Tesla',
                'model': 'Model 3',
                'year': 2022,
                'status': Vehicle.Status.ACTIVE,
                'simulation_route': [
                    [40.7282, -73.7949],  # Brooklyn area
                    [40.7292, -73.7959],
                    [40.7302, -73.7969],
                    [40.7312, -73.7979],
                    [40.7322, -73.7989],
                ]
            },
            {
                'plate': 'JKL-654',
                'brand': 'BMW',
                'model': 'X5',
                'year': 2021,
                'status': Vehicle.Status.MAINTENANCE,
                'simulation_route': [
                    [40.7614, -73.9776],  # Lincoln Center area
                    [40.7624, -73.9786],
                    [40.7634, -73.9796],
                ]
            },
        ]

        vehicles = []
        for v_data in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                plate=v_data['plate'],
                defaults={
                    'owner': admin_user,
                    'brand': v_data['brand'],
                    'model': v_data['model'],
                    'year': v_data['year'],
                    'status': v_data['status'],
                    'simulation_route': v_data['simulation_route'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created vehicle: {vehicle.plate}'))
            else:
                self.stdout.write(self.style.WARNING(f'Vehicle already exists: {vehicle.plate}'))
            vehicles.append(vehicle)

        # Create personnel
        personnel_data = [
            {'full_name': 'John Doe', 'title': 'Driver', 'phone': '555-0101', 'email': 'john@example.com'},
            {'full_name': 'Jane Smith', 'title': 'Driver', 'phone': '555-0102', 'email': 'jane@example.com'},
            {'full_name': 'Bob Johnson', 'title': 'Supervisor', 'phone': '555-0103', 'email': 'bob@example.com'},
            {'full_name': 'Alice Williams', 'title': 'Driver', 'phone': '555-0104', 'email': 'alice@example.com'},
            {'full_name': 'Charlie Brown', 'title': 'Manager', 'phone': '555-0105', 'email': 'charlie@example.com'},
        ]

        personnel_list = []
        for p_data in personnel_data:
            person, created = Personnel.objects.get_or_create(
                email=p_data['email'],
                defaults=p_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created personnel: {person.full_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Personnel already exists: {person.full_name}'))
            personnel_list.append(person)

        # Create vehicle permissions for normal user (only first 2 vehicles)
        for vehicle in vehicles[:2]:
            perm, created = VehicleUserPermission.objects.get_or_create(
                user=normal_user,
                vehicle=vehicle
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created permission: {normal_user.email} -> {vehicle.plate}'))

        # Create plans (today + future) without conflicts
        now = timezone.now()
        today_start = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        plans_data = [
            {
                'vehicle': vehicles[0],
                'personnel': personnel_list[0],
                'start_at': today_start,
                'end_at': today_start + timedelta(hours=2),
                'description': 'Morning delivery route',
                'status': Plan.Status.PLANNED,
            },
            {
                'vehicle': vehicles[0],
                'personnel': personnel_list[0],
                'start_at': today_start + timedelta(hours=3),
                'end_at': today_start + timedelta(hours=5),
                'description': 'Afternoon pickup route',
                'status': Plan.Status.PLANNED,
            },
            {
                'vehicle': vehicles[1],
                'personnel': personnel_list[1],
                'start_at': today_start,
                'end_at': today_start + timedelta(hours=4),
                'description': 'Full day route',
                'status': Plan.Status.ACTIVE,
            },
            {
                'vehicle': vehicles[3],
                'personnel': personnel_list[2],
                'start_at': today_start + timedelta(days=1),
                'end_at': today_start + timedelta(days=1, hours=3),
                'description': 'Tomorrow morning route',
                'status': Plan.Status.PLANNED,
            },
            {
                'vehicle': vehicles[3],
                'personnel': personnel_list[3],
                'start_at': today_start + timedelta(days=2),
                'end_at': today_start + timedelta(days=2, hours=2),
                'description': 'Future route',
                'status': Plan.Status.PLANNED,
            },
        ]

        for plan_data in plans_data:
            plan, created = Plan.objects.get_or_create(
                vehicle=plan_data['vehicle'],
                personnel=plan_data['personnel'],
                start_at=plan_data['start_at'],
                defaults={
                    'end_at': plan_data['end_at'],
                    'description': plan_data['description'],
                    'status': plan_data['status'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created plan: {plan.vehicle.plate} - {plan.start_at}'))
            else:
                self.stdout.write(self.style.WARNING(f'Plan already exists: {plan.vehicle.plate} - {plan.start_at}'))

        self.stdout.write(self.style.SUCCESS('\nDemo data seeding completed!'))
        self.stdout.write(self.style.SUCCESS(f'\nAdmin credentials: admin@example.com / Admin1234!'))
        self.stdout.write(self.style.SUCCESS(f'User credentials: user@example.com / User1234!'))

