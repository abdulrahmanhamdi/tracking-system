import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import './Vehicles.css'

function Vehicles() {
  const [vehicles, setVehicles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [plateFilter, setPlateFilter] = useState('')
  const [brandFilter, setBrandFilter] = useState('')

  useEffect(() => {
    fetchVehicles()
  }, [search, statusFilter, plateFilter, brandFilter])

  const fetchVehicles = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (statusFilter) params.append('status', statusFilter)
      if (plateFilter) params.append('plate', plateFilter)
      if (brandFilter) params.append('brand', brandFilter)
      
      const response = await api.get(`/vehicles/?${params.toString()}`)
      setVehicles(response.data.results || response.data)
    } catch (err) {
      setError('Failed to load vehicles')
      console.error('Vehicles error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="page-container"><div className="loading">Loading vehicles...</div></div>
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Vehicles</h1>
      </div>
      
      <div className="filters-section">
        <div className="filter-group">
          <input
            type="text"
            placeholder="Search (plate, brand, model)..."
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
            placeholder="Filter by plate..."
            value={plateFilter}
            onChange={(e) => setPlateFilter(e.target.value)}
            className="filter-input"
          />
        </div>
        <div className="filter-group">
          <input
            type="text"
            placeholder="Filter by brand..."
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
            {vehicles.length === 0 ? (
              <tr>
                <td colSpan="6">No vehicles found</td>
              </tr>
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
                  <td>
                    <Link to={`/vehicles/${vehicle.id}`} className="btn-link">
                      View Details
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Vehicles
