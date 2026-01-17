import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/axios'
import './LocationsHistory.css'

// --- إضافات الخريطة ---
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// حل مشكلة أيقونات Leaflet الافتراضية مع Vite/React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});
// --------------------

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
      if (fromDate) params.append('from', new Date(fromDate).toISOString())
      if (toDate) params.append('to', new Date(toDate).toISOString())
      
      const url = vehicleId 
        ? `/vehicles/${vehicleId}/locations/?${params.toString()}`
        : `/tracking/locations/?${params.toString()}`
      
      const response = await api.get(url)
      setLocations(response.data.results || response.data)
    } catch (err) {
      setError('Failed to load location history')
    } finally {
      setLoading(false)
    }
  }

  const fetchAllLocations = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (fromDate) params.append('from', new Date(fromDate).toISOString())
      if (toDate) params.append('to', new Date(toDate).toISOString())
      
      const response = await api.get(`/tracking/locations/?${params.toString()}`)
      setLocations(response.data.results || response.data)
    } catch (err) {
      setError('Failed to load location history')
    } finally {
      setLoading(false)
    }
  }

  // تجهيز إحداثيات المسار للخريطة
  const polylinePositions = locations.map(loc => [loc.lat, loc.lng]);
  const mapCenter = polylinePositions.length > 0 ? polylinePositions[0] : [40.7128, -74.0060];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Location History{vehicleId ? ` - Vehicle ${vehicleId}` : ''}</h1>
      </div>
      
      <div className="filters-section">
        <div className="filter-group">
          <label>From Date:</label>
          <input type="datetime-local" value={fromDate} onChange={(e) => setFromDate(e.target.value)} className="filter-input" />
        </div>
        <div className="filter-group">
          <label>To Date:</label>
          <input type="datetime-local" value={toDate} onChange={(e) => setToDate(e.target.value)} className="filter-input" />
        </div>
        <button onClick={() => { setFromDate(''); setToDate('') }} className="btn-secondary">Clear Filters</button>
      </div>

      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="loading">Loading locations...</div>
      ) : (
        <div className="locations-table-container">
          
          {/* قسم الخريطة الجديد */}
          {locations.length > 0 && (
            <div className="map-wrapper">
              <h3>Route Map</h3>
              <MapContainer center={mapCenter} zoom={13} scrollWheelZoom={true} className="history-map">
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; OpenStreetMap contributors'
                />
                <Polyline positions={polylinePositions} color="red" weight={3} opacity={0.7} />
                
                {/* وضع Marker فقط على أول وآخر نقطة لعدم زحام الخريطة */}
                <Marker position={polylinePositions[0]}>
                  <Popup>Start Point <br/> {new Date(locations[0].recorded_at).toLocaleString()}</Popup>
                </Marker>
                <Marker position={polylinePositions[polylinePositions.length - 1]}>
                  <Popup>Current/Last Point <br/> {new Date(locations[locations.length-1].recorded_at).toLocaleString()}</Popup>
                </Marker>
              </MapContainer>
            </div>
          )}

          <table className="locations-table">
            <thead>
              <tr>
                <th>Vehicle</th>
                <th>Latitude</th>
                <th>Longitude</th>
                <th>Speed (km/h)</th>
                <th>Source</th>
                <th>Recorded At</th>
              </tr>
            </thead>
            <tbody>
              {locations.length === 0 ? (
                <tr><td colSpan="6">No location data found</td></tr>
              ) : (
                locations.map((location) => (
                  <tr key={location.id}>
                    <td>{location.vehicle_info?.plate || location.vehicle}</td>
                    <td>{location.lat}</td>
                    <td>{location.lng}</td>
                    <td>{location.speed || 'N/A'}</td>
                    <td>{location.source}</td>
                    <td>{new Date(location.recorded_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default LocationsHistory