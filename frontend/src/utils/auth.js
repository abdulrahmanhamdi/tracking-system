/**
 * Authentication utilities
 * 
 * SECURITY NOTE: localStorage is used for JWT tokens in development.
 * In production, consider using httpOnly cookies or secure storage mechanisms
 * to prevent XSS attacks from accessing tokens.
 */

export const getToken = () => {
  return localStorage.getItem('access_token')
}

export const setTokens = (access, refresh) => {
  localStorage.setItem('access_token', access)
  if (refresh) {
    localStorage.setItem('refresh_token', refresh)
  }
}

export const removeTokens = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export const isAuthenticated = () => {
  return !!getToken()
}

export const getUser = async () => {
  const token = getToken()
  if (!token) return null
  
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/me/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      return await response.json()
    }
  } catch (error) {
    console.error('Error fetching user:', error)
  }
  return null
}

