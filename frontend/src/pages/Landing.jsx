import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { setTokens } from '../utils/auth'
import './Landing.css'

function Landing() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleDemoLogin = async (email, password) => {
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/auth/login/', {
        email,
        password,
      })
      const { access, refresh } = response.data
      setTokens(access, refresh)
      navigate('/app')
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.message || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="landing-container">
      <div className="landing-content">
        <h1>Vehicle Tracking & Planning System</h1>
        <p className="subtitle">Demo Application</p>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="demo-buttons">
          <button
            className="demo-btn admin-btn"
            onClick={() => handleDemoLogin('admin@example.com', 'Admin1234!')}
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login as Admin'}
          </button>
          <button
            className="demo-btn user-btn"
            onClick={() => handleDemoLogin('user@example.com', 'User1234!')}
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login as User'}
          </button>
        </div>
        
        <div className="landing-links">
          <a href="/login">Manual Login</a>
          <a href="/register">Register</a>
        </div>
        
        <div className="demo-info">
          <h3>Demo Credentials:</h3>
          <div className="credentials">
            <div>
              <strong>Admin:</strong> admin@example.com / Admin1234!
            </div>
            <div>
              <strong>User:</strong> user@example.com / User1234!
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Landing

