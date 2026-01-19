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
  const [generatingReport, setGeneratingReport] = useState(false)
  const [reportSuccess, setReportSuccess] = useState(false)
  const [requestInProgress, setRequestInProgress] = useState(false)
  const [requestTimeout, setRequestTimeout] = useState(null)

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
      const response = await fetch('http://localhost:4001/auth-status', {
        credentials: 'include'
      })
      
      const data = await response.json()
      
      if (data.authenticated) {
        setPardotConnected(true)
      } else {
        console.log('Auth failed:', data.reason)
        setPardotConnected(false)
        // Don't navigate away, just show the button as disabled
      }
    } catch (error) {
      console.error('Auth check error:', error)
      setPardotConnected(false)
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

  const generateFullReport = async () => {
    setGeneratingReport(true)
    try {
      const response = await fetch('http://localhost:4001/download-summary-pdf', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
        throw new Error(errorData.error || 'Failed to generate report')
      }
      
      // Create blob and download
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `pardot-comprehensive-report-${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      // Show success message
      setReportSuccess(true)
      setTimeout(() => setReportSuccess(false), 3000)
    } catch (error) {
      console.error('Error generating report:', error)
      alert(`Failed to generate report: ${error.message}`)
    } finally {
      setGeneratingReport(false)
    }
  }

  // Request management functions
  const startRequest = () => {
    setRequestInProgress(true)
    // Set timeout to auto-cancel after 3 Min
    const timeout = setTimeout(() => {
      setRequestInProgress(false)
      console.log('Request timeout - navigation enabled')
    }, 1800000)
    setRequestTimeout(timeout)
  }

  const endRequest = () => {
    setRequestInProgress(false)
    if (requestTimeout) {
      clearTimeout(requestTimeout)
      setRequestTimeout(null)
    }
  }

  // Context value
  const googleAuthValue = {
    googleAuth: googleConnected,
    loading,
    handleGoogleAuth,
    disconnectGoogle,
    refreshAuthStatus: checkGoogleAuthStatus,
    requestInProgress,
    startRequest,
    endRequest
  }

  const modules = [
    { id: 'emails', name: '📧 Email Campaigns', path: '/dashboard/emails' },
    { id: 'forms', name: '📝 Forms Analysis', path: '/dashboard/forms' },
    { id: 'prospects', name: '👥 Prospect Health', path: '/dashboard/prospects' },
    { id: 'landing-pages', name: '🚀 Landing Pages', path: '/dashboard/landing-pages' },
    { id: 'engagement', name: '🎯 Engagement Studio', path: '/dashboard/engagement' },
    { id: 'utm', name: '📊 Field Analysis', path: '/dashboard/utm' }
  ]

  return (
    <GoogleAuthContext.Provider value={googleAuthValue}>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
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
            width: '48px', 
            height: '48px', 
            background: 'linear-gradient(135deg, #00396B, #0176D3)', 
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '1.75rem',
            fontWeight: '800',
            boxShadow: '0 4px 12px rgba(1, 118, 211, 0.3)',
            letterSpacing: '-0.02em'
          }}>P</div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <h1 style={{ 
              fontSize: '2rem', 
              fontWeight: '800', 
              color: '#00396B', 
              margin: 0, 
              lineHeight: 1,
              letterSpacing: '-0.02em'
            }}>
              Pardot<span style={{color:"#00A1E0", fontWeight: '800'}}>S</span>can
            </h1>
            <p style={{ 
              fontSize: '0.7rem', 
              color: '#706E6B', 
              margin: 0, 
              lineHeight: 1,
              marginTop: '0.25rem',
              letterSpacing: '0.08em',
              textAlign: 'center',
              fontWeight: '500'
            }}>Scan. Diagnose. Optimize.</p>
          </div>
        </div>

        {/* Connection Status & Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', position: 'relative' }}>
          {/* Success Message */}
          {reportSuccess && (
            <div style={{
              position: 'absolute',
              top: '100%',
              right: '0',
              marginTop: '0.5rem',
              background: '#10B981',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontSize: '0.85rem',
              fontWeight: '600',
              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
              zIndex: 1000,
              whiteSpace: 'nowrap'
            }}>
              ✅ Report generated successfully!
            </div>
          )}

          {/* Pardot Status */}
          {!pardotConnected ? (
            <button
              onClick={() => window.location.href = 'http://localhost:4001/login'}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 1rem',
                borderRadius: '6px',
                background: '#DC2626',
                border: 'none',
                color: 'white',
                fontSize: '0.85rem',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#ffffff'
              }}></div>
              Login to Salesforce
            </button>
          ) : (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              background: '#E8F4FD',
              border: '1px solid #B8E6FF',
              color: '#00396B',
              fontSize: '0.9rem',
              fontWeight: '700'
            }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#01d32fff'
              }}></div>
              Salesforce Connected
            </div>
          )}

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
              fontSize: '0.9rem',
              fontWeight: '700',
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
          boxShadow: '1px 0 3px rgba(0,0,0,0.05)',
          overflowY: 'auto',
          overflowX: 'hidden'
        }}>
          <h3 style={{
            fontSize: '1.1rem',
            fontWeight: '800',
            color: '#00396B',
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
                onClick={() => !requestInProgress && navigate(module.path)}
                disabled={requestInProgress}
                style={{
                  width: '100%',
                  padding: '0.875rem 1rem',
                  margin: '0.25rem 0',
                  border: activeModule === module.id ? '1px solid #0176D3' : '1px solid transparent',
                  borderRadius: '6px',
                  background: requestInProgress ? '#F3F4F6' : (activeModule === module.id ? '#E8F4FD' : 'transparent'),
                  color: requestInProgress ? '#9CA3AF' : (activeModule === module.id ? '#00396B' : '#706E6B'),
                  cursor: requestInProgress ? 'not-allowed' : 'pointer',
                  fontSize: '1rem',
                  fontWeight: '700',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  opacity: requestInProgress ? 0.6 : 1
                }}
                onMouseOver={(e) => {
                  if (activeModule !== module.id && !requestInProgress) {
                    e.target.style.background = '#F7F9FB'
                    e.target.style.color = '#00396B'
                  }
                }}
                onMouseOut={(e) => {
                  if (activeModule !== module.id && !requestInProgress) {
                    e.target.style.background = 'transparent'
                    e.target.style.color = '#706E6B'
                  }
                }}
              >
                {module.name}
                {requestInProgress && activeModule === module.id && (
                  <div style={{
                    width: '12px',
                    height: '12px',
                    border: '2px solid #9CA3AF',
                    borderTop: '2px solid #0176D3',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                    display: 'inline-block',
                    marginLeft: '0.5rem'
                  }}></div>
                )}
              </button>
            ))}
            
            {/* Sidebar Full Report Button */}
            <div style={{ marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid #E5E5E5' }}>
              <button
                onClick={generateFullReport}
                disabled={generatingReport || !pardotConnected || requestInProgress}
                style={{
                  width: '100%',
                  padding: '0.875rem 1rem',
                  margin: '0.25rem 0',
                  border: 'none',
                  borderRadius: '8px',
                  background: (generatingReport || requestInProgress) ? '#9CA3AF' : 'linear-gradient(135deg, #7C3AED, #A855F7)',
                  color: 'white',
                  cursor: (generatingReport || !pardotConnected || requestInProgress) ? 'not-allowed' : 'pointer',
                  fontSize: '1rem',
                  fontWeight: '800',
                  textAlign: 'center',
                  transition: 'all 0.2s ease',
                  boxShadow: '0 2px 4px rgba(124, 58, 237, 0.2)',
                  opacity: requestInProgress ? 0.6 : 1
                }}
                onMouseOver={(e) => {
                  if (!generatingReport && pardotConnected && !requestInProgress) {
                    e.target.style.transform = 'translateY(-1px)'
                    e.target.style.boxShadow = '0 4px 8px rgba(124, 58, 237, 0.3)'
                  }
                }}
                onMouseOut={(e) => {
                  if (!generatingReport && pardotConnected && !requestInProgress) {
                    e.target.style.transform = 'translateY(0px)'
                    e.target.style.boxShadow = '0 2px 4px rgba(124, 58, 237, 0.2)'
                  }
                }}
              >
                {generatingReport ? (
                  <>
                    <div style={{
                      width: '14px',
                      height: '14px',
                      border: '2px solid #ffffff',
                      borderTop: '2px solid transparent',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite',
                      display: 'inline-block',
                      marginRight: '0.5rem'
                    }}></div>
                    Generating...
                  </>
                ) : requestInProgress ? (
                  '⏳ Request in Progress'
                ) : (
                  '📊 Generate Full Report'
                )}
              </button>
              {!pardotConnected && (
                <button
                  onClick={() => window.location.href = 'http://localhost:4001/login'}
                  style={{
                    width: '100%',
                    padding: '0.5rem 1rem',
                    margin: '0.5rem 0',
                    border: '1px solid #0176D3',
                    borderRadius: '6px',
                    background: 'transparent',
                    color: '#0176D3',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    fontWeight: '600',
                    textAlign: 'center'
                  }}
                >
                  🔐 Login to Salesforce
                </button>
              )}
              <p style={{
                fontSize: '0.7rem',
                color: '#9CA3AF',
                textAlign: 'center',
                margin: '0.5rem 0 0 0',
                lineHeight: 1.3
              }}>
                {!pardotConnected ? 'Connect to Salesforce first' : 'Comprehensive PDF with all analytics'}
              </p>
            </div>
          </nav>
        </aside>

        {/* Main Content */}
        <main style={{
          flex: 1,
          padding: '2rem',
          background: '#F7F9FB',
          overflowY: 'auto',
          overflowX: 'hidden',
          height: 'calc(100vh - 81px)'
        }}>
          <Outlet />
        </main>
      </div>
    </div>
    </GoogleAuthContext.Provider>
  )
}

export default Dashboard