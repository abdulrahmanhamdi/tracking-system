import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../context/AuthContext' 
import './Vehicles.css'

function Vehicles() {
  const { user, loading: authLoading } = useAuth() 
  const [vehicles, setVehicles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // التحقق الشامل من صلاحية الأدمن لضمان الوصول
  const isAdmin = user && (
    user.is_superuser || 
    user.is_staff || 
    (user.role && user.role.toUpperCase() === 'ADMIN')
  );

  // حالات الفلترة والبحث
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [plateFilter, setPlateFilter] = useState('')
  const [brandFilter, setBrandFilter] = useState('')

  // حالات النافذة المنبثقة (Modal) والإدارة
  const [showModal, setShowModal] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState(null)
  const [formData, setFormData] = useState({
    plate: '',
    brand: '',
    model: '',
    year: new Date().getFullYear(),
    status: 'ACTIVE',
    owner: '' 
  })

  // جلب البيانات عند تغيير الفلاتر أو عند اكتمال تحميل بيانات المستخدم
  useEffect(() => {
    if (!authLoading) {
      fetchVehicles()
    }
  }, [authLoading, search, statusFilter, plateFilter, brandFilter])

  const fetchVehicles = async () => {
    try {
      setLoading(true)
      const response = await api.get('/vehicles/', {
        params: {
          search: search || undefined,
          status: statusFilter || undefined,
          plate: plateFilter || undefined,
          brand: brandFilter || undefined,
        }
      })
      // التعامل مع Pagination إذا كان موجوداً
      setVehicles(response.data.results || response.data)
    } catch (err) {
      setError('Failed to load vehicles')
      console.error('Vehicles error:', err)
    } finally {
      setLoading(false)
    }
  }

  // --- وظائف الإدارة (CRUD) ---

  const handleDelete = async (id) => {
    if (!isAdmin) {
      alert('لا تملك صلاحيات الحذف.');
      return;
    }
    if (window.confirm('هل أنت متأكد من حذف هذه السيارة نهائياً؟')) {
      try {
        await api.delete(`/vehicles/${id}/`)
        setVehicles(vehicles.filter(v => v.id !== id))
      } catch (err) {
        alert('حدث خطأ أثناء الحذف. تأكد من أن حسابك لديه صلاحيات كافية.')
      }
    }
  }

  const openModal = (vehicle = null) => {
    if (!isAdmin) {
      alert('عذراً، هذه الخاصية متاحة للمسؤولين فقط.');
      return;
    }
    if (vehicle) {
      setEditingVehicle(vehicle)
      setFormData({
        plate: vehicle.plate,
        brand: vehicle.brand,
        model: vehicle.model,
        year: vehicle.year,
        status: vehicle.status,
        owner: vehicle.owner || '' 
      })
    } else {
      setEditingVehicle(null)
      setFormData({
        plate: '',
        brand: '',
        model: '',
        year: new Date().getFullYear(),
        status: 'ACTIVE',
        owner: ''
      })
    }
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!isAdmin) return;
    
    const dataToSubmit = { ...formData };
    if (!dataToSubmit.owner || dataToSubmit.owner === '') {
        delete dataToSubmit.owner;
    } else {
        dataToSubmit.owner = parseInt(dataToSubmit.owner);
    }

    try {
      if (editingVehicle) {
        await api.put(`/vehicles/${editingVehicle.id}/`, dataToSubmit)
      } else {
        await api.post('/vehicles/', dataToSubmit)
      }
      setShowModal(false)
      fetchVehicles() 
    } catch (err) {
      console.error('Submit error:', err.response?.data);
      const errorMsg = err.response?.data?.plate?.[0] || 
                       err.response?.data?.detail || 
                       'حدث خطأ أثناء حفظ البيانات. تأكد من صحة معرف المالك وأن رقم اللوحة فريد.';
      alert(errorMsg)
    }
  }

  if (authLoading) return <div className="page-container">Loading User Permissions...</div>

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Vehicles Management</h1>
        
        {isAdmin && (
          <button className="btn-add-vehicle" onClick={() => openModal()}>
            + Add New Vehicle
          </button>
        )}
      </div>
      
      <div className="filters-section">
        <div className="filter-group">
          <input
            type="text"
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="filter-input"
          />
        </div>
        <div className="filter-group">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Status</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="MAINTENANCE">Maintenance</option>
          </select>
        </div>
        <div className="filter-group">
          <input
            type="text"
            placeholder="Plate..."
            value={plateFilter}
            onChange={(e) => setPlateFilter(e.target.value)}
            className="filter-input"
          />
        </div>
        <div className="filter-group">
          <input
            type="text"
            placeholder="Brand..."
            value={brandFilter}
            onChange={(e) => setBrandFilter(e.target.value)}
            className="filter-input"
          />
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      
      <div className="vehicles-table-container">
        <table className="vehicles-table">
          <thead>
            <tr>
              <th>Plate</th>
              <th>Brand</th>
              <th>Model</th>
              <th>Year</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="6" className="loading-cell">Loading Vehicles...</td></tr>
            ) : vehicles.length === 0 ? (
              <tr><td colSpan="6">No vehicles found</td></tr>
            ) : (
              vehicles.map((vehicle) => (
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
                  <td className="actions-cell">
                    <Link to={`/vehicles/${vehicle.id}`} className="btn-view">View</Link>
                    
                    {isAdmin && (
                      <>
                        <button onClick={() => openModal(vehicle)} className="btn-edit">Edit</button>
                        <button onClick={() => handleDelete(vehicle.id)} className="btn-delete">Delete</button>
                      </>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && isAdmin && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>{editingVehicle ? 'Edit Vehicle' : 'Add New Vehicle'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Plate Number</label>
                <input 
                  type="text" 
                  value={formData.plate} 
                  onChange={e => setFormData({...formData, plate: e.target.value})} 
                  required 
                />
              </div>
              <div className="form-group">
                <label>Owner (User ID)</label>
                <input 
                  type="number" 
                  placeholder="Leave empty for current user"
                  value={formData.owner} 
                  onChange={e => setFormData({...formData, owner: e.target.value})} 
                />
              </div>
              <div className="form-group">
                <label>Brand</label>
                <input 
                  type="text" 
                  value={formData.brand} 
                  onChange={e => setFormData({...formData, brand: e.target.value})} 
                  required 
                />
              </div>
              <div className="form-group">
                <label>Model</label>
                <input 
                  type="text" 
                  value={formData.model} 
                  onChange={e => setFormData({...formData, model: e.target.value})} 
                  required 
                />
              </div>
              <div className="form-group">
                <label>Year</label>
                <input 
                  type="number" 
                  value={formData.year} 
                  onChange={e => setFormData({...formData, year: e.target.value})} 
                  required 
                />
              </div>
              <div className="form-group">
                <label>Status</label>
                <select 
                  value={formData.status} 
                  onChange={e => setFormData({...formData, status: e.target.value})}
                >
                  <option value="ACTIVE">Active</option>
                  <option value="INACTIVE">Inactive</option>
                  <option value="MAINTENANCE">Maintenance</option>
                </select>
              </div>
              <div className="modal-buttons">
                <button type="submit" className="btn-save">Save Changes</button>
                <button type="button" className="btn-cancel" onClick={() => setShowModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Vehicles;