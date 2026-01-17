import { useEffect, useState } from 'react'
import api from '../api/axios'
import { getUser } from '../utils/auth'
import { useNavigate } from 'react-router-dom'
import './AdminPanel.css'

function AdminPanel() {
  const [user, setUser] = useState(null)
  const [activeTab, setActiveTab] = useState('users')
  const [users, setUsers] = useState([])
  const [vehicles, setVehicles] = useState([])
  const [personnel, setPersonnel] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  // حالات النماذج (Form states)
  const [showUserForm, setShowUserForm] = useState(false)
  const [showVehicleForm, setShowVehicleForm] = useState(false)
  const [showPersonnelForm, setShowPersonnelForm] = useState(false)
  const [showRouteForm, setShowRouteForm] = useState(false)
  const [selectedVehicleForRoute, setSelectedVehicleForRoute] = useState(null)
  const [routeData, setRouteData] = useState('')

  useEffect(() => {
    checkAdminAccess()
  }, [])

  // دالة مساعدة للتحقق من صلاحية الأدمن بشكل مرن (تشمل السوبر يوزر)
  const isAdmin = (userData) => {
    return userData && (userData.is_superuser || (userData.role && userData.role.toUpperCase() === 'ADMIN'));
  };

  useEffect(() => {
    // جلب البيانات فقط إذا كان المستخدم أدمن
    if (isAdmin(user)) {
      fetchData()
    }
  }, [activeTab, user])

  const checkAdminAccess = async () => {
    const userData = await getUser()
    // إذا لم يكن المستخدم أدمن أو سوبر يوزر، يتم توجيهه للصفحة الرئيسية
    if (!isAdmin(userData)) {
      navigate('/')
      return
    }
    setUser(userData)
  }

  const fetchData = async () => {
    try {
      setLoading(true)
      if (activeTab === 'users') {
        const res = await api.get('/admin/users/')
        setUsers(res.data || [])
      } else if (activeTab === 'vehicles') {
        const res = await api.get('/vehicles/')
        setVehicles(res.data.results || res.data)
      } else if (activeTab === 'personnel') {
        const res = await api.get('/personnel/')
        setPersonnel(res.data.results || res.data)
      }
    } catch (err) {
      setError('Failed to load data')
      console.error('Admin panel error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateUser = async (userId, updates) => {
    try {
      await api.put(`/admin/users/${userId}/`, updates)
      fetchData()
      setError('')
    } catch (err) {
      setError('Failed to update user')
      console.error('Update user error:', err)
    }
  }

  const handleSetRoute = async (e) => {
    e.preventDefault()
    try {
      const route = JSON.parse(routeData)
      await api.put(`/vehicles/${selectedVehicleForRoute}/simulation-route/`, { route })
      setShowRouteForm(false)
      setRouteData('')
      setSelectedVehicleForRoute(null)
      alert('Simulation route updated successfully')
    } catch (err) {
      setError('Failed to set route. Make sure JSON is valid.')
      console.error('Route error:', err)
    }
  }

  const handleStartStreaming = async (vehicleId) => {
    try {
      await api.post(`/live/start/${vehicleId}/`)
      alert('Streaming started')
      fetchData()
    } catch (err) {
      setError('Failed to start streaming')
    }
  }

  const handleStopStreaming = async (vehicleId) => {
    try {
      await api.post(`/live/stop/${vehicleId}/`)
      alert('Streaming stopped')
      fetchData()
    } catch (err) {
      setError('Failed to stop streaming')
    }
  }

  // عرض رسالة منع الوصول إذا لم تتحقق الصلاحية
  if (!user || !isAdmin(user)) {
    return <div className="page-container">Access denied</div>
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Admin Panel</h1>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="admin-tabs">
        <button 
          className={activeTab === 'users' ? 'active' : ''}
          onClick={() => setActiveTab('users')}
        >
          Users
        </button>
        <button 
          className={activeTab === 'vehicles' ? 'active' : ''}
          onClick={() => setActiveTab('vehicles')}
        >
          Vehicles
        </button>
        <button 
          className={activeTab === 'personnel' ? 'active' : ''}
          onClick={() => setActiveTab('personnel')}
        >
          Personnel
        </button>
        <button 
          className={activeTab === 'simulation' ? 'active' : ''}
          onClick={() => setActiveTab('simulation')}
        >
          Simulation Routes
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <>
          {activeTab === 'users' && (
            <div className="admin-section">
              <div className="section-header">
                <h2>Users Management</h2>
              </div>
              <div className="table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Email</th>
                      <th>Name</th>
                      <th>Role</th>
                      <th>Active</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(userItem => (
                      <tr key={userItem.id}>
                        <td>{userItem.email}</td>
                        <td>{userItem.first_name} {userItem.last_name}</td>
                        <td>
                          <select
                            value={userItem.role}
                            onChange={(e) => handleUpdateUser(userItem.id, { role: e.target.value })}
                            className="role-select"
                          >
                            <option value="ADMIN">Admin</option>
                            <option value="USER">User</option>
                          </select>
                        </td>
                        <td>
                          <input
                            type="checkbox"
                            checked={userItem.is_active}
                            onChange={(e) => handleUpdateUser(userItem.id, { is_active: e.target.checked })}
                          />
                        </td>
                        <td>
                          <span className={`status-badge ${userItem.is_active ? 'active' : 'inactive'}`}>
                            {userItem.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'vehicles' && (
            <div className="admin-section">
              <div className="section-header">
                <h2>Vehicles Management</h2>
                <button className="btn-primary" onClick={() => setShowVehicleForm(!showVehicleForm)}>
                  {showVehicleForm ? 'Cancel' : 'Add Vehicle'}
                </button>
              </div>
              {showVehicleForm && (
                <div className="form-section">
                  <p>Vehicle creation form can be added here or used from Vehicles page</p>
                </div>
              )}
              <div className="table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Plate</th>
                      <th>Brand</th>
                      <th>Model</th>
                      <th>Year</th>
                      <th>Status</th>
                      <th>Streaming</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {vehicles.map(vehicle => (
                      <tr key={vehicle.id}>
                        <td>{vehicle.plate}</td>
                        <td>{vehicle.brand}</td>
                        <td>{vehicle.model}</td>
                        <td>{vehicle.year}</td>
                        <td>
                          <span className={`status-badge ${vehicle.status.toLowerCase()}`}>
                            {vehicle.status}
                          </span>
                        </td>
                        <td>
                          {vehicle.is_streaming ? (
                            <span className="status-badge active">Active</span>
                          ) : (
                            <span className="status-badge inactive">Inactive</span>
                          )}
                        </td>
                        <td>
                          <button 
                            className="btn-small"
                            onClick={() => handleStartStreaming(vehicle.id)}
                            disabled={vehicle.is_streaming}
                          >
                            Start
                          </button>
                          <button 
                            className="btn-small"
                            onClick={() => handleStopStreaming(vehicle.id)}
                            disabled={!vehicle.is_streaming}
                          >
                            Stop
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'personnel' && (
            <div className="admin-section">
              <div className="section-header">
                <h2>Personnel Management</h2>
                <button className="btn-primary" onClick={() => setShowPersonnelForm(!showPersonnelForm)}>
                  {showPersonnelForm ? 'Cancel' : 'Add Personnel'}
                </button>
              </div>
              {showPersonnelForm && (
                <div className="form-section">
                  <p>Personnel creation form can be added here</p>
                </div>
              )}
              <div className="table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Full Name</th>
                      <th>Title</th>
                      <th>Phone</th>
                      <th>Email</th>
                    </tr>
                  </thead>
                  <tbody>
                    {personnel.map(p => (
                      <tr key={p.id}>
                        <td>{p.full_name}</td>
                        <td>{p.title || 'N/A'}</td>
                        <td>{p.phone || 'N/A'}</td>
                        <td>{p.email || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'simulation' && (
            <div className="admin-section">
              <h2>Simulation Routes</h2>
              <div className="route-form-section">
                <div className="form-group">
                  <label>Select Vehicle:</label>
                  <select
                    value={selectedVehicleForRoute || ''}
                    onChange={(e) => setSelectedVehicleForRoute(e.target.value)}
                    className="form-select"
                  >
                    <option value="">-- Select vehicle --</option>
                    {vehicles.map(v => (
                      <option key={v.id} value={v.id}>{v.plate} - {v.brand} {v.model}</option>
                    ))}
                  </select>
                </div>
                {selectedVehicleForRoute && (
                  <form onSubmit={handleSetRoute} className="route-form">
                    <div className="form-group">
                      <label>Route JSON (array of [lat, lng] coordinates):</label>
                      <textarea
                        value={routeData}
                        onChange={(e) => setRouteData(e.target.value)}
                        placeholder='[[40.7128, 28.9744], [40.7138, 28.9754]]'
                        rows="6"
                        className="route-textarea"
                        required
                      />
                    </div>
                    <button type="submit" className="btn-primary">Set Route</button>
                  </form>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default AdminPanel;