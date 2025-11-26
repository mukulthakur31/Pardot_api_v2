import React, { useState } from 'react'
import { useGoogleAuth } from '../pages/Dashboard'
import './EmailModule.css'

const EngagementModule = () => {
  const [engagementData, setEngagementData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState({ sheets: false, pdf: false })
  const [error, setError] = useState('')
  const { googleAuth, handleGoogleAuth } = useGoogleAuth()

  const fetchEngagementPrograms = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch('http://localhost:4001/get-engagement-programs-analysis', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setEngagementData(data)
      } else {
        setError('Failed to fetch engagement programs')
      }
    } catch (error) {
      setError('Error fetching engagement programs: ' + error.message)
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
      const exportData = formatForExport(engagementData)

      const response = await fetch('http://localhost:4001/export-to-sheets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: `Engagement Programs - ${new Date().toLocaleDateString()}`,
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
          data_type: 'engagement_programs',
          data: engagementData
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `engagement-programs-report-${new Date().toISOString().split('T')[0]}.pdf`
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

  const formatForExport = (data) => {
    if (!data) return []
    const allPrograms = [...(data.active_programs || []), ...(data.inactive_programs || []), ...(data.paused_programs || [])]
    return allPrograms.map(program => ({
      'Program ID': program.id,
      'Program Name': program.name,
      'Status': program.status,
      'Is Deleted': program.isDeleted ? 'Yes' : 'No',
      'Created Date': program.createdAt ? new Date(program.createdAt).toLocaleDateString() : 'N/A',
      'Updated Date': program.updatedAt ? new Date(program.updatedAt).toLocaleDateString() : 'N/A',
      'Description': program.description || 'N/A'
    }))
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'Running': return '#10b981'
      case 'Paused': return '#f59e0b'
      case 'Stopped': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const renderEngagementPrograms = () => {
    if (!engagementData) {
      return (
        <div className="empty-state">
          <div className="empty-icon">🎯</div>
          <h3>No Engagement Programs Data</h3>
          <p>Click "Fetch Programs" to load engagement programs</p>
        </div>
      )
    }

    return (
      <>
        {/* Summary Section */}
        <div className="summary-section">
          <div className="summary-header">
            <h3>🎯 Engagement Programs Overview</h3>
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
                <div className="summary-value">{engagementData.summary.total_programs}</div>
                <div className="summary-label">Total Programs</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{engagementData.summary.active_count}</div>
                <div className="summary-label">Active Programs</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{engagementData.summary.inactive_count}</div>
                <div className="summary-label">Inactive Programs</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{engagementData.summary.paused_count}</div>
                <div className="summary-label">Paused Programs</div>
              </div>
            </div>
          </div>
        </div>

        {/* Active Programs */}
        {engagementData.active_programs && engagementData.active_programs.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h3>✅ Active Programs ({engagementData.active_programs.length})</h3>
            </div>
            
            <div className="table-container">
              <table className="campaigns-table">
                <thead>
                  <tr>
                    <th>Program ID</th>
                    <th>Program Name</th>
                    <th>Status</th>
                    <th>Created Date</th>
                    <th>Updated Date</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {engagementData.active_programs.map((program) => (
                    <tr key={program.id}>
                      <td>{program.id}</td>
                      <td className="campaign-name">{program.name}</td>
                      <td>
                        <span 
                          className="rate-badge"
                          style={{ color: getStatusColor(program.status) }}
                        >
                          {program.status}
                        </span>
                      </td>
                      <td>{program.createdAt ? new Date(program.createdAt).toLocaleDateString() : 'N/A'}</td>
                      <td>{program.updatedAt ? new Date(program.updatedAt).toLocaleDateString() : 'N/A'}</td>
                      <td className="campaign-subject">{program.description || 'No description'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Inactive Programs */}
        {engagementData.inactive_programs && engagementData.inactive_programs.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h3>❌ Inactive Programs ({engagementData.inactive_programs.length})</h3>
            </div>
            
            <div className="table-container">
              <table className="campaigns-table">
                <thead>
                  <tr>
                    <th>Program ID</th>
                    <th>Program Name</th>
                    <th>Status</th>
                    <th>Created Date</th>
                    <th>Updated Date</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {engagementData.inactive_programs.map((program) => (
                    <tr key={program.id}>
                      <td>{program.id}</td>
                      <td className="campaign-name">{program.name}</td>
                      <td>
                        <span 
                          className="rate-badge"
                          style={{ color: getStatusColor(program.status) }}
                        >
                          {program.status || 'Unknown'}
                        </span>
                      </td>
                      <td>{program.createdAt ? new Date(program.createdAt).toLocaleDateString() : 'N/A'}</td>
                      <td>{program.updatedAt ? new Date(program.updatedAt).toLocaleDateString() : 'N/A'}</td>
                      <td className="campaign-subject">{program.description || 'No description'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Paused Programs */}
        {engagementData.paused_programs && engagementData.paused_programs.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h3>⏸️ Paused Programs ({engagementData.paused_programs.length})</h3>
            </div>
            
            <div className="table-container">
              <table className="campaigns-table">
                <thead>
                  <tr>
                    <th>Program ID</th>
                    <th>Program Name</th>
                    <th>Status</th>
                    <th>Created Date</th>
                    <th>Updated Date</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {engagementData.paused_programs.map((program) => (
                    <tr key={program.id}>
                      <td>{program.id}</td>
                      <td className="campaign-name">{program.name}</td>
                      <td>
                        <span 
                          className="rate-badge"
                          style={{ color: getStatusColor(program.status) }}
                        >
                          {program.status}
                        </span>
                      </td>
                      <td>{program.createdAt ? new Date(program.createdAt).toLocaleDateString() : 'N/A'}</td>
                      <td>{program.updatedAt ? new Date(program.updatedAt).toLocaleDateString() : 'N/A'}</td>
                      <td className="campaign-subject">{program.description || 'No description'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </>
    )
  }

  return (
    <div className="email-module">
      <div className="module-header">
        <div className="header-content">
          <h2>🎯 Engagement Programs Analytics</h2>
          <p>Analyze engagement program performance and status</p>
        </div>
      </div>

      {/* Controls */}
      <div className="filter-section">
        <div className="filter-controls">
          <button 
            className="fetch-btn"
            onClick={fetchEngagementPrograms}
            disabled={loading}
          >
            {loading ? '🔄 Loading...' : '🎯 Fetch Engagement Programs'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Engagement Programs Content */}
      {renderEngagementPrograms()}
    </div>
  );
};

export default EngagementModule;