import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Dashboard from './pages/Dashboard'
import Vehicles from './pages/Vehicles'
import VehicleDetails from './pages/VehicleDetails'
import LocationsHistory from './pages/LocationsHistory'
import LiveTracking from './pages/LiveTracking'
import Planning from './pages/Planning'
import AdminPanel from './pages/AdminPanel'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/app" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Dashboard />} />
          <Route path="vehicles" element={<Vehicles />} />
          <Route path="vehicles/:id" element={<VehicleDetails />} />
          <Route path="locations/:vehicleId" element={<LocationsHistory />} />
          <Route path="locations" element={<LocationsHistory />} />
          <Route path="live" element={<LiveTracking />} />
          <Route path="planning" element={<Planning />} />
          <Route path="admin" element={<AdminPanel />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App

