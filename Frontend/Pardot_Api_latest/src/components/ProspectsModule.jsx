import React, { useState } from 'react'
import { useGoogleAuth } from '../pages/Dashboard'
import './ProspectsModule.css'

const ProspectsModule = () => {
  const [healthData, setHealthData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('all')
  const [detailData, setDetailData] = useState({
    all: [],
    active: [],
    duplicates: [],
    inactive: [],
    missingFields: [],
    scoringIssues: []
  })
  const [filters, setFilters] = useState({
    view: 'all_prospects',
    date_range: 'all_time',
    date_field: 'last_activity',
    start_date: '',
    end_date: ''
  })
  const [filteredProspects, setFilteredProspects] = useState([])
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0
  })
  const [exporting, setExporting] = useState({ sheets: false, pdf: false })
  const { googleAuth, handleGoogleAuth, startRequest, endRequest } = useGoogleAuth()

  const analyzeProspectHealth = async () => {
    setLoading(true)
    setError('')
    startRequest() // Block navigation
    
    try {
      const response = await fetch('http://localhost:4001/get-prospect-health', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setHealthData(data)
        // Auto-load All Prospects tab immediately
        fetchDetailData('all')
      } else {
        setError('Failed to fetch prospect health data')
      }
    } catch (error) {
      setError('Error analyzing prospect health: ' + error.message)
    } finally {
      setLoading(false)
      endRequest() // Re-enable navigation
    }
  }

  const applyFilters = async (page = 1) => {
    try {
      const response = await fetch('http://localhost:4001/filter-prospects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          filters,
          page,
          per_page: pagination.per_page
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setFilteredProspects(data.prospects)
        setPagination(data.pagination)
        setActiveTab('filtered')
      } else {
        setError('Failed to apply filters')
      }
    } catch (error) {
      setError('Error applying filters: ' + error.message)
    }
  }

  const fetchDetailData = async (type, page = 1) => {
    try {
      let endpoint = ''
      switch (type) {
        case 'all':
          endpoint = '/get-all-prospects'
          break
        case 'active':
          endpoint = '/get-active-prospects'
          break
        case 'duplicates':
          endpoint = '/get-duplicate-prospects'
          break
        case 'inactive':
          endpoint = '/get-inactive-prospects'
          break
        case 'missing':
          endpoint = '/get-missing-fields-prospects'
          break
        case 'scoring':
          endpoint = '/get-scoring-issues-prospects'
          break
        default:
          return
      }

      const response = await fetch(`http://localhost:4001${endpoint}?page=${page}&per_page=${pagination.per_page}`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setDetailData(prev => ({ ...prev, [type]: data }))
        setActiveTab(type)
      } else {
        setError(`Failed to fetch ${type} data`)
      }
    } catch (error) {
      setError(`Error fetching ${type}: ` + error.message)
    }
  }

  const getHealthStatus = (value, type) => {
    if (type === 'duplicates' || type === 'inactive' || type === 'missing') {
      if (value === 0) return 'good'
      if (value < 10) return 'warning'
      return 'critical'
    }
    return 'good'
  }

  const renderPagination = (paginationData, onPageChange) => {
    if (!paginationData || paginationData.pages <= 1) return null

    const { page, pages, total, per_page } = paginationData
    const startItem = (page - 1) * per_page + 1
    const endItem = Math.min(page * per_page, total)

    return (
      <div className="pagination-container">
        <div className="pagination-info">
          Showing {startItem}-{endItem} of {total} results
        </div>
        <div className="pagination-controls">
          <button 
            onClick={() => onPageChange(1)}
            disabled={page === 1}
            className="pagination-btn"
          >
            First
          </button>
          <button 
            onClick={() => onPageChange(page - 1)}
            disabled={page === 1}
            className="pagination-btn"
          >
            Previous
          </button>
          
          {Array.from({ length: Math.min(5, pages) }, (_, i) => {
            let pageNum
            if (pages <= 5) {
              pageNum = i + 1
            } else if (page <= 3) {
              pageNum = i + 1
            } else if (page >= pages - 2) {
              pageNum = pages - 4 + i
            } else {
              pageNum = page - 2 + i
            }
            
            return (
              <button
                key={pageNum}
                onClick={() => onPageChange(pageNum)}
                className={`pagination-btn ${page === pageNum ? 'active' : ''}`}
              >
                {pageNum}
              </button>
            )
          })}
          
          <button 
            onClick={() => onPageChange(page + 1)}
            disabled={page === pages}
            className="pagination-btn"
          >
            Next
          </button>
          <button 
            onClick={() => onPageChange(pages)}
            disabled={page === pages}
            className="pagination-btn"
          >
            Last
          </button>
        </div>
      </div>
    )
  }



  const renderDuplicates = () => {
    const data = detailData.duplicates
    if (!data?.duplicate_prospects?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">✅</div>
            <h3>No Duplicate Prospects Found</h3>
            <p>Your prospect database is clean of duplicates</p>
          </div>
        </div>
      )
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>👥 Duplicate Prospects ({data.total_duplicate_groups} groups)</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Duplicate Count</th>
                <th>Names</th>
                <th>Companies</th>
                <th>Created Dates</th>
                <th>Last Activities</th>
              </tr>
            </thead>
            <tbody>
              {data.duplicate_prospects.map((group, index) => (
                <tr key={index}>
                  <td className="prospect-email">{group.email}</td>
                  <td><span className="status-badge critical">{group.prospects?.length || group.count}</span></td>
                  <td className="prospect-name">
                    {group.prospects?.map(p => `${p.firstName || ''} ${p.lastName || ''}`).join(', ') || 'N/A'}
                  </td>
                  <td>{group.prospects?.map(p => p.company || 'N/A').join(', ') || 'N/A'}</td>
                  <td>{group.prospects?.map(p => new Date(p.createdAt).toLocaleDateString()).join(', ') || 'N/A'}</td>
                  <td>{group.prospects?.map(p => p.lastActivityAt ? new Date(p.lastActivityAt).toLocaleDateString() : 'Never').join(', ') || 'Never'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('duplicates', page))}
      </div>
    )
  }

  const renderInactive = () => {
    const data = detailData.inactive
    if (!data?.inactive_prospects?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">✅</div>
            <h3>No Inactive Prospects</h3>
            <p>All prospects have recent activity</p>
          </div>
        </div>
      )
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>😴 Inactive Prospects ({data.total_inactive})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Name</th>
                <th>Company</th>
                <th>Last Activity</th>
                <th>Days Inactive</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {data.inactive_prospects.map((prospect, index) => (
                <tr key={index}>
                  <td className="prospect-email">{prospect.email}</td>
                  <td className="prospect-name">{prospect.firstName || ''} {prospect.lastName || ''}</td>
                  <td>{prospect.company || 'N/A'}</td>
                  <td>{prospect.lastActivityAt ? new Date(prospect.lastActivityAt).toLocaleDateString() : 'Never'}</td>
                  <td>{prospect.daysInactive || 'N/A'}</td>
                  <td>
                    <span className="status-badge inactive">Inactive</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('inactive', page))}
      </div>
    )
  }

  const renderMissingFields = () => {
    const data = detailData.missing
    console.log('[DEBUG] Missing fields data:', data)
    
    if (!data?.prospects_missing_fields?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">⚠️</div>
            <h3>No Missing Fields Data</h3>
            <p>Click the tab again to load missing fields data</p>
            <p>Expected: {healthData?.missing_fields_count || 0} prospects with missing fields</p>
          </div>
        </div>
      )
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>📝 Missing Critical Fields ({data.total_with_missing_fields})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Name</th>
                <th>Company</th>
                <th>Missing Fields</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {data.prospects_missing_fields.map((prospect, index) => (
                <tr key={index}>
                  <td className="prospect-email">{prospect.email}</td>
                  <td className="prospect-name">{prospect.firstName || ''} {prospect.lastName || ''}</td>
                  <td>{prospect.company || 'N/A'}</td>
                  <td>
                    <div className="missing-fields">
                      {prospect.missingFields?.map((field, fIndex) => (
                        <span key={fIndex} className="missing-field">{field}</span>
                      )) || 'N/A'}
                    </div>
                  </td>
                  <td>
                    <span className="status-badge missing">Incomplete</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('missing', page))}
      </div>
    )
  }

  const renderFiltered = () => {
    if (!filteredProspects.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3>No Filtered Results</h3>
            <p>Apply filters to see prospect results</p>
          </div>
        </div>
      )
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>🔍 Filtered Prospects ({pagination.total})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Name</th>
                <th>Company</th>
                <th>Score</th>
                <th>Grade</th>
                <th>Last Activity</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {filteredProspects.map((prospect, index) => (
                <tr key={index}>
                  <td className="prospect-email">{prospect.email}</td>
                  <td className="prospect-name">{prospect.firstName || ''} {prospect.lastName || ''}</td>
                  <td>{prospect.company || 'N/A'}</td>
                  <td>{prospect.score || 0}</td>
                  <td>{prospect.grade || 'N/A'}</td>
                  <td>{prospect.lastActivityAt ? new Date(prospect.lastActivityAt).toLocaleDateString() : 'Never'}</td>
                  <td>{new Date(prospect.createdAt).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {renderPagination(pagination, applyFilters)}
      </div>
    )
  }

  const exportToSheets = async (type) => {
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
      const response = await fetch('http://localhost:4001/export-prospects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ type })
      })
      
      const result = await response.json()
      if (result.success) {
        let exportData = []
        
        if (type === 'all' && result.data.summary) {
          // Export comprehensive data with multiple sheets
          const allData = result.data
          
          // Summary sheet
          exportData = [
            { 'Metric': 'Total Prospects', 'Count': allData.summary.total_prospects },
            { 'Metric': 'Active Prospects', 'Count': allData.summary.active_prospects },
            { 'Metric': 'Duplicate Groups', 'Count': allData.summary.duplicate_groups },
            { 'Metric': 'Inactive Prospects', 'Count': allData.summary.inactive_prospects },
            { 'Metric': 'Missing Fields Prospects', 'Count': allData.summary.missing_fields_prospects },
            {},
            { 'Metric': 'ALL PROSPECTS', 'Count': '' },
            ...allData.all_prospects.slice(0, 100).map(p => ({
              'Email': p.email,
              'First Name': p.firstName || '',
              'Last Name': p.lastName || '',
              'Company': p.company || '',
              'Score': p.score || 0,
              'Grade': p.grade || '',
              'Last Activity': p.lastActivityAt ? new Date(p.lastActivityAt).toLocaleDateString() : 'Never'
            }))
          ]
        } else if (type === 'duplicates') {
          exportData = result.data.map(group => ({
            'Email': group.email,
            'Duplicate Count': group.count || group.prospects?.length || 0,
            'Names': group.prospects?.map(p => `${p.firstName || ''} ${p.lastName || ''}`).join(', ') || '',
            'Created Dates': group.prospects?.map(p => new Date(p.createdAt).toLocaleDateString()).join(', ') || ''
          }))
        } else if (type === 'inactive') {
          exportData = result.data.map(prospect => ({
            'Email': prospect.email,
            'First Name': prospect.firstName || '',
            'Last Name': prospect.lastName || '',
            'Company': prospect.company || '',
            'Last Activity': prospect.lastActivityAt ? new Date(prospect.lastActivityAt).toLocaleDateString() : 'Never',
            'Days Inactive': prospect.daysInactive || 'N/A'
          }))
        } else if (type === 'missing_fields') {
          exportData = result.data.map(prospect => ({
            'Email': prospect.email,
            'First Name': prospect.firstName || '',
            'Last Name': prospect.lastName || '',
            'Company': prospect.company || '',
            'Missing Fields': prospect.missingFields?.join(', ') || ''
          }))
        } else if (type === 'scoring_issues') {
          exportData = result.data.map(prospect => ({
            'Email': prospect.email,
            'First Name': prospect.firstName || '',
            'Last Name': prospect.lastName || '',
            'Company': prospect.company || '',
            'Score': prospect.score,
            'Grade': prospect.grade,
            'Issues': prospect.issues?.join(', ') || '',
            'Last Activity': prospect.lastActivityAt ? new Date(prospect.lastActivityAt).toLocaleDateString() : 'Never'
          }))
        } else {
          exportData = result.data.map(prospect => ({
            'Email': prospect.email,
            'First Name': prospect.firstName || '',
            'Last Name': prospect.lastName || '',
            'Company': prospect.company || '',
            'Score': prospect.score || 0,
            'Grade': prospect.grade || '',
            'Last Activity': prospect.lastActivityAt ? new Date(prospect.lastActivityAt).toLocaleDateString() : 'Never'
          }))
        }

        const sheetsResponse = await fetch('http://localhost:4001/export-to-sheets', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            title: `Prospect ${type.charAt(0).toUpperCase() + type.slice(1)} Report - ${new Date().toLocaleDateString()}`,
            data: exportData
          })
        })

        const sheetsResult = await sheetsResponse.json()
        if (sheetsResult.success) {
          window.open(sheetsResult.url, '_blank')
        } else {
          setError('Export to sheets failed')
        }
      } else {
        setError('Export failed')
      }
    } catch (error) {
      setError('Export failed: ' + error.message)
    } finally {
      setExporting(prev => ({ ...prev, sheets: false }))
    }
  }

  const downloadPDF = async (type) => {
    setExporting(prev => ({ ...prev, pdf: true }))
    try {
      const response = await fetch('http://localhost:4001/export-prospects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ type })
      })
      
      const result = await response.json()
      if (result.success) {
        const pdfResponse = await fetch('http://localhost:4001/download-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            data_type: 'prospects',
            data: result.data,
            export_type: type,
            summary: result.data.summary || null,
            filters: filters
          })
        })

        if (pdfResponse.ok) {
          const blob = await pdfResponse.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `prospect-${type}-report-${new Date().toISOString().split('T')[0]}.pdf`
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
        } else {
          setError('PDF download failed')
        }
      } else {
        setError('Export failed')
      }
    } catch (error) {
      setError('PDF download failed: ' + error.message)
    } finally {
      setExporting(prev => ({ ...prev, pdf: false }))
    }
  }

  const renderScoringIssues = () => {
    const data = detailData.scoring
    if (!data?.prospects_scoring_issues?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">✅</div>
            <h3>No Scoring Issues</h3>
            <p>All prospects have consistent scoring</p>
          </div>
        </div>
      )
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>📊 Scoring Issues ({data.total_scoring_issues})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Name</th>
                <th>Company</th>
                <th>Score</th>
                <th>Grade</th>
                <th>Issues</th>
                <th>Last Activity</th>
              </tr>
            </thead>
            <tbody>
              {data.prospects_scoring_issues.map((prospect, index) => (
                <tr key={index}>
                  <td className="prospect-email">{prospect.email}</td>
                  <td className="prospect-name">{prospect.firstName || ''} {prospect.lastName || ''}</td>
                  <td>{prospect.company || 'N/A'}</td>
                  <td>{prospect.score}</td>
                  <td><span className="status-badge">{prospect.grade}</span></td>
                  <td>
                    <div className="scoring-issues">
                      {prospect.issues?.map((issue, iIndex) => (
                        <span key={iIndex} className="scoring-issue">{issue}</span>
                      )) || 'N/A'}
                    </div>
                  </td>
                  <td>{prospect.lastActivityAt ? new Date(prospect.lastActivityAt).toLocaleDateString() : 'Never'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('scoring', page))}
      </div>
    )
  }

  const renderAllProspects = () => {
    const data = detailData.all
    if (!data?.all_prospects?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">👥</div>
            <h3>No Prospects Data</h3>
            <p>Click the tab again to load all prospects</p>
          </div>
        </div>
      )
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>👥 All Prospects ({data.total_prospects})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Name</th>
                <th>Company</th>
                <th>Score</th>
                <th>Grade</th>
                <th>Last Activity</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {data.all_prospects.map((prospect, index) => (
                <tr key={index}>
                  <td className="prospect-email">{prospect.email}</td>
                  <td className="prospect-name">{prospect.firstName || ''} {prospect.lastName || ''}</td>
                  <td>{prospect.company || 'N/A'}</td>
                  <td>{prospect.score || 0}</td>
                  <td><span className="status-badge">{prospect.grade || 'D'}</span></td>
                  <td>{prospect.lastActivityAt ? new Date(prospect.lastActivityAt).toLocaleDateString() : 'Never'}</td>
                  <td>{prospect.createdAt ? new Date(prospect.createdAt).toLocaleDateString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('all', page))}
      </div>
    )
  }

  const renderActiveProspects = () => {
    const data = detailData.active
    if (!data?.active_prospects?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">✅</div>
            <h3>No Active Prospects</h3>
            <p>Click the tab again to load active prospects</p>
          </div>
        </div>
      )
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>✅ Active Prospects ({data.total_active})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Name</th>
                <th>Company</th>
                <th>Score</th>
                <th>Grade</th>
                <th>Last Activity</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {data.active_prospects.map((prospect, index) => (
                <tr key={index}>
                  <td className="prospect-email">{prospect.email}</td>
                  <td className="prospect-name">{prospect.firstName || ''} {prospect.lastName || ''}</td>
                  <td>{prospect.company || 'N/A'}</td>
                  <td>{prospect.score || 0}</td>
                  <td><span className="status-badge active">{prospect.grade || 'D'}</span></td>
                  <td>{prospect.lastActivityAt ? new Date(prospect.lastActivityAt).toLocaleDateString() : 'Never'}</td>
                  <td>{prospect.createdAt ? new Date(prospect.createdAt).toLocaleDateString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('active', page))}
      </div>
    )
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'all':
        return renderAllProspects()
      case 'active':
        return renderActiveProspects()
      case 'duplicates':
        return renderDuplicates()
      case 'inactive':
        return renderInactive()
      case 'missing':
        return renderMissingFields()
      case 'scoring':
        return renderScoringIssues()
      case 'filtered':
        return renderFiltered()
      default:
        return (
          <div className="empty-state">
            <div className="empty-icon">👥</div>
            <h3>Select a Tab</h3>
            <p>Choose a tab above to view detailed prospect analysis</p>
          </div>
        )
    }
  }

  return (
    <div className="prospects-module">
      <div className="module-header">
        <div className="header-content">
          <h2>👥 Prospect Database Health</h2>
          <p>Comprehensive analysis of prospect data quality and engagement</p>
        </div>
      </div>

      {/* Action Section */}
      <div className="filter-section">
        <div className="filter-controls">
          <button 
            className="fetch-btn"
            onClick={analyzeProspectHealth}
            disabled={loading}
          >
            {loading ? '🔄 Analyzing...' : '🔍 Analyze Prospect Health'}
          </button>
        </div>
      </div>

      {/* Filter Section */}
      {healthData && (
        <div className="filter-section">
          <div className="filter-controls">
            <div className="filter-group">
              <label>View</label>
              <select value={filters.view} onChange={(e) => setFilters(prev => ({ ...prev, view: e.target.value }))}>
                <option value="all_prospects">All Prospects</option>
                <option value="active_prospects">Active Prospects</option>
                <option value="never_active_prospects">Never Active</option>
                <option value="mailable_prospects">Mailable Prospects</option>
                <option value="assigned_prospects">Assigned Prospects</option>
                <option value="unassigned_prospects">Unassigned Prospects</option>
                <option value="prospects_not_in_salesforce">Not in Salesforce</option>
              </select>
            </div>
            <div className="filter-group">
              <label>Date Range</label>
              <select value={filters.date_range} onChange={(e) => setFilters(prev => ({ ...prev, date_range: e.target.value }))}>
                <option value="all_time">All Time</option>
                <option value="today">Today</option>
                <option value="yesterday">Yesterday</option>
                <option value="last_7_days">Last 7 Days</option>
                <option value="last_week">Last Week</option>
                <option value="this_month">This Month</option>
                <option value="last_month">Last Month</option>
                <option value="this_quarter">This Quarter</option>
                <option value="last_quarter">Last Quarter</option>
                <option value="this_year">This Year</option>
                <option value="last_year">Last Year</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>
            <div className="filter-group">
              <label>Date Field</label>
              <select value={filters.date_field} onChange={(e) => setFilters(prev => ({ ...prev, date_field: e.target.value }))}>
                <option value="last_activity">Last Activity</option>
                <option value="created">Created Date</option>
                <option value="updated">Updated Date</option>
              </select>
            </div>
            {filters.date_range === 'custom' && (
              <>
                <div className="filter-group">
                  <label>Start Date</label>
                  <input 
                    type="date" 
                    value={filters.start_date}
                    onChange={(e) => setFilters(prev => ({ ...prev, start_date: e.target.value }))}
                  />
                </div>
                <div className="filter-group">
                  <label>End Date</label>
                  <input 
                    type="date" 
                    value={filters.end_date}
                    onChange={(e) => setFilters(prev => ({ ...prev, end_date: e.target.value }))}
                  />
                </div>
              </>
            )}
            <div className="filter-group">
              <label>Results per page</label>
              <select value={pagination.per_page} onChange={(e) => setPagination(prev => ({ ...prev, per_page: parseInt(e.target.value), page: 1 }))}>
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>
            <button 
              className="fetch-btn"
              onClick={() => applyFilters(1)}
            >
              🔍 Apply Filters
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}



      {/* Summary Statistics Section */}
      {healthData && (
        <div className="summary-section">
          <div className="summary-header">
            <h3>📊 Prospects Overview</h3>
            <div className="export-controls">
              <button 
                className="export-btn sheets"
                onClick={() => exportToSheets('all')}
                disabled={exporting.sheets}
              >
                {exporting.sheets ? '🔄 Exporting...' : '📊 Export to Sheets'}
                {!googleAuth && <span className="auth-required">*Auth Required</span>}
              </button>
              <button 
                className="export-btn pdf"
                onClick={() => downloadPDF('all')}
                disabled={exporting.pdf}
              >
                {exporting.pdf ? '🔄 Generating...' : '📄 Download PDF'}
              </button>
            </div>
          </div>
          <div className="summary-grid">
            <div className="summary-card primary">
              <div className="summary-content">
                <div className="summary-value">{healthData.total_prospects?.toLocaleString() || 0}</div>
                <div className="summary-label">Total Prospects</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{healthData.active_prospects?.toLocaleString() || 0}</div>
                <div className="summary-label">Active Prospects</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{healthData.duplicate_count?.toLocaleString() || 0}</div>
                <div className="summary-label">Duplicate Prospects</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{healthData.inactive_count?.toLocaleString() || 0}</div>
                <div className="summary-label">Inactive Prospects</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{healthData.missing_fields_count?.toLocaleString() || 0}</div>
                <div className="summary-label">Missing Fields</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{healthData.scoring_issues_count || 0}</div>
                <div className="summary-label">Scoring Issues</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Analysis Tabs */}
      {healthData && (
        <div>
          <div className="health-tabs">
            <button 
              className={`health-tab ${activeTab === 'all' ? 'active' : ''}`}
              onClick={() => fetchDetailData('all')}
            >
              👥 All Prospects ({healthData.total_prospects || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'active' ? 'active' : ''}`}
              onClick={() => fetchDetailData('active')}
            >
              ✅ Active ({healthData.active_prospects || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'duplicates' ? 'active' : ''}`}
              onClick={() => fetchDetailData('duplicates')}
            >
              👥 Duplicates ({healthData.duplicate_count || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'inactive' ? 'active' : ''}`}
              onClick={() => fetchDetailData('inactive')}
            >
              😴 Inactive ({healthData.inactive_count || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'missing' ? 'active' : ''}`}
              onClick={() => fetchDetailData('missing')}
            >
              📝 Missing Fields ({healthData.missing_fields_count || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'scoring' ? 'active' : ''}`}
              onClick={() => fetchDetailData('scoring')}
            >
              📊 Scoring Issues ({healthData.scoring_issues_count || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'filtered' ? 'active' : ''}`}
              onClick={() => setActiveTab('filtered')}
            >
              🔍 Filtered Results ({filteredProspects.length})
            </button>
          </div>
          
          {renderTabContent()}
        </div>
      )}

      {/* Empty State */}
      {!healthData && !loading && (
        <div className="empty-state">
          <div className="empty-icon">👥</div>
          <h3>Prospect Health Analysis</h3>
          <p>Click "Analyze Prospect Health" to start evaluating your prospect database</p>
        </div>
      )}
    </div>
  )
}

export default ProspectsModule