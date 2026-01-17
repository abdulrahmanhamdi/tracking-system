import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../context/AuthContext' // استيراد نظام الصلاحيات
import './VehicleDetails.css'

// استيراد أيقونات أو تنسيقات إضافية إذا لزم الأمر
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'

function VehicleDetails() {
  const { id } = useParams()
  const { user } = useAuth() // جلب بيانات المستخدم الحالي
  const [vehicle, setVehicle] = useState(null)
  const [lastLocation, setLastLocation] = useState(null)
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const isAdmin = user?.role === 'ADMIN'

  useEffect(() => {
    fetchVehicleData()
  }, [id])

  const fetchVehicleData = async () => {
    try {
      setLoading(true)
      
      // 1. جلب بيانات المركبة
      const vehicleRes = await api.get(`/vehicles/${id}/`)
      setVehicle(vehicleRes.data)
      
      // 2. جلب آخر موقع معروف
      try {
        const locationsRes = await api.get(`/vehicles/${id}/locations/?limit=1`)
        const locations = locationsRes.data.results || locationsRes.data
        if (locations.length > 0) {
          setLastLocation(locations[0])
        }
      } catch (err) {
        console.error('Error fetching last location:', err)
      }
      
      // 3. جلب الخطط المرتبطة بهذه المركبة
      try {
        const plansRes = await api.get('/plans/')
        const allPlans = plansRes.data.results || plansRes.data
        const vehiclePlans = allPlans.filter(plan => plan.vehicle === parseInt(id))
        setPlans(vehiclePlans)
      } catch (err) {
        console.error('Error fetching plans:', err)
      }
    } catch (err) {
      setError('Failed to load vehicle details')
      console.error('Vehicle details error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="page-container"><div className="loading">Loading...</div></div>
  }

  if (!vehicle) {
    return <div className="page-container"><div className="error-message">Vehicle not found</div></div>
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="header-title">
          <h1>Vehicle Details</h1>
          <span className={`status-badge ${vehicle.status.toLowerCase()}`}>
            {vehicle.status}
          </span>
        </div>
        <div className="header-actions">
          <Link to="/vehicles" className="btn-secondary">Back to Vehicles</Link>
          
          {/* زر التتبع المباشر يظهر للجميع */}
          <Link to={`/tracking?vehicle_id=${id}`} className="btn-primary">Live Track</Link>
          
          {/* زر التعديل يظهر فقط للمسؤول (Admin) */}
          {isAdmin && (
            <Link to={`/vehicles/${id}/edit`} className="btn-warning">Edit Vehicle</Link>
          )}
        </div>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="vehicle-details-grid">
        {/* القسم الأول: المعلومات الأساسية */}
        <div className="detail-section info-card">
          <h3>Basic Information</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <label>Plate Number</label>
              <p className="highlight">{vehicle.plate}</p>
            </div>
            <div className="detail-item">
              <label>Brand & Model</label>
              <p>{vehicle.brand} {vehicle.model}</p>
            </div>
            <div className="detail-item">
              <label>Year</label>
              <p>{vehicle.year}</p>
            </div>
            {/* عرض المالك للمسؤولين فقط */}
            {isAdmin && (
              <div className="detail-item">
                <label>Managed By (Owner)</label>
                <p>{vehicle.owner_info?.full_name || 'System Admin'}</p>
              </div>
            )}
            <div className="detail-item">
              <label>Added On</label>
              <p>{new Date(vehicle.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
        
        {/* القسم الثاني: آخر موقع معروف */}
        <div className="detail-section location-card">
          <h3>Last Known Location</h3>
          {lastLocation ? (
            <div className="location-content">
              <div className="location-info">
                <p><strong>Lat/Lng:</strong> {lastLocation.lat}, {lastLocation.lng}</p>
                <p><strong>Speed:</strong> {lastLocation.speed ? `${lastLocation.speed} km/h` : 'Stopped'}</p>
                <p><strong>Last Update:</strong> {new Date(lastLocation.recorded_at).toLocaleString()}</p>
              </div>
              <Link to={`/locations/${id}`} className="btn-link">View History Path</Link>
            </div>
          ) : (
            <p className="no-data">No location data recorded yet.</p>
          )}
        </div>

        {/* القسم الثالث: الجدولة والخطط */}
        <div className="detail-section plans-card">
          <h3>Assigned Plans</h3>
          {plans.length === 0 ? (
            <p className="no-data">No active or future plans scheduled.</p>
          ) : (
            <div className="plans-list">
              {plans.map((plan) => (
                <div key={plan.id} className="plan-card-item">
                  <div className="plan-header">
                    <strong>#{plan.id} - {plan.status}</strong>
                    <span className="plan-date">{new Date(plan.start_at).toLocaleDateString()}</span>
                  </div>
                  <div className="plan-body">
                    <p><strong>Personnel:</strong> {plan.personnel_info?.full_name}</p>
                    <p><strong>Duration:</strong> {new Date(plan.start_at).toLocaleTimeString()} - {new Date(plan.end_at).toLocaleTimeString()}</p>
                    {plan.description && <p className="description">{plan.description}</p>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default VehicleDetails