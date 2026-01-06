import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api/axios'
import './VehicleDetails.css'

function VehicleDetails() {
  const { id } = useParams()
  const [vehicle, setVehicle] = useState(null)
  const [lastLocation, setLastLocation] = useState(null)
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchVehicleData()
  }, [id])

  const fetchVehicleData = async () => {
    try {
      setLoading(true)
      
      // Fetch vehicle
      const vehicleRes = await api.get(`/vehicles/${id}/`)
      setVehicle(vehicleRes.data)
      
      // Fetch last location
      try {
        const locationsRes = await api.get(`/vehicles/${id}/locations/?limit=1`)
        const locations = locationsRes.data.results || locationsRes.data
        if (locations.length > 0) {
          setLastLocation(locations[0])
        }
      } catch (err) {
        console.error('Error fetching last location:', err)
      }
      
      // Fetch plans for this vehicle
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
        <h1>Vehicle Details</h1>
        <Link to="/vehicles" className="btn-link">Back to Vehicles</Link>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="vehicle-details">
        <div className="detail-section">
          <h2>{vehicle.brand} {vehicle.model}</h2>
          <div className="detail-grid">
            <div className="detail-item">
              <label>Plate</label>
              <p>{vehicle.plate}</p>
            </div>
            <div className="detail-item">
              <label>Year</label>
              <p>{vehicle.year}</p>
            </div>
            <div className="detail-item">
              <label>Status</label>
              <span className={`status-badge ${vehicle.status.toLowerCase()}`}>
                {vehicle.status}
              </span>
            </div>
            <div className="detail-item">
              <label>Created</label>
              <p>{new Date(vehicle.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
        
        <div className="detail-section">
          <h3>Last Known Location</h3>
          {lastLocation ? (
            <div className="location-info">
              <p><strong>Coordinates:</strong> {lastLocation.lat}, {lastLocation.lng}</p>
              <p><strong>Speed:</strong> {lastLocation.speed ? `${lastLocation.speed} km/h` : 'N/A'}</p>
              <p><strong>Heading:</strong> {lastLocation.heading ? `${lastLocation.heading}°` : 'N/A'}</p>
              <p><strong>Recorded:</strong> {new Date(lastLocation.recorded_at).toLocaleString()}</p>
              <p><strong>Source:</strong> {lastLocation.source}</p>
              <Link to={`/locations/${id}`} className="btn-link">View History</Link>
            </div>
          ) : (
            <p>No location data available</p>
          )}
        </div>
        
        <div className="detail-section">
          <h3>Plans</h3>
          {plans.length === 0 ? (
            <p>No plans scheduled for this vehicle</p>
          ) : (
            <div className="plans-list">
              {plans.map((plan) => (
                <div key={plan.id} className="plan-item">
                  <div className="plan-header">
                    <h4>Plan #{plan.id}</h4>
                    <span className={`status-badge ${plan.status.toLowerCase()}`}>
                      {plan.status}
                    </span>
                  </div>
                  <p><strong>Personnel:</strong> {plan.personnel_info?.full_name || 'N/A'}</p>
                  <p><strong>Start:</strong> {new Date(plan.start_at).toLocaleString()}</p>
                  <p><strong>End:</strong> {new Date(plan.end_at).toLocaleString()}</p>
                  {plan.description && <p><strong>Description:</strong> {plan.description}</p>}
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
