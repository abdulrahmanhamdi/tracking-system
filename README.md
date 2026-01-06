# Vehicle Tracking & Planning Web App

A complete monorepo for a Vehicle Tracking & Planning system built with Django REST Framework backend and React frontend.

## Tech Stack

- **Backend**: Python Django + Django REST Framework
- **Realtime**: WebSocket using Django Channels
- **Database**: PostgreSQL
- **Frontend**: React (Vite)
- **Containerization**: Docker Compose

## Repository Structure

```
tracking-system/
├── backend/              # Django project
│   ├── core/            # Main Django project
│   ├── accounts/         # User authentication app
│   ├── vehicles/         # Vehicle management app
│   ├── tracking/         # Location tracking app
│   ├── planning/         # Route planning app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # React Vite app
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── components/   # Reusable components
│   │   └── api/          # API client setup
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml     # Docker Compose configuration
└── README.md
```

## Prerequisites

- Docker and Docker Compose installed
- Git (optional)

## Quick Start

### 1. Clone the repository (if applicable)

```bash
git clone <repository-url>
cd tracking-system
```

### 2. Set up environment variables

Create a `.env` file in the root directory (optional, defaults are provided):

```env
# Database Configuration
POSTGRES_DB=tracking_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Django Configuration
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

### 3. Build and start all services

```bash
docker compose up --build
```

This command will:
- Build Docker images for backend and frontend
- Start PostgreSQL database
- Start Django backend (waits for DB, runs migrations automatically)
- Start React frontend

### 4. Seed Demo Data

After the containers are running, seed demo data:

```bash
docker compose exec backend python manage.py seed_demo
```

This creates:
- Admin user: `admin@example.com` / `Admin1234!`
- Normal user: `user@example.com` / `User1234!`
- 5 vehicles with simulation routes
- 5 personnel
- Sample plans (today + future)
- Vehicle permissions for normal user (2 vehicles)

### 5. Access the application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Backend Admin**: http://localhost:8000/admin
- **PostgreSQL**: localhost:5432

### 6. Login

Visit http://localhost:5173 and use the demo login buttons:
- **Login as Admin** - Uses admin@example.com / Admin1234!
- **Login as User** - Uses user@example.com / User1234!

Or manually login at `/login` page.

## How to Use

### Access Django Admin

1. Visit http://localhost:8000/admin
2. Login with admin credentials: `admin@example.com` / `Admin1234!`
3. Manage users, vehicles, locations, plans, and permissions

### Test Live Tracking

1. Login as admin
2. Go to **Admin Panel** → **Simulation Routes**
3. Select a vehicle and set a simulation route (JSON array of [lat, lng] coordinates)
4. Go to **Admin Panel** → **Vehicles** and click **Start** for the vehicle
5. Go to **Live Tracking** page
6. Select the vehicle from dropdown
7. Watch real-time location updates appear every 1-2 seconds
8. Check **Locations History** to see all recorded points in database

### Test Planning Conflict Detection

1. Login as admin
2. Go to **Planning** page
3. Click **Create Plan**
4. Select a vehicle, personnel, and set start/end times
5. Try creating an overlapping plan for the same vehicle → Should show error
6. Create non-overlapping plans → Should succeed

### Test RBAC (Role-Based Access Control)

1. Login as **User** (user@example.com)
2. Go to **Vehicles** → Should only see 2 vehicles (the ones with permissions)
3. Try accessing Admin Panel → Should be redirected
4. Login as **Admin** → Should see all vehicles and have admin access

## Development

### Backend Development

The backend automatically:
- Waits for database to be ready
- Runs migrations on container start
- Reloads on code changes (volume mount)

To run Django management commands:
```bash
docker compose exec backend python manage.py <command>
```

Create a superuser:
```bash
docker compose exec backend python manage.py createsuperuser
```

Seed demo data:
```bash
docker compose exec backend python manage.py seed_demo
```

### Frontend Development

The frontend:
- Hot-reloads on code changes
- Uses Vite dev server
- Connects to backend via `VITE_API_URL` environment variable

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (get access + refresh tokens)
- `POST /api/auth/logout/` - Logout (blacklist refresh token)
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password with token
- `GET /api/me/` - Get current user info

### Admin
- `GET /api/admin/users/` - List all users (admin only)
- `PUT /api/admin/users/{id}/` - Update user role/is_active (admin only)

### Vehicles
- `GET /api/vehicles/` - List vehicles (filtered by permissions)
- `POST /api/vehicles/` - Create vehicle (admin only)
- `GET /api/vehicles/{id}/` - Get vehicle details
- `PUT /api/vehicles/{id}/` - Update vehicle (admin only)
- `DELETE /api/vehicles/{id}/` - Delete vehicle (admin only)
- `PUT /api/vehicles/{id}/simulation-route/` - Set simulation route (admin only)

### Tracking
- `GET /api/tracking/locations/` - List all location history
- `GET /api/vehicles/{id}/locations/` - Get vehicle location history
- `GET /api/vehicles/last-locations/` - Get last known location per vehicle

### Live Tracking
- `POST /api/live/start/{vehicle_id}/` - Start streaming (admin only)
- `POST /api/live/stop/{vehicle_id}/` - Stop streaming (admin only)
- `WS /ws/live?vehicle_id={id}&token={jwt}` - WebSocket connection

### Planning
- `GET /api/plans/` - List plans (filtered by vehicle permissions)
- `POST /api/plans/` - Create plan (admin only)
- `PUT /api/plans/{id}/` - Update plan (admin only)
- `DELETE /api/plans/{id}/` - Delete plan (admin only)

### Personnel
- `GET /api/personnel/` - List personnel
- `POST /api/personnel/` - Create personnel (admin only)
- `PUT /api/personnel/{id}/` - Update personnel (admin only)
- `DELETE /api/personnel/{id}/` - Delete personnel (admin only)

## Frontend Pages

- `/` - Landing page with demo login buttons
- `/login` - Login page
- `/register` - Registration page
- `/forgot-password` - Password reset request
- `/reset-password` - Password reset
- `/app` - Dashboard (protected)
- `/app/vehicles` - Vehicle list
- `/app/vehicles/:id` - Vehicle details
- `/app/locations` - Location history
- `/app/locations/:vehicleId` - Vehicle-specific location history
- `/app/live` - Live tracking
- `/app/planning` - Route planning
- `/app/admin` - Admin panel

## WebSocket Live Tracking

### WebSocket Endpoint

**Connection URL:** `ws://localhost:8000/ws/live?vehicle_id={id}&token={jwt_token}`

**Authentication:**
- JWT token can be passed via query string: `?token=...`
- Or via Authorization header: `Authorization: Bearer <token>`
- For development, query string is acceptable; for production, use headers

**Message Format:**

Location Update:
```json
{
  "type": "location",
  "vehicle_id": 1,
  "lat": 40.7128,
  "lng": -74.0060,
  "speed": 45.5,
  "heading": 180.0,
  "recorded_at": "2024-01-01T12:00:00Z",
  "source": "SIMULATED"
}
```

Status Message:
```json
{
  "type": "status",
  "message": "Streaming paused",
  "streaming": false
}
```

### Frontend Reconnect Strategy

The frontend implements exponential backoff reconnection:
- Starts with 1 second delay
- Doubles delay on each retry (max 30 seconds)
- Resets after successful connection
- Handles token refresh automatically

## Stopping the Services

```bash
docker compose down
```

To remove volumes (database data):
```bash
docker compose down -v
```

## Troubleshooting

### Backend won't start
- Check if PostgreSQL is healthy: `docker compose ps`
- Check backend logs: `docker compose logs backend`
- Ensure database credentials match in `.env`

### Frontend won't connect to backend
- Verify `VITE_API_URL` in `.env` matches backend URL
- Check CORS settings in `backend/core/settings.py`
- Ensure backend is running: `curl http://localhost:8000/api/health/`

### Database connection errors
- Wait for database to be ready (healthcheck should pass)
- Verify POSTGRES_* environment variables
- Check database logs: `docker compose logs db`

### WebSocket not connecting
- Ensure vehicle streaming is started: `POST /api/live/start/{vehicle_id}/`
- Check WebSocket URL format: `ws://localhost:8000/ws/live?vehicle_id={id}&token={token}`
- Verify JWT token is valid and not expired
- Check browser console for connection errors

## Acceptance Checklist

✅ **Register/Login works**
- Users can register with email, password, name
- Users can login and receive JWT tokens
- Token refresh works automatically

✅ **Forgot/Reset works**
- Password reset tokens generated and logged to console
- Tokens expire after 30 minutes
- Tokens are one-time use

✅ **RBAC enforced**
- Admin can access all features
- Users can only see permitted vehicles
- Backend enforces permissions on all endpoints

✅ **Vehicles list/filter works**
- Search by plate, brand, model
- Filter by status, plate, brand
- Pagination supported

✅ **Last locations + history works**
- Last known location per vehicle
- Date range filtering
- Vehicle-specific history

✅ **Live tracking WebSocket works**
- Real-time updates every 1-2 seconds
- Simulated routes generate location data
- All points saved to database with source=SIMULATED
- Start/stop controls work

✅ **Planning conflict detection works**
- Overlapping plans blocked with clear error
- Non-overlapping plans allowed
- Conflict detection excludes canceled/completed plans

✅ **Admin panel features work**
- User management (list, update role, activate/deactivate)
- Vehicle management (start/stop streaming)
- Personnel management
- Simulation route management

## Production Considerations

Before deploying to production:

1. Change `SECRET_KEY` to a secure random value
2. Set `DEBUG=False`
3. Configure proper `ALLOWED_HOSTS`
4. Set up proper SSL/TLS certificates (WSS for WebSocket)
5. Use environment-specific `.env` files
6. Configure Redis for Channels (currently using in-memory fallback)
7. Set up proper static file serving
8. Configure database backups
9. Set up monitoring and logging
10. Review security settings
11. Use WebSocket headers for JWT (not query string) in production
12. Implement rate limiting for WebSocket connections
13. Monitor WebSocket connection count and performance
14. Use httpOnly cookies for JWT tokens instead of localStorage

## License

This project is provided as-is for development purposes.
