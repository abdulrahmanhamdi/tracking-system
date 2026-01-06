import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/axios'
import './Auth.css'

function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    try {
      await api.post('/auth/forgot-password/', { email })
      setMessage('If the email exists, a password reset link has been sent. Check console logs for the reset link (dev mode).')
    } catch (err) {
      // Still show success message for security (don't reveal if email exists)
      setMessage('If the email exists, a password reset link has been sent. Check console logs for the reset link (dev mode).')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Forgot Password</h1>
        <form onSubmit={handleSubmit}>
          {message && <div className="success-message">{message}</div>}
          {error && <div className="error-message">{error}</div>}
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>
        <div className="auth-links">
          <a href="/login">Back to Login</a>
        </div>
      </div>
    </div>
  )
}

export default ForgotPassword
