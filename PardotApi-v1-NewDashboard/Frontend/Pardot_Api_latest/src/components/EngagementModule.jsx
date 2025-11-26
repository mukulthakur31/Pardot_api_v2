import React, { useState } from 'react';
import './ProspectsModule.css';

const EngagementModule = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('all');
  const [detailData, setDetailData] = useState({
    all: [],
    active: [],
    inactive: [],
    lowPerformance: [],
    noEntries: []
  });
  const [filters, setFilters] = useState({
    view: 'all_programs',
    date_range: 'all_time',
    date_field: 'created',
    start_date: '',
    end_date: ''
  });
  const [filteredPrograms, setFilteredPrograms] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0
  });

  const analyzeEngagementHealth = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:4001/engagement-health-analysis', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setHealthData(data.summary);
        // Auto-load All Programs tab immediately
        fetchDetailData('all');
      } else {
        setError('Failed to fetch engagement health data');
      }
    } catch (error) {
      setError('Error analyzing engagement health: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchDetailData = async (type, page = 1) => {
    try {
      let endpoint = '';
      switch (type) {
        case 'all':
          endpoint = '/get-all-programs';
          break;
        case 'active':
          endpoint = '/get-active-programs';
          break;
        case 'inactive':
          endpoint = '/get-inactive-programs';
          break;
        case 'lowPerformance':
          endpoint = '/get-low-performance-programs';
          break;
        case 'noEntries':
          endpoint = '/get-no-entries-programs';
          break;
        default:
          return;
      }

      const response = await fetch(`http://localhost:4001${endpoint}?page=${page}&per_page=${pagination.per_page}`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setDetailData(prev => ({ ...prev, [type]: data }));
        setActiveTab(type);
      } else {
        setError(`Failed to fetch ${type} data`);
      }
    } catch (error) {
      setError(`Error fetching ${type}: ` + error.message);
    }
  };

  const applyFilters = async (page = 1) => {
    try {
      const response = await fetch('http://localhost:4001/filter-programs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          filters,
          page,
          per_page: pagination.per_page
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setFilteredPrograms(data.programs);
        setPagination(data.pagination);
        setActiveTab('filtered');
      } else {
        setError('Failed to apply filters');
      }
    } catch (error) {
      setError('Error applying filters: ' + error.message);
    }
  };

  const renderPagination = (paginationData, onPageChange) => {
    if (!paginationData || paginationData.pages <= 1) return null;

    const { page, pages, total, per_page } = paginationData;
    const startItem = (page - 1) * per_page + 1;
    const endItem = Math.min(page * per_page, total);

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
            let pageNum;
            if (pages <= 5) {
              pageNum = i + 1;
            } else if (page <= 3) {
              pageNum = i + 1;
            } else if (page >= pages - 2) {
              pageNum = pages - 4 + i;
            } else {
              pageNum = page - 2 + i;
            }
            
            return (
              <button
                key={pageNum}
                onClick={() => onPageChange(pageNum)}
                className={`pagination-btn ${page === pageNum ? 'active' : ''}`}
              >
                {pageNum}
              </button>
            );
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
    );
  };

  const renderAllPrograms = () => {
    const data = detailData.all;
    if (!data?.all_programs?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <h3>No Programs Data</h3>
            <p>Click the tab again to load all programs</p>
          </div>
        </div>
      );
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>📊 All Programs ({data.total_programs})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Created</th>
                <th>Updated</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {data.all_programs.map((program, index) => (
                <tr key={program.id || index}>
                  <td className="program-name">{program.name}</td>
                  <td>
                    <span className={`status-badge ${program.status?.toLowerCase()}`}>
                      {program.status}
                    </span>
                  </td>
                  <td>{program.createdAt ? new Date(program.createdAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.updatedAt ? new Date(program.updatedAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.description || 'No description'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('all', page))}
      </div>
    );
  };

  const renderActivePrograms = () => {
    const data = detailData.active;
    if (!data?.active_programs?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">✅</div>
            <h3>No Active Programs</h3>
            <p>Click the tab again to load active programs</p>
          </div>
        </div>
      );
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>✅ Active Programs ({data.total_active})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Created</th>
                <th>Updated</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {data.active_programs.map((program, index) => (
                <tr key={program.id || index}>
                  <td className="program-name">{program.name}</td>
                  <td><span className="status-badge active">{program.status}</span></td>
                  <td>{program.createdAt ? new Date(program.createdAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.updatedAt ? new Date(program.updatedAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.description || 'No description'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('active', page))}
      </div>
    );
  };

  const renderInactivePrograms = () => {
    const data = detailData.inactive;
    if (!data?.inactive_programs?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">😴</div>
            <h3>No Inactive Programs</h3>
            <p>All programs are currently active</p>
          </div>
        </div>
      );
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>😴 Inactive Programs ({data.total_inactive})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Created</th>
                <th>Updated</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {data.inactive_programs.map((program, index) => (
                <tr key={program.id || index}>
                  <td className="program-name">{program.name}</td>
                  <td><span className="status-badge inactive">{program.status}</span></td>
                  <td>{program.createdAt ? new Date(program.createdAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.updatedAt ? new Date(program.updatedAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.description || 'No description'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('inactive', page))}
      </div>
    );
  };

  const renderLowPerformance = () => {
    const data = detailData.lowPerformance;
    if (!data?.low_performance_programs?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">📉</div>
            <h3>No Low Performance Programs</h3>
            <p>All programs are performing well</p>
          </div>
        </div>
      );
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>📉 Low Performance Programs ({data.total_low_performance})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Created</th>
                <th>Updated</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {data.low_performance_programs.map((program, index) => (
                <tr key={program.id || index}>
                  <td className="program-name">{program.name}</td>
                  <td><span className="status-badge critical">{program.status}</span></td>
                  <td>{program.createdAt ? new Date(program.createdAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.updatedAt ? new Date(program.updatedAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.description || 'No description'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('lowPerformance', page))}
      </div>
    );
  };

  const renderNoEntries = () => {
    const data = detailData.noEntries;
    if (!data?.no_entries_programs?.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">🚫</div>
            <h3>No Programs Without Entries</h3>
            <p>All programs have prospect entries</p>
          </div>
        </div>
      );
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>🚫 Programs Without Entries ({data.total_no_entries})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Created</th>
                <th>Updated</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {data.no_entries_programs.map((program, index) => (
                <tr key={program.id || index}>
                  <td className="program-name">{program.name}</td>
                  <td><span className="status-badge warning">{program.status}</span></td>
                  <td>{program.createdAt ? new Date(program.createdAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.updatedAt ? new Date(program.updatedAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.description || 'No description'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {data.pagination && renderPagination(data.pagination, (page) => fetchDetailData('noEntries', page))}
      </div>
    );
  };

  const renderFiltered = () => {
    if (!filteredPrograms.length) {
      return (
        <div className="results-section">
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3>No Filtered Results</h3>
            <p>Apply filters to see program results</p>
          </div>
        </div>
      );
    }

    return (
      <div className="results-section">
        <div className="results-header">
          <h3>🔍 Filtered Programs ({pagination.total})</h3>
        </div>
        
        <div className="table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Created</th>
                <th>Updated</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {filteredPrograms.map((program, index) => (
                <tr key={program.id || index}>
                  <td className="program-name">{program.name}</td>
                  <td><span className="status-badge">{program.status}</span></td>
                  <td>{program.createdAt ? new Date(program.createdAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.updatedAt ? new Date(program.updatedAt).toLocaleDateString() : 'N/A'}</td>
                  <td>{program.description || 'No description'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {renderPagination(pagination, applyFilters)}
      </div>
    );
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'all':
        return renderAllPrograms();
      case 'active':
        return renderActivePrograms();
      case 'inactive':
        return renderInactivePrograms();
      case 'lowPerformance':
        return renderLowPerformance();
      case 'noEntries':
        return renderNoEntries();
      case 'filtered':
        return renderFiltered();
      default:
        return (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <h3>Select a Tab</h3>
            <p>Choose a tab above to view detailed engagement analysis</p>
          </div>
        );
    }
  };

  return (
    <div className="prospects-module">
      <div className="module-header">
        <div className="header-content">
          <h2>📊 Engagement Programs Health</h2>
          <p>Comprehensive analysis of engagement program performance and status</p>
        </div>
      </div>

      {/* Action Section */}
      <div className="filter-section">
        <div className="filter-controls">
          <button 
            className="fetch-btn"
            onClick={analyzeEngagementHealth}
            disabled={loading}
          >
            {loading ? '🔄 Analyzing...' : '🔍 Analyze Engagement Health'}
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
                <option value="all_programs">All Programs</option>
                <option value="active_programs">Active Programs</option>
                <option value="inactive_programs">Inactive Programs</option>
                <option value="paused_programs">Paused Programs</option>
                <option value="deleted_programs">Deleted Programs</option>
              </select>
            </div>
            <div className="filter-group">
              <label>Date Range</label>
              <select value={filters.date_range} onChange={(e) => setFilters(prev => ({ ...prev, date_range: e.target.value }))}>
                <option value="all_time">All Time</option>
                <option value="today">Today</option>
                <option value="yesterday">Yesterday</option>
                <option value="last_7_days">Last 7 Days</option>
                <option value="last_30_days">Last 30 Days</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>
            <div className="filter-group">
              <label>Date Field</label>
              <select value={filters.date_field} onChange={(e) => setFilters(prev => ({ ...prev, date_field: e.target.value }))}>
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
            <h3>📊 Programs Overview</h3>
          </div>
          <div className="summary-grid">
            <div className="summary-card primary">
              <div className="summary-content">
                <div className="summary-value">{healthData.total_programs?.toLocaleString() || 0}</div>
                <div className="summary-label">Total Programs</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{healthData.active_count?.toLocaleString() || 0}</div>
                <div className="summary-label">Active Programs</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{healthData.inactive_count?.toLocaleString() || 0}</div>
                <div className="summary-label">Inactive Programs</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{healthData.low_performance_count?.toLocaleString() || 0}</div>
                <div className="summary-label">Low Performance</div>
              </div>
            </div>
            
            <div className="summary-card">
              <div className="summary-content">
                <div className="summary-value">{healthData.no_entries_count || 0}</div>
                <div className="summary-label">No Entries</div>
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
              📊 All Programs ({healthData.total_programs || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'active' ? 'active' : ''}`}
              onClick={() => fetchDetailData('active')}
            >
              ✅ Active ({healthData.active_count || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'inactive' ? 'active' : ''}`}
              onClick={() => fetchDetailData('inactive')}
            >
              😴 Inactive ({healthData.inactive_count || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'lowPerformance' ? 'active' : ''}`}
              onClick={() => fetchDetailData('lowPerformance')}
            >
              📉 Low Performance ({healthData.low_performance_count || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'noEntries' ? 'active' : ''}`}
              onClick={() => fetchDetailData('noEntries')}
            >
              🚫 No Entries ({healthData.no_entries_count || 0})
            </button>
            <button 
              className={`health-tab ${activeTab === 'filtered' ? 'active' : ''}`}
              onClick={() => setActiveTab('filtered')}
            >
              🔍 Filtered Results ({filteredPrograms.length})
            </button>
          </div>
          
          {renderTabContent()}
        </div>
      )}

      {/* Empty State */}
      {!healthData && !loading && (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>Engagement Health Analysis</h3>
          <p>Click "Analyze Engagement Health" to start evaluating your engagement programs</p>
        </div>
      )}
    </div>
  );
};

export default EngagementModule;