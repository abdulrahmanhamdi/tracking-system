import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import api from '../api/axios'
import './Auth.css'

function ResetPassword() {
  const [searchParams] = useSearchParams()
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const token = searchParams.get('token')

  useEffect(() => {
    if (!token) {
      setError('Reset token is missing')
    }
  }, [token])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')

    if (password !== password2) {
      setError('Passwords do not match')
      return
    }

    if (!token) {
      setError('Reset token is required')
      return
    }

    setLoading(true)

    try {
      await api.post('/auth/reset-password/', {
        token,
        new_password: password
      })
      setMessage('Password has been reset successfully.')
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      const errorData = err.response?.data
      if (typeof errorData === 'object') {
        const errorMessages = Object.values(errorData).flat()
        setError(errorMessages.join(', '))
      } else {
        setError(errorData?.error || 'Failed to reset password')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Reset Password</h1>
        <form onSubmit={handleSubmit}>
          {message && <div className="success-message">{message}</div>}
          {error && <div className="error-message">{error}</div>}
          <div className="form-group">
            <label>New Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading || !token}
            />
          </div>
          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              required
              disabled={loading || !token}
            />
          </div>
          <button type="submit" className="submit-btn" disabled={loading || !token}>
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
        <div className="auth-links">
          <a href="/login">Back to Login</a>
        </div>
      </div>
    </div>
  )
}

export default ResetPassword
