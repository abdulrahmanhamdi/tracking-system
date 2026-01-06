import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import './Dashboard.css'

function Dashboard() {
  const [stats, setStats] = useState({
    totalVehicles: 0,
    activeVehicles: 0,
    todayPlans: 0,
    recentVehicles: []
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch vehicles
      const vehiclesRes = await api.get('/vehicles/')
      const vehicles = vehiclesRes.data.results || vehiclesRes.data
      
      // Fetch last locations
      const locationsRes = await api.get('/vehicles/last-locations/')
      const lastLocations = locationsRes.data || []
      
      // Fetch plans
      const plansRes = await api.get('/plans/')
      const plans = plansRes.data.results || plansRes.data
      
      // Calculate stats
      const totalVehicles = vehicles.length
      
      // Active vehicles: last update within 60 seconds or speed > 0
      const now = new Date()
      const activeVehicles = lastLocations.filter(loc => {
        if (!loc.recorded_at) return false
        const lastUpdate = new Date(loc.recorded_at)
        const secondsSinceUpdate = (now - lastUpdate) / 1000
        return secondsSinceUpdate < 60 || (loc.speed && loc.speed > 0)
      }).length
      
      // Today's plans
      const today = new Date().toISOString().split('T')[0]
      const todayPlans = plans.filter(plan => {
        const planDate = new Date(plan.start_at).toISOString().split('T')[0]
        return planDate === today && plan.status !== 'CANCELED'
      }).length
      
      // Recent vehicles (last 5 with recent updates)
      const recentVehicles = lastLocations
        .filter(loc => loc.recorded_at)
        .sort((a, b) => new Date(b.recorded_at) - new Date(a.recorded_at))
        .slice(0, 5)
      
      setStats({
        totalVehicles,
        activeVehicles,
        todayPlans,
        recentVehicles
      })
    } catch (err) {
      setError('Failed to load dashboard data')
      console.error('Dashboard error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="dashboard"><div className="loading">Loading dashboard...</div></div>
  }

  if (error) {
    return <div className="dashboard"><div className="error-message">{error}</div></div>
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Vehicles</h3>
          <p className="stat-value">{stats.totalVehicles}</p>
        </div>
        <div className="stat-card">
          <h3>Active Vehicles</h3>
          <p className="stat-value">{stats.activeVehicles}</p>
        </div>
        <div className="stat-card">
          <h3>Today's Plans</h3>
          <p className="stat-value">{stats.todayPlans}</p>
        </div>
      </div>
      
      <div className="recent-vehicles">
        <h2>Recently Updated Vehicles</h2>
        {stats.recentVehicles.length === 0 ? (
          <p>No recent vehicle updates</p>
        ) : (
          <div className="vehicles-list">
            {stats.recentVehicles.map((vehicle) => (
              <Link 
                key={vehicle.vehicle_info?.id || vehicle.id} 
                to={`/vehicles/${vehicle.vehicle_info?.id || vehicle.id}`}
                className="vehicle-item"
              >
                <div className="vehicle-header">
                  <h4>{vehicle.vehicle_info?.plate || vehicle.plate}</h4>
                  <span className={`status-badge ${vehicle.vehicle_info?.status?.toLowerCase() || 'active'}`}>
                    {vehicle.vehicle_info?.status || 'Active'}
                  </span>
                </div>
                <div className="vehicle-details">
                  <p><strong>Brand:</strong> {vehicle.vehicle_info?.brand || vehicle.brand}</p>
                  <p><strong>Model:</strong> {vehicle.vehicle_info?.model || vehicle.model}</p>
                  {vehicle.lat && vehicle.lng && (
                  <p>
                    <strong>Last Location:</strong> 
                    {Number(vehicle.lat).toFixed(6)}, {Number(vehicle.lng).toFixed(6)}
                  </p>
                )}
                  {vehicle.recorded_at && (
                    <p><strong>Last Update:</strong> {new Date(vehicle.recorded_at).toLocaleString()}</p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
