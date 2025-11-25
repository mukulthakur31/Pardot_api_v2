import React, { useState } from 'react'
import { useGoogleAuth } from '../pages/Dashboard'
import './EmailModule.css'

const EngagementModule = () => {
  const [analysisData, setAnalysisData] = useState(null)
  const [performanceData, setPerformanceData] = useState(null)
  const [loading, setLoading] = useState({ analysis: false, performance: false })
  const [exporting, setExporting] = useState({ sheets: false, pdf: false })
  const [activeTab, setActiveTab] = useState('analysis')
  const [error, setError] = useState('')
  const { googleAuth, handleGoogleAuth } = useGoogleAuth()

  const fetchAnalysis = async () => {
    setLoading(prev => ({ ...prev, analysis: true }))
    setError('')
    
    try {
      const response = await fetch('http://localhost:4001/get-engagement-programs-analysis', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setAnalysisData(data)
      } else {
        setError('Failed to fetch engagement programs analysis')
      }
    } catch (error) {
      setError('Error fetching analysis: ' + error.message)
    } finally {
      setLoading(prev => ({ ...prev, analysis: false }))
    }
  }

  const fetchPerformance = async () => {
    setLoading(prev => ({ ...prev, performance: true }))
    setError('')
    
    try {
      const response = await fetch('http://localhost:4001/get-engagement-programs-performance', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setPerformanceData(data)
      } else {
        setError('Failed to fetch engagement programs performance')
      }
    } catch (error) {
      setError('Error fetching performance: ' + error.message)
    } finally {
      setLoading(prev => ({ ...prev, performance: false }))
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
      const currentData = activeTab === 'analysis' ? analysisData : performanceData
      const exportData = activeTab === 'analysis' 
        ? formatAnalysisForExport(currentData)
        : formatPerformanceForExport(currentData)

      const response = await fetch('http://localhost:4001/export-to-sheets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: `Engagement Programs ${activeTab === 'analysis' ? 'Analysis' : 'Performance'} - ${new Date().toLocaleDateString()}`,
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
          data_type: `engagement_${activeTab}`,
          data: activeTab === 'analysis' ? analysisData : performanceData
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `engagement-${activeTab}-report-${new Date().toISOString().split('T')[0]}.pdf`
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

  const formatAnalysisForExport = (data) => {
    if (!data) return []
    const allPrograms = [...(data.active_programs || []), ...(data.inactive_programs || [])]
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

  const formatPerformanceForExport = (data) => {
    if (!data?.all_programs) return []
    return data.all_programs.map(program => ({
      'Program ID': program.id,
      'Program Name': program.name,
      'Status': program.status,
      'Is Deleted': program.is_deleted ? 'Yes' : 'No',
      'Created Date': program.created_at ? new Date(program.created_at).toLocaleDateString() : 'N/A',
      'Updated Date': program.updated_at ? new Date(program.updated_at).toLocaleDateString() : 'N/A',
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

  const renderAnalysisTab = () => {
    if (!analysisData) {
      return (
        <div className="empty-state">
          <div className="empty-icon">🎯</div>
          <h3>No Analysis Data</h3>
          <p>Click "Fetch Analysis" to analyze engagement programs</p>
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
                <div className="summary-value">{analysisData.summary.total_programs}</div>
                <div className="summary-label">Total Programs</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{analysisData.summary.active_count}</div>
                <div className="summary-label">Active Programs</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{analysisData.summary.inactive_count}</div>
                <div className="summary-label">Inactive Programs</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{analysisData.summary.no_entry_count}</div>
                <div className="summary-label">Paused Programs</div>
              </div>
            </div>
          </div>
        </div>

        {/* Active Programs */}
        {analysisData.active_programs && analysisData.active_programs.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h3>✅ Active Programs ({analysisData.active_programs.length})</h3>
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
                  {analysisData.active_programs.map((program) => (
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
        {analysisData.inactive_programs && analysisData.inactive_programs.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h3>❌ Inactive Programs ({analysisData.inactive_programs.length})</h3>
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
                  {analysisData.inactive_programs.map((program) => (
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
      </>
    )
  }

  const renderPerformanceTab = () => {
    if (!performanceData) {
      return (
        <div className="empty-state">
          <div className="empty-icon">📈</div>
          <h3>No Performance Data</h3>
          <p>Click "Fetch Performance" to get detailed program metrics</p>
        </div>
      )
    }

    return (
      <>
        {/* Performance Summary */}
        <div className="summary-section">
          <div className="summary-header">
            <h3>📈 Performance Overview</h3>
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
                <div className="summary-value">{performanceData.performance_summary.total_programs}</div>
                <div className="summary-label">Total Programs</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{performanceData.top_performers?.length || 0}</div>
                <div className="summary-label">Top Performers</div>
              </div>
            </div>
          </div>
          
          {performanceData.performance_summary.note && (
            <div style={{ 
              background: '#f0f9ff', 
              border: '1px solid #0ea5e9', 
              borderRadius: '8px', 
              padding: '1rem', 
              marginTop: '1rem',
              color: '#0369a1'
            }}>
              ℹ️ {performanceData.performance_summary.note}
            </div>
          )}
        </div>

        {/* All Programs Performance */}
        {performanceData.all_programs && performanceData.all_programs.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h3>📊 All Programs Performance ({performanceData.all_programs.length})</h3>
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
                  {performanceData.all_programs.map((program) => (
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
                      <td>{program.created_at ? new Date(program.created_at).toLocaleDateString() : 'N/A'}</td>
                      <td>{program.updated_at ? new Date(program.updated_at).toLocaleDateString() : 'N/A'}</td>
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

      {/* Tab Navigation */}
      <div className="filter-section">
        <div className="filter-controls">
          <div className="filter-group">
            <label>Analysis Type</label>
            <select 
              value={activeTab} 
              onChange={(e) => setActiveTab(e.target.value)}
            >
              <option value="analysis">Program Analysis</option>
              <option value="performance">Performance Metrics</option>
            </select>
          </div>

          <button 
            className="fetch-btn"
            onClick={activeTab === 'analysis' ? fetchAnalysis : fetchPerformance}
            disabled={loading.analysis || loading.performance}
          >
            {loading.analysis || loading.performance 
              ? '🔄 Loading...' 
              : activeTab === 'analysis' 
                ? '🎯 Fetch Analysis' 
                : '📈 Fetch Performance'
            }
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Content based on active tab */}
      {activeTab === 'analysis' ? renderAnalysisTab() : renderPerformanceTab()}
    </div>
  )
}

export default EngagementModule