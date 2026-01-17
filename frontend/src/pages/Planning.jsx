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
  
  // حالات التحكم في النموذج (إنشاء وتعديل)
  const [showForm, setShowForm] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [currentPlanId, setCurrentPlanId] = useState(null)

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
      const userData = await getUser()
      setUser(userData)
      
      const plansRes = await api.get('/plans/')
      let allPlans = plansRes.data.results || plansRes.data
      
      if (vehicleFilter) {
        allPlans = allPlans.filter(plan => plan.vehicle === parseInt(vehicleFilter))
      }
      
      setPlans(allPlans)
      
      if (userData) {
        const [vehiclesRes, personnelRes] = await Promise.all([
          api.get('/vehicles/'),
          api.get('/personnel/')
        ])
        
        setVehicles(vehiclesRes.data.results || vehiclesRes.data)
        setPersonnel(personnelRes.data.results || personnelRes.data)
      }
    } catch (err) {
      setError('Failed to load planning data')
      console.error('Planning error:', err)
    } finally {
      setLoading(false)
    }
  }

  // دالة موحدة للتعامل مع الإرسال (إنشاء أو تعديل)
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    // إرسال البيانات كما هي من input datetime-local 
    // نظام Django سيقوم بتفسيرها بناءً على TIME_ZONE = 'Europe/Istanbul'
    try {
      if (isEditing) {
        await api.patch(`/plans/${currentPlanId}/`, formData)
      } else {
        await api.post('/plans/', formData)
      }
      resetForm()
      fetchData()
    } catch (err) {
      const errorData = err.response?.data
      if (typeof errorData === 'object') {
        const errorMessages = Object.values(errorData).flat()
        setError(errorMessages.join(', '))
      } else {
        setError('Operation failed')
      }
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('هل أنت متأكد من حذف هذه الخطة؟')) return
    try {
      await api.delete(`/plans/${id}/`)
      fetchData()
    } catch (err) {
      setError('Failed to delete plan')
    }
  }

  const openEditForm = (plan) => {
    setFormData({
      vehicle: plan.vehicle,
      personnel: plan.personnel,
      // قص السلسلة الزمنية لتناسب تنسيق datetime-local (YYYY-MM-DDTHH:MM)
      start_at: plan.start_at ? plan.start_at.slice(0, 16) : '',
      end_at: plan.end_at ? plan.end_at.slice(0, 16) : '',
      description: plan.description || '',
      status: plan.status
    })
    setCurrentPlanId(plan.id)
    setIsEditing(true)
    setShowForm(true)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const resetForm = () => {
    setShowForm(false)
    setIsEditing(false)
    setCurrentPlanId(null)
    setFormData({
      vehicle: '',
      personnel: '',
      start_at: '',
      end_at: '',
      description: '',
      status: 'PLANNED'
    })
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  // تنسيق الوقت للعرض حسب توقيت إسطنبول (tr-TR)
  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString('tr-TR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  }

  if (loading) {
    return <div className="page-container"><div className="loading">Loading plans...</div></div>
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Planning</h1>
        {user && (
          <button 
            className={showForm ? "btn-secondary" : "btn-primary"} 
            onClick={() => showForm ? resetForm() : setShowForm(true)}
          >
            {showForm ? 'Cancel' : 'Create Plan'}
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {showForm && user && (
        <div className="create-plan-form">
          <h3>{isEditing ? 'Edit Plan' : 'Create New Plan'}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Vehicle *</label>
              <select name="vehicle" value={formData.vehicle} onChange={handleChange} required>
                <option value="">Select vehicle</option>
                {vehicles.map(v => (
                  <option key={v.id} value={v.id}>{v.plate} - {v.brand} {v.model}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Personnel *</label>
              <select name="personnel" value={formData.personnel} onChange={handleChange} required>
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
              <textarea name="description" value={formData.description} onChange={handleChange} rows="3" />
            </div>
            {isEditing && (
              <div className="form-group">
                <label>Status</label>
                <select name="status" value={formData.status} onChange={handleChange}>
                  <option value="PLANNED">Planned</option>
                  <option value="ACTIVE">Active</option>
                  <option value="COMPLETED">Completed</option>
                  <option value="CANCELED">Canceled</option>
                </select>
              </div>
            )}
            <button type="submit" className="btn-primary">
              {isEditing ? 'Update Plan' : 'Create Plan'}
            </button>
          </form>
        </div>
      )}

      <div className="filters-section">
        <div className="filter-group">
          <label>Filter by Vehicle:</label>
          <select value={vehicleFilter} onChange={(e) => setVehicleFilter(e.target.value)} className="filter-select">
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
                <h3>Plan #{plan.user_plan_number || plan.id}</h3>
                <div className="plan-header-right">
                  <span className={`status-badge ${plan.status.toLowerCase()}`}>
                    {plan.status}
                  </span>
                  {(user?.role === 'ADMIN' || plan.created_by === user?.id) && (
                    <div className="action-buttons">
                      <button className="edit-btn" onClick={() => openEditForm(plan)}>Edit</button>
                      <button className="delete-btn" onClick={() => handleDelete(plan.id)}>Delete</button>
                    </div>
                  )}
                </div>
              </div>
              <div className="plan-details">
                <p><strong>Vehicle:</strong> {plan.vehicle_info?.plate || 'N/A'}</p>
                <p><strong>Personnel:</strong> {plan.personnel_info?.full_name || 'N/A'}</p>
                <p><strong>Start:</strong> {formatDateTime(plan.start_at)}</p>
                <p><strong>End:</strong> {formatDateTime(plan.end_at)}</p>
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