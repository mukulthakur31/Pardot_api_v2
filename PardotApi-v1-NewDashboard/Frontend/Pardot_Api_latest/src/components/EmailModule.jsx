import React, { useState } from 'react'
import { useGoogleAuth } from '../pages/Dashboard'
import './EmailModule.css'

const EmailModule = () => {
  const [emailStats, setEmailStats] = useState([])
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState({ sheets: false, pdf: false })
  const [filters, setFilters] = useState({
    filterType: 'all',
    startDate: '',
    endDate: ''
  })
  const [error, setError] = useState('')
  const { googleAuth, handleGoogleAuth } = useGoogleAuth()

  const fetchEmailStats = async () => {
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
      
      const response = await fetch(`http://localhost:4001/get-email-stats?${params}`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setEmailStats(data)
      } else {
        setError('Failed to fetch email statistics')
      }
    } catch (error) {
      setError('Error fetching email stats: ' + error.message)
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
      const exportData = emailStats.map(email => ({
        'Campaign Name': email.name,
        'Subject': email.subject,
        'Created Date': new Date(email.createdat).toLocaleDateString(),
        'Sent': email.stats.sent,
        'Delivered': email.stats.delivered,
        'Opens': email.stats.opens,
        'Unique Opens': email.stats.uniqueOpens,
        'Clicks': email.stats.clicks,
        'Unique Clicks': email.stats.uniqueClicks,
        'Bounces': email.stats.bounces,
        'Hard Bounces': email.stats.hardBounces,
        'Soft Bounces': email.stats.softBounces,
        'Open Rate': email.stats.delivered > 0 ? ((email.stats.uniqueOpens / email.stats.delivered) * 100).toFixed(2) + '%' : '0%',
        'Click Rate': email.stats.delivered > 0 ? ((email.stats.uniqueClicks / email.stats.delivered) * 100).toFixed(2) + '%' : '0%',
        'Bounce Rate': email.stats.sent > 0 ? ((email.stats.bounces / email.stats.sent) * 100).toFixed(2) + '%' : '0%'
      }))

      const response = await fetch('http://localhost:4001/export-to-sheets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: `Email Campaign Report - ${new Date().toLocaleDateString()}`,
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
          data_type: 'emails',
          data: emailStats,
          filters: filters
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `email-campaign-report-${new Date().toISOString().split('T')[0]}.pdf`
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

  const calculateMetrics = (stats) => {
    const openRate = stats.delivered > 0 ? (stats.uniqueOpens / stats.delivered) * 100 : 0
    const clickRate = stats.delivered > 0 ? (stats.uniqueClicks / stats.delivered) * 100 : 0
    const bounceRate = stats.sent > 0 ? (stats.bounces / stats.sent) * 100 : 0
    const deliveryRate = stats.sent > 0 ? (stats.delivered / stats.sent) * 100 : 0
    
    return { openRate, clickRate, bounceRate, deliveryRate }
  }

  const getPerformanceColor = (rate, type) => {
    if (type === 'open') {
      if (rate >= 25) return '#10b981'
      if (rate >= 15) return '#f59e0b'
      return '#ef4444'
    }
    if (type === 'click') {
      if (rate >= 3) return '#10b981'
      if (rate >= 1) return '#f59e0b'
      return '#ef4444'
    }
    if (type === 'bounce') {
      if (rate <= 2) return '#10b981'
      if (rate <= 5) return '#f59e0b'
      return '#ef4444'
    }
    return '#6b7280'
  }

  const calculateTotalStats = () => {
    if (!emailStats.length) return null
    
    const totals = emailStats.reduce((acc, email) => {
      acc.campaigns += 1
      acc.sent += email.stats.sent
      acc.delivered += email.stats.delivered
      acc.opens += email.stats.opens
      acc.uniqueOpens += email.stats.uniqueOpens
      acc.clicks += email.stats.clicks
      acc.uniqueClicks += email.stats.uniqueClicks
      acc.bounces += email.stats.bounces
      acc.hardBounces += email.stats.hardBounces
      acc.softBounces += email.stats.softBounces
      return acc
    }, {
      campaigns: 0,
      sent: 0,
      delivered: 0,
      opens: 0,
      uniqueOpens: 0,
      clicks: 0,
      uniqueClicks: 0,
      bounces: 0,
      hardBounces: 0,
      softBounces: 0
    })

    const avgOpenRate = totals.delivered > 0 ? (totals.uniqueOpens / totals.delivered) * 100 : 0
    const avgClickRate = totals.delivered > 0 ? (totals.uniqueClicks / totals.delivered) * 100 : 0
    const avgBounceRate = totals.sent > 0 ? (totals.bounces / totals.sent) * 100 : 0
    const deliveryRate = totals.sent > 0 ? (totals.delivered / totals.sent) * 100 : 0

    return { ...totals, avgOpenRate, avgClickRate, avgBounceRate, deliveryRate }
  }

  return (
    <div className="email-module">
      <div className="module-header">
        <div className="header-content">
          <h2>📧 Email Analytics</h2>
          <p>Comprehensive email performance metrics and insights</p>
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
              <option value="last_6_months">Last 6 Months</option>
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
            onClick={fetchEmailStats}
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

      {/* Summary Statistics Section */}
      {emailStats.length > 0 && (() => {
        const totalStats = calculateTotalStats()
        return (
          <div className="summary-section">
            <div className="summary-header">
              <h3>📈 Emails Overview</h3>
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
                  <div className="summary-value">{totalStats.campaigns}</div>
                  <div className="summary-label">Total Campaigns</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.sent.toLocaleString()}</div>
                  <div className="summary-label">Total Sent</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.delivered.toLocaleString()}</div>
                  <div className="summary-label">Total Delivered</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.uniqueOpens.toLocaleString()}</div>
                  <div className="summary-label">Unique Opens</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.uniqueClicks.toLocaleString()}</div>
                  <div className="summary-label">Unique Clicks</div>
                </div>
              </div>
              
              <div className="summary-card">
                <div className="summary-content">
                  <div className="summary-value">{totalStats.bounces.toLocaleString()}</div>
                  <div className="summary-label">Total Bounces</div>
                </div>
              </div>
            </div>
            
            <div className="performance-summary">
              <div className="performance-item">
                <span className="performance-label">Average Open Rate</span>
                <span 
                  className="performance-value"
                  style={{ color: getPerformanceColor(totalStats.avgOpenRate, 'open') }}
                >
                  {totalStats.avgOpenRate.toFixed(1)}%
                </span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Average Click Rate</span>
                <span 
                  className="performance-value"
                  style={{ color: getPerformanceColor(totalStats.avgClickRate, 'click') }}
                >
                  {totalStats.avgClickRate.toFixed(1)}%
                </span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Average Bounce Rate</span>
                <span 
                  className="performance-value"
                  style={{ color: getPerformanceColor(totalStats.avgBounceRate, 'bounce') }}
                >
                  {totalStats.avgBounceRate.toFixed(1)}%
                </span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Delivery Rate</span>
                <span 
                  className="performance-value"
                  style={{ color: getPerformanceColor(totalStats.deliveryRate, 'open') }}
                >
                  {totalStats.deliveryRate.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        )
      })()}



      {/* Results Section */}
      {emailStats.length > 0 ? (
        <div className="results-section">
          <div className="results-header">
            <h3>📈 Email Performance ({emailStats.length} campaigns)</h3>
          </div>
          
          <div className="table-container">
            <table className="campaigns-table">
              <thead>
                <tr>
                  <th>Campaign Name</th>
                  <th>Subject</th>
                  <th>Created</th>
                  <th>Sent</th>
                  <th>Delivered</th>
                  <th>Opens</th>
                  <th>Unique Opens</th>
                  <th>Clicks</th>
                  <th>Unique Clicks</th>
                  <th>Bounces</th>
                  <th>Open Rate</th>
                  <th>Click Rate</th>
                  <th>Bounce Rate</th>
                </tr>
              </thead>
              <tbody>
                {emailStats.map((email) => {
                  const metrics = calculateMetrics(email.stats)
                  return (
                    <tr key={email.id}>
                      <td className="campaign-name">{email.name}</td>
                      <td className="campaign-subject">{email.subject || 'No subject'}</td>
                      <td>{new Date(email.createdat).toLocaleDateString()}</td>
                      <td>{email.stats.sent.toLocaleString()}</td>
                      <td>{email.stats.delivered.toLocaleString()}</td>
                      <td>{email.stats.opens.toLocaleString()}</td>
                      <td>{email.stats.uniqueOpens.toLocaleString()}</td>
                      <td>{email.stats.clicks.toLocaleString()}</td>
                      <td>{email.stats.uniqueClicks.toLocaleString()}</td>
                      <td>{email.stats.bounces.toLocaleString()}</td>
                      <td>
                        <span 
                          className="rate-badge"
                          style={{ color: getPerformanceColor(metrics.openRate, 'open') }}
                        >
                          {metrics.openRate.toFixed(1)}%
                        </span>
                      </td>
                      <td>
                        <span 
                          className="rate-badge"
                          style={{ color: getPerformanceColor(metrics.clickRate, 'click') }}
                        >
                          {metrics.clickRate.toFixed(1)}%
                        </span>
                      </td>
                      <td>
                        <span 
                          className="rate-badge"
                          style={{ color: getPerformanceColor(metrics.bounceRate, 'bounce') }}
                        >
                          {metrics.bounceRate.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : !loading && (
        <div className="empty-state">
          <div className="empty-icon">📧</div>
          <h3>No Email Data</h3>
          <p>Use the filters above to fetch email campaign statistics</p>
        </div>
      )}
    </div>
  )
}

export default EmailModule