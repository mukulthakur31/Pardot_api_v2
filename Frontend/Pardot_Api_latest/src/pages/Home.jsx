import React from 'react'
import './Home.css'

const Home = () => {
  const handleSalesforceLogin = () => {
    window.location.href = 'http://localhost:4001/login'
  }

  return (
    <div className="home-container">
      <div className="home-background">
        <div className="background-pattern"></div>
      </div>
      
      <div className="home-content">
        <div className="login-card">
          <div className="brand-section">
            <div className="brand-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm5-18v4h3V3h-3z" fill="#00396B"/>
              </svg>
            </div>
            <h1 className="brand-title">Pardot Analytics</h1>
            <p className="brand-subtitle">Comprehensive Marketing Analytics & Insights</p>
          </div>
          
          <div className="login-section">
            <div className="login-info">
              <h2>Welcome Back</h2>
              <p>Connect with your Salesforce account to access your marketing analytics dashboard</p>
            </div>
            
            <button
              onClick={handleSalesforceLogin}
              className="salesforce-login-btn"
            >
              Continue with Salesforce
            </button>
            
            <div className="security-note">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.4 16,13V16C16,17.4 15.4,18 14.8,18H9.2C8.6,18 8,17.4 8,16V13C8,12.4 8.6,11.5 9.2,11.5V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.5,8.7 10.5,10V11.5H13.5V10C13.5,8.7 12.8,8.2 12,8.2Z"/>
              </svg>
              Secure OAuth 2.0 Authentication
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home