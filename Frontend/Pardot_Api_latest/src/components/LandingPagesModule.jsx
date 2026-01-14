import React, { useState } from 'react'
import { useGoogleAuth } from '../pages/Dashboard'
import './EmailModule.css'

const LandingPagesModule = () => {
  const [landingPageStats, setLandingPageStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState({ sheets: false, pdf: false })
  const [filters, setFilters] = useState({
    filterType: 'all',
    startDate: '',
    endDate: ''
  })
  const [error, setError] = useState('')
  const { googleAuth, handleGoogleAuth } = useGoogleAuth()

  const fetchLandingPageStats = async () => {
    setLoading(true)
    setError('')
    
    try {
      const params = new URLSearchParams()
      if (filters.filterType !== 'all') {
        params.append('filter_type', filters.filterType)
        if (filters.filterType === 'custom' && filters.startDate && filters.endDate) {
          params.append('start_date', filters.startDate)
          params.append('end_date', filters.endDate)
        }
      }
      
      const response = await fetch(`http://localhost:4001/get-landing-page-stats?${params}`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setLandingPageStats(data)
      } else {
        setError('Failed to fetch landing page statistics')
      }
    } catch (error) {
      setError('Error fetching landing page stats: ' + error.message)
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
      const exportData = landingPageStats 
        ? [...landingPageStats.active_pages.pages, ...landingPageStats.inactive_pages.pages].map(page => ({
            'Page Name': page.name,
            'URL': page.url,
            'Status': page.is_active ? 'Active' : 'Inactive',
            'Views': page.views,
            'Submissions': page.submissions,
            'Clicks': page.clicks,
            'Total Activities': page.total_activities,
            'Recent Activities': page.recent_activities,
            'Last Activity': page.last_activity ? new Date(page.last_activity).toLocaleDateString() : 'None',
            'Created Date': page.created_at ? new Date(page.created_at).toLocaleDateString() : 'Unknown'
          })) : []

      const response = await fetch('http://localhost:4001/export-to-sheets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: `Landing Pages Report - ${new Date().toLocaleDateString()}`,
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
          data_type: 'landing_pages',
          data: landingPageStats,
          filters: filters
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `landing-pages-report-${new Date().toISOString().split('T')[0]}.pdf`
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
          <h2>🚀 Landing Pages Analytics</h2>
          <p>Comprehensive landing page performance metrics and field mapping audit</p>
        </div>
      </div>

      {/* Filter Section */}
      <div className="filter-section">
        <div className="filter-controls">
          <div className="filter-group">
            <label>Time Period</label>
            <select 
              value={filters.filterType} 
              onChange={(e) => setFilters(prev => ({ ...prev, filterType: e.target.value }))}
            >
              <option value="all">All Time</option>
              <option value="last_7_days">Last 7 Days</option>
              <option value="last_30_days">Last 30 Days</option>
              <option value="last_3_months">Last 3 Months</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>

          {filters.filterType === 'custom' && (
            <>
              <div className="filter-group">
                <label>Start Date</label>
                <input 
                  type="date" 
                  value={filters.startDate}
                  onChange={(e) => setFilters(prev => ({ ...prev, startDate: e.target.value }))}
                />
              </div>
              <div className="filter-group">
                <label>End Date</label>
                <input 
                  type="date" 
                  value={filters.endDate}
                  onChange={(e) => setFilters(prev => ({ ...prev, endDate: e.target.value }))}
                />
              </div>
            </>
          )}

          <button 
            className="fetch-btn"
            onClick={fetchLandingPageStats}
            disabled={loading}
          >
            {loading ? '🔄 Loading...' : '🔍 Fetch Data'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Results Section */}
      {landingPageStats && (
        <>
          {/* Summary Section */}
          <div className="summary-section">
            <div className="summary-header">
              <h3>📈 Landing Pages Overview</h3>
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
            
            <div style={{
              background: '#f0f9ff',
              border: '1px solid #0ea5e9',
              borderRadius: '8px',
              padding: '1rem',
              marginBottom: '1.5rem',
              fontSize: '0.875rem',
              color: '#0c4a6e'
            }}>
              <strong>📊 Activity Classification:</strong> Pages are considered <strong>Active</strong> if they have visitor activity (views, clicks, or form submissions) in the last 3 months. Pages with no activity in this period are marked as <strong>Inactive</strong>.
            </div>
            
            <div className="summary-grid">
              <div className="summary-card primary">
                <div className="summary-content">
                  <div className="summary-value">{landingPageStats.summary.total_pages}</div>
                  <div className="summary-label">Total Pages</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{landingPageStats.active_pages.count}</div>
                  <div className="summary-label">Active Pages</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{landingPageStats.inactive_pages.count}</div>
                  <div className="summary-label">Inactive Pages</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{landingPageStats.summary.total_activities.toLocaleString()}</div>
                  <div className="summary-label">Total Activities</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">
                    {(() => {
                      const totalViews = [...landingPageStats.active_pages.pages, ...landingPageStats.inactive_pages.pages]
                        .reduce((sum, page) => sum + page.views, 0)
                      const totalSubmissions = [...landingPageStats.active_pages.pages, ...landingPageStats.inactive_pages.pages]
                        .reduce((sum, page) => sum + page.submissions, 0)
                      const conversionRate = totalViews > 0 ? ((totalSubmissions / totalViews) * 100).toFixed(1) : '0.0'
                      return `${conversionRate}%`
                    })()
                    }
                  </div>
                  <div className="summary-label">Conversion Rate</div>
                </div>
              </div>
              

            </div>
          </div>

          {/* Active Pages Table */}
          {landingPageStats.active_pages.pages.length > 0 && (
            <div className="results-section">
              <div className="results-header">
                <h3>✅ Active Landing Pages ({landingPageStats.active_pages.count})</h3>
              </div>
              
              <div className="table-container">
                <table className="campaigns-table">
                  <thead>
                    <tr>
                      <th>Page Name</th>
                      <th>URL</th>
                      <th>Views</th>
                      <th>Submissions</th>
                      <th>Clicks</th>
                      <th>Total Activities</th>

                      <th>Last Activity</th>
                    </tr>
                  </thead>
                  <tbody>
                    {landingPageStats.active_pages.pages.map((page) => (
                      <tr key={page.id}>
                        <td className="campaign-name">{page.name}</td>
                        <td className="campaign-subject">
                          <a href={page.url} target="_blank" rel="noopener noreferrer" style={{ color: '#3b82f6' }}>
                            {page.url}
                          </a>
                        </td>
                        <td>{page.views.toLocaleString()}</td>
                        <td>{page.submissions.toLocaleString()}</td>
                        <td>{page.clicks.toLocaleString()}</td>
                        <td>{page.total_activities.toLocaleString()}</td>

                        <td>{page.last_activity ? new Date(page.last_activity).toLocaleDateString() : 'None'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Inactive Pages Table */}
          {landingPageStats.inactive_pages.pages.length > 0 && (
            <div className="results-section">
              <div className="results-header">
                <h3>⚠️ Inactive Landing Pages ({landingPageStats.inactive_pages.count})</h3>
              </div>
              
              <div className="table-container">
                <table className="campaigns-table">
                  <thead>
                    <tr>
                      <th>Page Name</th>
                      <th>URL</th>
                      <th>Views</th>
                      <th>Submissions</th>
                      <th>Clicks</th>
                      <th>Total Activities</th>
                      <th>Recent Activities</th>
                      <th>Last Activity</th>
                      <th>Created Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {landingPageStats.inactive_pages.pages.map((page) => (
                      <tr key={page.id}>
                        <td className="campaign-name">{page.name}</td>
                        <td className="campaign-subject">
                          <a href={page.url} target="_blank" rel="noopener noreferrer" style={{ color: '#3b82f6' }}>
                            {page.url}
                          </a>
                        </td>
                        <td>{page.views.toLocaleString()}</td>
                        <td>{page.submissions.toLocaleString()}</td>
                        <td>{page.clicks.toLocaleString()}</td>
                        <td>{page.total_activities.toLocaleString()}</td>
                        <td>{page.recent_activities.toLocaleString()}</td>
                        <td>{page.last_activity ? new Date(page.last_activity).toLocaleDateString() : 'None'}</td>
                        <td>{page.created_at ? new Date(page.created_at).toLocaleDateString() : 'Unknown'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}



      {/* Empty State */}
      {!landingPageStats && !loading && (
        <div className="empty-state">
          <div className="empty-icon">🚀</div>
          <h3>No Landing Page Data</h3>
          <p>Use the filters above to fetch landing page statistics</p>
        </div>
      )}
    </div>
  )
}

export default LandingPagesModule