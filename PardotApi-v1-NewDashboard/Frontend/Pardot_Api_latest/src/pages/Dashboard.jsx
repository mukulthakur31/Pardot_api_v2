import React, { useState, useEffect, createContext, useContext } from 'react'
import { useNavigate, Outlet, useLocation } from 'react-router-dom'

// Create Google Auth Context
const GoogleAuthContext = createContext()

export const useGoogleAuth = () => {
  const context = useContext(GoogleAuthContext)
  if (!context) {
    throw new Error('useGoogleAuth must be used within Dashboard')
  }
  return context
}

const Dashboard = () => {
  const [pardotConnected, setPardotConnected] = useState(false)
  const [googleConnected, setGoogleConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const location = useLocation()
  
  // Get active module from URL
  const activeModule = location.pathname.split('/')[2] || 'emails'

  useEffect(() => {
    checkAuth()
    checkGoogleAuthStatus()
    
    // Check for Google auth callback
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.get('google_auth') === 'success') {
      setGoogleConnected(true)
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [])

  const checkAuth = async () => {
    try {
      const response = await fetch('http://localhost:4001/check-auth', {
        credentials: 'include'
      })
      
      if (!response.ok) {
        navigate('/')
        return
      }
      
      setPardotConnected(true)
    } catch (error) {
      navigate('/')
    }
  }

  const checkGoogleAuthStatus = async () => {
    try {
      const response = await fetch('http://localhost:4001/google-auth-status', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setGoogleConnected(data.authenticated)
      }
    } catch (error) {
      console.error('Error checking Google auth:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleAuth = async () => {
    try {
      const response = await fetch('http://localhost:4001/google-auth', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        window.location.href = data.auth_url
      }
    } catch (error) {
      console.error('Error connecting to Google:', error)
      throw error
    }
  }

  const disconnectGoogle = async () => {
    try {
      const response = await fetch('http://localhost:4001/google-disconnect', {
        method: 'POST',
        credentials: 'include'
      })
      
      if (response.ok) {
        setGoogleConnected(false)
      }
    } catch (error) {
      console.error('Error disconnecting Google:', error)
      throw error
    }
  }



  const handleGoogleConnect = async () => {
    try {
      if (googleConnected) {
        await disconnectGoogle()
      } else {
        await handleGoogleAuth()
      }
    } catch (error) {
      console.error('Google auth error:', error)
    }
  }

  // Context value
  const googleAuthValue = {
    googleAuth: googleConnected,
    loading,
    handleGoogleAuth,
    disconnectGoogle,
    refreshAuthStatus: checkGoogleAuthStatus
  }

  const modules = [
    { id: 'emails', name: '📧 Email Campaigns', path: '/dashboard/emails' },
    { id: 'forms', name: '📝 Forms Analysis', path: '/dashboard/forms' },
    { id: 'prospects', name: '👥 Prospect Health', path: '/dashboard/prospects' },
    { id: 'landing-pages', name: '🚀 Landing Pages', path: '/dashboard/landing-pages' },
    { id: 'engagement', name: '🎯 Engagement', path: '/dashboard/engagement' },
    { id: 'utm', name: '📊 UTM Analysis', path: '/dashboard/utm' }
  ]

  return (
    <GoogleAuthContext.Provider value={googleAuthValue}>
      <div style={{ minHeight: '100vh', background: '#F7F9FB' }}>
      {/* Header */}
      <header style={{
        background: '#FFFFFF',
        borderBottom: '1px solid #E5E5E5',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            background: 'linear-gradient(135deg, #00396B, #0176D3)', 
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '1.25rem',
            fontWeight: 'bold'
          }}>P</div>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#00396B', margin: 0, lineHeight: 1 }}>
              Pardot Analytics
            </h1>
            <p style={{ fontSize: '0.75rem', color: '#706E6B', margin: 0, lineHeight: 1 }}>Marketing Intelligence</p>
          </div>
        </div>

        {/* Connection Status & Logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Pardot Status */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            background: pardotConnected ? '#E8F4FD' : '#FEF2F2',
            border: `1px solid ${pardotConnected ? '#B8E6FF' : '#FECACA'}`,
            color: pardotConnected ? '#00396B' : '#DC2626',
            fontSize: '0.85rem',
            fontWeight: '600'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: pardotConnected ? '#01d32fff' : '#EF4444'
            }}></div>
            Salesforce
          </div>

          {/* Google Connect/Disconnect Button */}
          <button
            onClick={handleGoogleConnect}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: googleConnected ? '#059669' : '#0176D3',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: '600',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.background = googleConnected ? '#047857' : '#014486'
            }}
            onMouseOut={(e) => {
              e.target.style.background = googleConnected ? '#059669' : '#0176D3'
            }}
          >
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: googleConnected ? '#E8F4FD' : '#ffffff'
            }}></div>
            {googleConnected ? 'Disconnect Google' : 'Connect Google'}
          </button>
        </div>
      </header>

      <div style={{ display: 'flex' }}>
        {/* Sidebar */}
        <aside style={{
          width: '280px',
          background: '#FFFFFF',
          minHeight: 'calc(100vh - 81px)',
          padding: '1.5rem 1rem',
          borderRight: '1px solid #E5E5E5',
          boxShadow: '1px 0 3px rgba(0,0,0,0.05)'
        }}>
          <h3 style={{
            fontSize: '0.9rem',
            fontWeight: '700',
            color: '#706E6B',
            marginBottom: '1.5rem',
            textAlign: 'left',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            paddingLeft: '1rem'
          }}>
            Analytics Modules
          </h3>

          <nav>
            {modules.map(module => (
              <button
                key={module.id}
                onClick={() => navigate(module.path)}
                style={{
                  width: '100%',
                  padding: '0.875rem 1rem',
                  margin: '0.25rem 0',
                  border: activeModule === module.id ? '1px solid #0176D3' : '1px solid transparent',
                  borderRadius: '6px',
                  background: activeModule === module.id ? '#E8F4FD' : 'transparent',
                  color: activeModule === module.id ? '#00396B' : '#706E6B',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: activeModule === module.id ? '600' : '500',
                  textAlign: 'left',
                  transition: 'all 0.2s ease'
                }}
                onMouseOver={(e) => {
                  if (activeModule !== module.id) {
                    e.target.style.background = '#F7F9FB'
                    e.target.style.color = '#00396B'
                  }
                }}
                onMouseOut={(e) => {
                  if (activeModule !== module.id) {
                    e.target.style.background = 'transparent'
                    e.target.style.color = '#706E6B'
                  }
                }}
              >
                {module.name}
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main style={{
          flex: 1,
          padding: '2rem',
          background: '#F7F9FB'
        }}>
          <Outlet />
        </main>
      </div>
    </div>
    </GoogleAuthContext.Provider>
  )
}

export default Dashboard