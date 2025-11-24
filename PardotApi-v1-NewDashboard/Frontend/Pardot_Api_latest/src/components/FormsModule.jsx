import React, { useState } from 'react'
import { useGoogleAuth } from '../pages/Dashboard'
import './FormsModule.css'

const FormsModule = () => {
  const [formStats, setFormStats] = useState([])
  const [activeInactiveData, setActiveInactiveData] = useState(null)
  const [abandonmentData, setAbandonmentData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState({ sheets: false, pdf: false })
  const [activeTab, setActiveTab] = useState('all') // all, active, inactive, abandonment
  const [filters, setFilters] = useState({
    filterType: 'all',
    startDate: '',
    endDate: ''
  })
  const [error, setError] = useState('')
  const { googleAuth, handleGoogleAuth } = useGoogleAuth()

  const fetchFormStats = async () => {
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
      
      const response = await fetch(`http://localhost:4001/get-form-stats?${params}`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setFormStats(data)
        
        // Fetch additional data
        await Promise.all([
          fetchActiveInactiveForms(),
          fetchAbandonmentAnalysis()
        ])
      } else {
        setError('Failed to fetch form statistics')
      }
    } catch (error) {
      setError('Error fetching form stats: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchActiveInactiveForms = async () => {
    try {
      const response = await fetch('http://localhost:4001/get-active-inactive-forms', {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setActiveInactiveData(data)
      }
    } catch (error) {
      console.error('Error fetching active/inactive forms:', error)
    }
  }

  const fetchAbandonmentAnalysis = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.filterType !== 'all') {
        params.append('filter_type', filters.filterType)
        if (filters.filterType === 'custom' && filters.startDate && filters.endDate) {
          params.append('start_date', filters.startDate)
          params.append('end_date', filters.endDate)
        }
      }
      
      const response = await fetch(`http://localhost:4001/get-form-abandonment-analysis?${params}`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setAbandonmentData(data)
      }
    } catch (error) {
      console.error('Error fetching abandonment analysis:', error)
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
      const currentData = getCurrentTabData()
      const exportData = currentData.map(form => ({
        'Form Name': form.name,
        'Status': form.is_active ? 'Active' : 'Inactive',
        'Views': form.views,
        'Unique Views': form.unique_views,
        'Submissions': form.submissions,
        'Unique Submissions': form.unique_submissions,
        'Conversions': form.conversions,
        'Abandoned': form.abandoned,
        'Abandonment Rate': form.abandonment_rate + '%',
        'Clicks': form.clicks,
        'Last Activity': form.last_activity ? new Date(form.last_activity).toLocaleDateString() : 'Never'
      }))

      const response = await fetch('http://localhost:4001/export-to-sheets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: `Form Analytics Report - ${new Date().toLocaleDateString()}`,
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
          data_type: 'forms',
          data: getCurrentTabData(),
          filters: filters
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `form-analytics-report-${new Date().toISOString().split('T')[0]}.pdf`
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

  const getCurrentTabData = () => {
    if (activeTab === 'active' && activeInactiveData) {
      return activeInactiveData.active_forms.forms
    } else if (activeTab === 'inactive' && activeInactiveData) {
      return activeInactiveData.inactive_forms.forms
    }
    return formStats
  }

  const getPerformanceColor = (rate, type) => {
    if (type === 'abandonment') {
      if (rate <= 30) return '#10b981'
      if (rate <= 60) return '#f59e0b'
      return '#ef4444'
    }
    return '#6b7280'
  }

  const calculateTotalStats = () => {
    if (!formStats.length) return null
    
    const totals = formStats.reduce((acc, form) => {
      acc.forms += 1
      acc.views += form.views
      acc.uniqueViews += form.unique_views
      acc.submissions += form.submissions
      acc.uniqueSubmissions += form.unique_submissions
      acc.abandoned += form.abandoned
      acc.clicks += form.clicks
      acc.conversions += form.conversions
      return acc
    }, {
      forms: 0,
      views: 0,
      uniqueViews: 0,
      submissions: 0,
      uniqueSubmissions: 0,
      abandoned: 0,
      clicks: 0,
      conversions: 0
    })

    const avgAbandonmentRate = totals.views > 0 ? (totals.abandoned / totals.views) * 100 : 0

    return { ...totals, avgAbandonmentRate }
  }

  return (
    <div className="forms-module">
      <div className="module-header">
        <div className="header-content">
          <h2>📝 Forms Analytics</h2>
          <p>Comprehensive form performance, conversion, and abandonment analysis</p>
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
              <option value="today">Today</option>
              <option value="yesterday">Yesterday</option>
              <option value="last_7_days">Last 7 Days</option>
              <option value="last_30_days">Last 30 Days</option>
              <option value="this_month">This Month</option>
              <option value="last_month">Last Month</option>
              <option value="this_quarter">This Quarter</option>
              <option value="this_year">This Year</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>

          {filters.filterType === 'custom' && (
            <>
              <div className="filter-group">
                <label>Start Date</label>
                <input 
                  type="datetime-local" 
                  value={filters.startDate}
                  onChange={(e) => setFilters(prev => ({ ...prev, startDate: e.target.value }))}
                />
              </div>
              <div className="filter-group">
                <label>End Date</label>
                <input 
                  type="datetime-local" 
                  value={filters.endDate}
                  onChange={(e) => setFilters(prev => ({ ...prev, endDate: e.target.value }))}
                />
              </div>
            </>
          )}

          <button 
            className="fetch-btn"
            onClick={fetchFormStats}
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

      {/* Tabs */}
      {formStats.length > 0 && (
        <div className="tabs-container">
          <button 
            className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            📊 All Forms ({formStats.length})
          </button>
          <button 
            className={`tab-btn ${activeTab === 'active' ? 'active' : ''}`}
            onClick={() => setActiveTab('active')}
          >
            ✅ Active ({activeInactiveData?.active_forms.count || 0})
          </button>
          <button 
            className={`tab-btn ${activeTab === 'inactive' ? 'active' : ''}`}
            onClick={() => setActiveTab('inactive')}
          >
            ⏸️ Inactive ({activeInactiveData?.inactive_forms.count || 0})
          </button>
          <button 
            className={`tab-btn ${activeTab === 'abandonment' ? 'active' : ''}`}
            onClick={() => setActiveTab('abandonment')}
          >
            ⚠️ Abandonment Analysis
          </button>
        </div>
      )}

      {/* Summary Statistics Section */}
      {formStats.length > 0 && activeTab !== 'abandonment' && (() => {
        const totalStats = calculateTotalStats()
        return (
          <div className="summary-section">
            <div className="summary-header">
              <h3>📈 Forms Overview</h3>
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
                  <div className="summary-value">{totalStats.forms}</div>
                  <div className="summary-label">Total Forms</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.views.toLocaleString()}</div>
                  <div className="summary-label">Total Views</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.uniqueViews.toLocaleString()}</div>
                  <div className="summary-label">Unique Views</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.submissions.toLocaleString()}</div>
                  <div className="summary-label">Total Submissions</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.uniqueSubmissions.toLocaleString()}</div>
                  <div className="summary-label">Unique Submissions</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.abandoned.toLocaleString()}</div>
                  <div className="summary-label">Abandoned</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.conversions.toLocaleString()}</div>
                  <div className="summary-label">Conversions (New Prospects)</div>
                </div>
              </div>
            </div>
            
            <div className="performance-summary">
              <div className="performance-item">
                <span className="performance-label">Average Abandonment Rate</span>
                <span 
                  className="performance-value"
                  style={{ color: getPerformanceColor(totalStats.avgAbandonmentRate, 'abandonment') }}
                >
                  {totalStats.avgAbandonmentRate.toFixed(1)}%
                </span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Active Forms</span>
                <span className="performance-value" style={{ color: '#10b981' }}>
                  {activeInactiveData?.active_forms.count || 0}
                </span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Inactive Forms</span>
                <span className="performance-value" style={{ color: '#ef4444' }}>
                  {activeInactiveData?.inactive_forms.count || 0}
                </span>
              </div>
            </div>
          </div>
        )
      })()}

      {/* Abandonment Analysis Tab */}
      {activeTab === 'abandonment' && abandonmentData && (
        <div className="abandonment-section">
          <div className="abandonment-header">
            <h3>⚠️ Form Abandonment Analysis</h3>
          </div>
          
          <div className="summary-grid">
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{abandonmentData.summary.total_views.toLocaleString()}</div>
                <div className="summary-label">Total Views</div>
              </div>
            </div>
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{abandonmentData.summary.total_submissions.toLocaleString()}</div>
                <div className="summary-label">Total Submissions</div>
              </div>
            </div>
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{abandonmentData.summary.total_abandoned.toLocaleString()}</div>
                <div className="summary-label">Total Abandoned</div>
              </div>
            </div>
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{abandonmentData.summary.overall_abandonment_rate}%</div>
                <div className="summary-label">Overall Abandonment Rate</div>
              </div>
            </div>
          </div>

          <div className="abandonment-categories">
            <div className="category-card high">
              <div className="category-value">{abandonmentData.categories.high_abandonment.count}</div>
              <div className="category-label">High Abandonment</div>
              <div className="category-threshold">{abandonmentData.categories.high_abandonment.threshold}</div>
            </div>
            <div className="category-card medium">
              <div className="category-value">{abandonmentData.categories.medium_abandonment.count}</div>
              <div className="category-label">Medium Abandonment</div>
              <div className="category-threshold">{abandonmentData.categories.medium_abandonment.threshold}</div>
            </div>
            <div className="category-card low">
              <div className="category-value">{abandonmentData.categories.low_abandonment.count}</div>
              <div className="category-label">Low Abandonment</div>
              <div className="category-threshold">{abandonmentData.categories.low_abandonment.threshold}</div>
            </div>
          </div>

          {abandonmentData.insights.best_performing_form && (
            <div className="performance-summary" style={{ marginTop: '1rem' }}>
              <div className="performance-item">
                <span className="performance-label">Best Performing Form</span>
                <span className="performance-value" style={{ color: '#10b981' }}>
                  {abandonmentData.insights.best_performing_form.name}
                </span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Worst Performing Form</span>
                <span className="performance-value" style={{ color: '#ef4444' }}>
                  {abandonmentData.insights.worst_performing_form?.name || 'N/A'}
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Results Table */}
      {formStats.length > 0 && activeTab !== 'abandonment' ? (
        <div className="results-section">
          <div className="results-header">
            <h3>📋 Form Performance ({getCurrentTabData().length} forms)</h3>
          </div>
          
          <div className="table-container">
            <table className="forms-table">
              <thead>
                <tr>
                  <th>Form Name</th>
                  <th>Status</th>
                  <th>Views</th>
                  <th>Unique Views</th>
                  <th>Submissions</th>
                  <th>Unique Submissions</th>
                  <th>Conversions</th>
                  <th>Abandoned</th>
                  <th>Abandonment Rate</th>
                  <th>Clicks</th>
                  <th>Last Activity</th>
                </tr>
              </thead>
              <tbody>
                {getCurrentTabData().map((form) => (
                  <tr key={form.id}>
                    <td className="form-name">{form.name}</td>
                    <td>
                      <span className={`status-badge ${form.is_active ? 'active' : 'inactive'}`}>
                        {form.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>{form.views.toLocaleString()}</td>
                    <td>{form.unique_views.toLocaleString()}</td>
                    <td>{form.submissions.toLocaleString()}</td>
                    <td>{form.unique_submissions.toLocaleString()}</td>
                    <td>{form.conversions.toLocaleString()}</td>
                    <td>{form.abandoned.toLocaleString()}</td>
                    <td>
                      <span 
                        className="rate-badge"
                        style={{ color: getPerformanceColor(form.abandonment_rate, 'abandonment') }}
                      >
                        {form.abandonment_rate}%
                      </span>
                    </td>
                    <td>{form.clicks.toLocaleString()}</td>
                    <td>{form.last_activity ? new Date(form.last_activity).toLocaleDateString() : 'Never'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : !loading && formStats.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <h3>No Form Data</h3>
          <p>Use the filters above to fetch form analytics and performance metrics</p>
        </div>
      )}
    </div>
  )
}

export default FormsModule
