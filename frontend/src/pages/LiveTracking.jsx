import { useEffect, useState, useRef } from 'react'
import api from '../api/axios'
import { getToken } from '../utils/auth'
import './LiveTracking.css'

// استيراد مكتبة الخرائط
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// إصلاح مشكلة ظهور أيقونات Leaflet مع Vite/React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

// مكون فرعي للتحكم في الخريطة (التركيز والزووم تلقائياً)
function RecenterMap({ position }) {
    const map = useMap();
    useEffect(() => {
        if (position) {
            map.setView(position, map.getZoom());
        }
    }, [position, map]);
    return null;
}

function LiveTracking() {
    const [vehicles, setVehicles] = useState([])
    const [selectedVehicle, setSelectedVehicle] = useState(null)
    const [currentLocation, setCurrentLocation] = useState(null)
    const [pathHistory, setPathHistory] = useState([]) // لحفظ المسار المقطوع
    const [connectionStatus, setConnectionStatus] = useState('disconnected')
    const [error, setError] = useState('')
    const wsRef = useRef(null)
    const reconnectTimeoutRef = useRef(null)
    const reconnectAttempts = useRef(0)
    const maxReconnectAttempts = 10
    const baseReconnectDelay = 1000

    useEffect(() => {
        fetchVehicles()
        return () => {
            if (wsRef.current) wsRef.current.close()
            if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
        }
    }, [])

    useEffect(() => {
        if (selectedVehicle) {
            setPathHistory([]); // تصفير المسار عند تغيير السيارة
            connectWebSocket(selectedVehicle)
        } else {
            disconnectWebSocket()
        }
        return () => disconnectWebSocket()
    }, [selectedVehicle])

    const fetchVehicles = async () => {
        try {
            const response = await api.get('/vehicles/')
            setVehicles(response.data.results || response.data)
        } catch (err) {
            setError('Failed to load vehicles')
        }
    }

    const connectWebSocket = (vehicleId) => {
        disconnectWebSocket()
        const token = getToken()
        if (!token) {
            setError('Not authenticated')
            return
        }
    
        // المسار يطابق backend/core/routing.py
        const wsUrl = `${WS_URL}/ws/tracking/live/?vehicle_id=${vehicleId}&token=${token}`
        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
            setConnectionStatus('connected')
            setError('')
            reconnectAttempts.current = 0
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                if (data.type === 'location') {
                    setCurrentLocation(data)
                    setPathHistory(prev => [...prev, [data.lat, data.lng]])
                } else if (data.type === 'status') {
                    // تحديث الحالة بناءً على رسائل الـ Consumer
                    setConnectionStatus(data.streaming ? 'connected' : 'paused')
                }
            } catch (err) {
                console.error('Error parsing WebSocket message:', err)
            }
        }

        ws.onerror = () => {
            setError('WebSocket connection error')
            setConnectionStatus('error')
        }

        ws.onclose = () => {
            setConnectionStatus('disconnected')
            if (selectedVehicle && reconnectAttempts.current < maxReconnectAttempts) {
                scheduleReconnect(vehicleId)
            }
        }
    }

    const scheduleReconnect = (vehicleId) => {
        const delay = Math.min(baseReconnectDelay * Math.pow(2, reconnectAttempts.current), 30000)
        reconnectAttempts.current++
        reconnectTimeoutRef.current = setTimeout(() => connectWebSocket(vehicleId), delay)
    }

    const disconnectWebSocket = () => {
        if (wsRef.current) {
            wsRef.current.close()
            wsRef.current = null
        }
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
            reconnectTimeoutRef.current = null
        }
        setConnectionStatus('disconnected')
        reconnectAttempts.current = 0
    }

    const handleVehicleChange = (e) => {
        const vehicleId = e.target.value
        setSelectedVehicle(vehicleId || null)
        setCurrentLocation(null)
    }

    // جلب بيانات السيارة المختارة لعرضها في الخريطة
    const selectedVehicleData = vehicles.find(v => v.id === parseInt(selectedVehicle));

    return (
        <div className="page-container">
            <div className="page-header">
                <h1>Live Tracking</h1>
                <div className="connection-status">
                    <span className={`status-indicator ${connectionStatus}`}>
                        {connectionStatus === 'connected' && '● Connected'}
                        {connectionStatus === 'disconnected' && '○ Disconnected'}
                        {connectionStatus === 'paused' && '◐ Paused'}
                        {connectionStatus === 'error' && '⚠ Error'}
                    </span>
                </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="tracking-container">
                <div className="vehicle-selector-panel">
                    <h3>Select Vehicle</h3>
                    <select
                        value={selectedVehicle || ''}
                        onChange={handleVehicleChange}
                        className="vehicle-select"
                    >
                        <option value="">-- Select a vehicle --</option>
                        {vehicles.map((v) => (
                            <option key={v.id} value={v.id}>
                                {v.plate} - {v.brand} {v.model}
                            </option>
                        ))}
                    </select>

                    {currentLocation && (
                        <div className="location-info-card" style={{marginTop: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '8px'}}>
                            <h4>Current Stats</h4>
                            <p><strong>Speed:</strong> {currentLocation.speed} km/h</p>
                            <p><strong>Heading:</strong> {currentLocation.heading}°</p>
                            <p><strong>Update:</strong> {new Date(currentLocation.recorded_at).toLocaleTimeString()}</p>
                        </div>
                    )}
                </div>

                <div className="tracking-content">
                    <div className="map-wrapper" style={{ height: '500px', width: '100%', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
                        <MapContainer 
                            center={[41.0082, 28.9784]} // تم التعديل إلى إسطنبول
                            zoom={13} 
                            style={{ height: '100%', width: '100%' }}
                        >
                            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                            
                            {currentLocation && (
                                <>
                                    <RecenterMap position={[currentLocation.lat, currentLocation.lng]} />
                                    <Polyline positions={pathHistory} color="blue" weight={4} opacity={0.6} />
                                    <Marker position={[currentLocation.lat, currentLocation.lng]}>
                                        <Popup>
                                            <strong>Plate: {selectedVehicleData?.plate}</strong><br />
                                            Vehicle: {selectedVehicleData?.brand} {selectedVehicleData?.model}<br />
                                            Speed: {currentLocation.speed} km/h
                                        </Popup>
                                    </Marker>
                                </>
                            )}
                        </MapContainer>
                    </div>

                    {!selectedVehicle && (
                        <div className="no-selection-overlay">
                            <p>Select a vehicle from the list to begin real-time tracking.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default LiveTracking