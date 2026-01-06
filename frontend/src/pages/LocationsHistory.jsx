import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/axios'
import './LocationsHistory.css'

function LocationsHistory() {
  const { vehicleId } = useParams()
  const [locations, setLocations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')

  useEffect(() => {
    if (vehicleId) {
      fetchLocations()
    } else {
      fetchAllLocations()
    }
  }, [vehicleId, fromDate, toDate])

  const fetchLocations = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (fromDate) {
        const from = new Date(fromDate).toISOString()
        params.append('from', from)
      }
      if (toDate) {
        const to = new Date(toDate).toISOString()
        params.append('to', to)
      }
      
      const url = vehicleId 
        ? `/vehicles/${vehicleId}/locations/?${params.toString()}`
        : `/tracking/locations/?${params.toString()}`
      
      const response = await api.get(url)
      setLocations(response.data.results || response.data)
    } catch (err) {
      setError('Failed to load location history')
      console.error('Locations error:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchAllLocations = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (fromDate) {
        const from = new Date(fromDate).toISOString()
        params.append('from', from)
      }
      if (toDate) {
        const to = new Date(toDate).toISOString()
        params.append('to', to)
      }
      
      const response = await api.get(`/tracking/locations/?${params.toString()}`)
      setLocations(response.data.results || response.data)
    } catch (err) {
      setError('Failed to load location history')
      console.error('Locations error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Location History{vehicleId ? ` - Vehicle ${vehicleId}` : ''}</h1>
      </div>
      
      <div className="filters-section">
        <div className="filter-group">
          <label>From Date:</label>
          <input
            type="datetime-local"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            className="filter-input"
          />
        </div>
        <div className="filter-group">
          <label>To Date:</label>
          <input
            type="datetime-local"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            className="filter-input"
          />
        </div>
        <button onClick={() => { setFromDate(''); setToDate('') }} className="btn-secondary">
          Clear Filters
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="loading">Loading locations...</div>
      ) : (
        <div className="locations-table-container">
          <table className="locations-table">
            <thead>
              <tr>
                <th>Vehicle</th>
                <th>Latitude</th>
                <th>Longitude</th>
                <th>Speed (km/h)</th>
                <th>Heading (°)</th>
                <th>Source</th>
                <th>Recorded At</th>
              </tr>
            </thead>
            <tbody>
              {locations.length === 0 ? (
                <tr>
                  <td colSpan="7">No location data found</td>
                </tr>
              ) : (
                locations.map((location) => (
                  <tr key={location.id}>
                    <td>{location.vehicle_info?.plate || location.vehicle}</td>
                    <td>{location.lat}</td>
                    <td>{location.lng}</td>
                    <td>{location.speed || 'N/A'}</td>
                    <td>{location.heading || 'N/A'}</td>
                    <td>{location.source}</td>
                    <td>{new Date(location.recorded_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
          
          {locations.length > 0 && (
            <div className="map-placeholder">
              <h3>Map View (Placeholder)</h3>
              <p>Map integration can be added here using libraries like Leaflet or Google Maps</p>
              <p>Showing {locations.length} location points</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default LocationsHistory
