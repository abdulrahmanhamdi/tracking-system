import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
// 1. استيراد المزود الذي أنشأناه (تأكد من وجود الملف في هذا المسار)
import { AuthProvider } from './context/AuthContext' 

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
    // 2. تغليف التطبيق بالكامل بـ AuthProvider
    // هذا يسمح باستخدام useAuth() في أي صفحة مثل VehicleDetails
    <AuthProvider>
      <Router>
        <Routes>
          {/* 1. المسارات العامة (بدون تسجيل دخول) */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />

          {/* 2. المسارات المحمية (تحت بادئة /app لضمان عمل القوائم القديمة) */}
          <Route path="/app" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Dashboard />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="vehicles" element={<Vehicles />} />
            <Route path="vehicles/:id" element={<VehicleDetails />} />
            <Route path="locations/:vehicleId" element={<LocationsHistory />} />
            <Route path="locations" element={<LocationsHistory />} />
            <Route path="live" element={<LiveTracking />} />
            <Route path="planning" element={<Planning />} />
            <Route path="admin" element={<AdminPanel />} />
          </Route>

          {/* 3. حل مشكلة الروابط المباشرة (مثل /vehicles/5 التي ظهرت في الكونسول) */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="vehicles" element={<Vehicles />} />
            <Route path="vehicles/:id" element={<VehicleDetails />} />
            <Route path="locations" element={<LocationsHistory />} />
            <Route path="locations/:vehicleId" element={<LocationsHistory />} />
            <Route path="live" element={<LiveTracking />} />
            <Route path="planning" element={<Planning />} />
            <Route path="admin" element={<AdminPanel />} />
          </Route>

          {/* 4. معالجة الصفحات غير الموجودة */}
          <Route path="*" element={
            <div style={{padding: "20px", textAlign: "center"}}>
              <h1>404</h1>
              <p>Page Not Found</p>
              <a href="/dashboard">Back to Dashboard</a>
            </div>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App