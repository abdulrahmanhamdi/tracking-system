import { useEffect, useState } from 'react'
import api from '../api/axios'
import { getUser } from '../utils/auth'
import './Planning.css'

function Planning() {
  const [plans, setPlans] = useState([])
  const [vehicles, setVehicles] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [vehicleFilter, setVehicleFilter] = useState('')
  const [user, setUser] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    vehicle: '',
    personnel: '',
    start_at: '',
    end_at: '',
    description: '',
    status: 'PLANNED'
  })

  useEffect(() => {
    fetchData()
  }, [vehicleFilter])

  const fetchData = async () => {
    try {
      setLoading(true)
      
      // Fetch user to check role
      const userData = await getUser()
      setUser(userData)
      
      // Fetch plans
      const plansRes = await api.get('/plans/')
      let allPlans = plansRes.data.results || plansRes.data
      
      // Filter by vehicle if selected
      if (vehicleFilter) {
        allPlans = allPlans.filter(plan => plan.vehicle === parseInt(vehicleFilter))
      }
      
      setPlans(allPlans)
      
      // Fetch vehicles and personnel for admin
      if (userData?.role === 'ADMIN') {
        const vehiclesRes = await api.get('/vehicles/')
        setVehicles(vehiclesRes.data.results || vehiclesRes.data)
        
        const personnelRes = await api.get('/personnel/')
        setPersonnel(personnelRes.data.results || personnelRes.data)
      }
    } catch (err) {
      setError('Failed to load plans')
      console.error('Planning error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePlan = async (e) => {
    e.preventDefault()
    try {
      await api.post('/plans/', formData)
      setShowCreateForm(false)
      setFormData({
        vehicle: '',
        personnel: '',
        start_at: '',
        end_at: '',
        description: '',
        status: 'PLANNED'
      })
      fetchData()
    } catch (err) {
      const errorData = err.response?.data
      if (typeof errorData === 'object') {
        const errorMessages = Object.values(errorData).flat()
        setError(errorMessages.join(', '))
      } else {
        setError('Failed to create plan')
      }
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  if (loading) {
    return <div className="page-container"><div className="loading">Loading plans...</div></div>
  }

  const isAdmin = user?.role === 'ADMIN'

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Planning</h1>
        {isAdmin && (
          <button 
            className="btn-primary" 
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? 'Cancel' : 'Create Plan'}
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {showCreateForm && isAdmin && (
        <div className="create-plan-form">
          <h3>Create New Plan</h3>
          <form onSubmit={handleCreatePlan}>
            <div className="form-group">
              <label>Vehicle *</label>
              <select
                name="vehicle"
                value={formData.vehicle}
                onChange={handleChange}
                required
              >
                <option value="">Select vehicle</option>
                {vehicles.map(v => (
                  <option key={v.id} value={v.id}>{v.plate} - {v.brand} {v.model}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Personnel *</label>
              <select
                name="personnel"
                value={formData.personnel}
                onChange={handleChange}
                required
              >
                <option value="">Select personnel</option>
                {personnel.map(p => (
                  <option key={p.id} value={p.id}>{p.full_name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Start Time *</label>
              <input
                type="datetime-local"
                name="start_at"
                value={formData.start_at}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>End Time *</label>
              <input
                type="datetime-local"
                name="end_at"
                value={formData.end_at}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows="3"
              />
            </div>
            <button type="submit" className="btn-primary">Create Plan</button>
          </form>
        </div>
      )}

      <div className="filters-section">
        <div className="filter-group">
          <label>Filter by Vehicle:</label>
          <select
            value={vehicleFilter}
            onChange={(e) => setVehicleFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Vehicles</option>
            {vehicles.map(v => (
              <option key={v.id} value={v.id}>{v.plate}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="plans-list">
        {plans.length === 0 ? (
          <p>No plans found</p>
        ) : (
          plans.map((plan) => (
            <div key={plan.id} className="plan-card">
              <div className="plan-header">
                <h3>Plan #{plan.id}</h3>
                <span className={`status-badge ${plan.status.toLowerCase()}`}>
                  {plan.status}
                </span>
              </div>
              <div className="plan-details">
                <p><strong>Vehicle:</strong> {plan.vehicle_info?.plate || 'N/A'}</p>
                <p><strong>Personnel:</strong> {plan.personnel_info?.full_name || 'N/A'}</p>
                <p><strong>Start:</strong> {new Date(plan.start_at).toLocaleString()}</p>
                <p><strong>End:</strong> {new Date(plan.end_at).toLocaleString()}</p>
                {plan.description && <p><strong>Description:</strong> {plan.description}</p>}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default Planning
