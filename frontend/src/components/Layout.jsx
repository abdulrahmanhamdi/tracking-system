import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { getUser } from '../utils/auth'
import { removeTokens } from '../utils/auth'
import './Layout.css'

function Layout() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const userData = await getUser()
    if (!userData) {
      navigate('/')
      return
    }
    setUser(userData)
  }

  const handleLogout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        // Call logout endpoint
        await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/auth/logout/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({ refresh: refreshToken })
        })
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      removeTokens()
      navigate('/login')
    }
  }

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/app" className="nav-logo">
            Vehicle Tracking
          </Link>
          <ul className="nav-menu">
            <li>
              <Link to="/app">Dashboard</Link>
            </li>
            <li>
              <Link to="/app/vehicles">Vehicles</Link>
            </li>
            <li>
              <Link to="/app/live">Live Tracking</Link>
            </li>
            <li>
              <Link to="/app/locations">Locations History</Link>
            </li>
            <li>
              <Link to="/app/planning">Planning</Link>
            </li>
            {user?.role === 'ADMIN' && (
              <li>
                <Link to="/app/admin">Admin</Link>
              </li>
            )}
            <li>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </li>
          </ul>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
