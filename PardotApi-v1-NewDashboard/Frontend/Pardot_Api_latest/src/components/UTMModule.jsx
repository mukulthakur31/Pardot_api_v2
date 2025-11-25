import React, { useState } from 'react'
import { useGoogleAuth } from '../pages/Dashboard'
import './EmailModule.css'
import './UTMModule.css'

const UTMModule = () => {
  const [utmData, setUtmData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState({ sheets: false, pdf: false })
  const [error, setError] = useState('')
  const { googleAuth, handleGoogleAuth } = useGoogleAuth()

  const fetchUtmAnalysis = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch('http://localhost:4001/get-utm-analysis', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setUtmData(data.utm_analysis)
      } else {
        setError('Failed to fetch UTM analysis')
      }
    } catch (error) {
      setError('Error fetching UTM analysis: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const exportToSheets = async () => {
    if (!googleAuth) {
      try {
        await handleGoogleAuth()
      } catch (error) {
        setError('Google authentication failed')
      }
      return
    }

    setExporting(prev => ({ ...prev, sheets: true }))
    try {
      const exportData = utmData ? utmData.export_data : []

      const response = await fetch('http://localhost:4001/export-to-sheets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: `UTM Analysis Report - ${new Date().toLocaleDateString()}`,
          data: exportData
        })
      })

      const result = await response.json()
      if (result.success) {
        window.open(result.url, '_blank')
      } else {
        setError('Export to sheets failed')
      }
    } catch (error) {
      setError('Export failed: ' + error.message)
    } finally {
      setExporting(prev => ({ ...prev, sheets: false }))
    }
  }

  const downloadPDF = async () => {
    setExporting(prev => ({ ...prev, pdf: true }))
    try {
      const response = await fetch('http://localhost:4001/download-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          data_type: 'utm_analysis',
          data: utmData
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `utm-analysis-report-${new Date().toISOString().split('T')[0]}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        setError('PDF download failed')
      }
    } catch (error) {
      setError('PDF download failed: ' + error.message)
    } finally {
      setExporting(prev => ({ ...prev, pdf: false }))
    }
  }

  return (
    <div className="email-module">
      <div className="module-header">
        <div className="header-content">
          <h2>🎯 UTM Analytics</h2>
          <p>Analyze UTM parameters and identify prospects with missing UTM fields</p>
        </div>
      </div>

      {/* Control Section */}
      <div className="filter-section">
        <div className="filter-controls">
          <button 
            className="fetch-btn"
            onClick={fetchUtmAnalysis}
            disabled={loading}
          >
            {loading ? '🔄 Loading...' : '🎯 Analyze UTM Fields'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* UTM Analysis Results */}
      {utmData ? (
        <>
          {/* UTM Summary */}
          <div className="summary-section">
            <div className="summary-header">
              <h3>🎯 UTM Analysis Overview</h3>
              <div className="export-controls">
                <button 
                  className="export-btn sheets"
                  onClick={exportToSheets}
                  disabled={exporting.sheets}
                >
                  {exporting.sheets ? '🔄 Exporting...' : '📊 Export to Sheets'}
                  {!googleAuth && <span className="auth-required">*Auth Required</span>}
                </button>
                <button 
                  className="export-btn pdf"
                  onClick={downloadPDF}
                  disabled={exporting.pdf}
                >
                  {exporting.pdf ? '🔄 Generating...' : '📄 Download PDF'}
                </button>
              </div>
            </div>
            
            <div className="summary-grid">
              <div className="summary-card primary">
                <div className="summary-content">
                  <div className="summary-value">{utmData.total_prospects_analyzed}</div>
                  <div className="summary-label">Total Prospects Analyzed</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{utmData.prospects_with_utm_issues}</div>
                  <div className="summary-label">Prospects with Missing UTM</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">
                    {utmData.total_prospects_analyzed > 0 
                      ? ((utmData.prospects_with_utm_issues / utmData.total_prospects_analyzed) * 100).toFixed(1)
                      : 0}%
                  </div>
                  <div className="summary-label">Missing UTM Rate</div>
                </div>
              </div>
            </div>
          </div>

          {/* UTM Issues Table */}
          {utmData.utm_issues && utmData.utm_issues.length > 0 && (
            <div className="results-section">
              <div className="results-header">
                <h3>🔍 Prospects with Missing UTM Fields ({utmData.utm_issues.length} shown)</h3>
              </div>
              
              <div className="table-container">
                <table className="campaigns-table">
                  <thead>
                    <tr>
                      <th>Prospect ID</th>
                      <th>Email</th>
                      <th>UTM Campaign</th>
                      <th>UTM Medium</th>
                      <th>UTM Source</th>
                      <th>UTM Term</th>
                    </tr>
                  </thead>
                  <tbody>
                    {utmData.utm_issues.map((issue, index) => (
                      <tr key={index}>
                        <td className="campaign-name">{issue.prospect_id}</td>
                        <td className="campaign-subject">{issue.email}</td>
                        <td>
                          <span className={`rate-badge ${issue.missing_fields.includes('utm_campaign__c') ? 'missing' : 'present'}`}>
                            {issue.missing_fields.includes('utm_campaign__c') ? '❌ Missing' : '✅ Present'}
                          </span>
                        </td>
                        <td>
                          <span className={`rate-badge ${issue.missing_fields.includes('utm_medium__c') ? 'missing' : 'present'}`}>
                            {issue.missing_fields.includes('utm_medium__c') ? '❌ Missing' : '✅ Present'}
                          </span>
                        </td>
                        <td>
                          <span className={`rate-badge ${issue.missing_fields.includes('utm_source__c') ? 'missing' : 'present'}`}>
                            {issue.missing_fields.includes('utm_source__c') ? '❌ Missing' : '✅ Present'}
                          </span>
                        </td>
                        <td>
                          <span className={`rate-badge ${issue.missing_fields.includes('utm_term__c') ? 'missing' : 'present'}`}>
                            {issue.missing_fields.includes('utm_term__c') ? '❌ Missing' : '✅ Present'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      ) : !loading && (
        <div className="empty-state">
          <div className="empty-icon">🎯</div>
          <h3>No UTM Data</h3>
          <p>Click "Analyze UTM Fields" to fetch prospects with missing UTM parameters</p>
        </div>
      )}
    </div>
  )
}

export default UTMModule