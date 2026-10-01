import React, { useState } from 'react';
import { Database, Search, RefreshCw, Calendar, HardDrive, ChevronDown, ChevronRight, AlertCircle, Wrench } from 'lucide-react';

export default function TelemetryHistoryTable({
  history = [],
  dbStats = null,
  loading = false,
  onQueryDatabase,
  activeMachine = 'Machine 1'
}) {
  const [selectedMachine, setSelectedMachine] = useState(activeMachine || 'Machine 1');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [queryLimit, setQueryLimit] = useState(100);
  const [expandedRowId, setExpandedRowId] = useState(null);

  const handleApplyDbQuery = () => {
    if (onQueryDatabase) {
      onQueryDatabase({
        machine_id: selectedMachine,
        limit: queryLimit,
        severity: severityFilter,
        start_time: startTime ? startTime.replace('T', ' ') : null,
        end_time: endTime ? endTime.replace('T', ' ') : null
      });
    }
  };

  const handleResetFilters = () => {
    setSelectedMachine('Machine 1');
    setSeverityFilter('ALL');
    setStartTime('');
    setEndTime('');
    setQueryLimit(100);
    setSearchTerm('');
    if (onQueryDatabase) {
      onQueryDatabase({
        machine_id: 'Machine 1',
        limit: 100,
        severity: 'ALL',
        start_time: null,
        end_time: null
      });
    }
  };

  const filteredHistory = history.filter(item => {
    const matchesSeverity = severityFilter === 'ALL' || item.diagnosis?.severity?.toUpperCase() === severityFilter;
    const matchesMachine = selectedMachine === 'ALL' || item.machine_id === selectedMachine;
    const matchesSearch = searchTerm === '' ||
      item.timestamp?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.machine_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.sensors?.type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.diagnosis?.status?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.diagnosis?.issues?.some(i => i.toLowerCase().includes(searchTerm.toLowerCase())) ||
      item.diagnosis?.recommendation?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSeverity && matchesMachine && matchesSearch;
  });

  return (
    <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', padding: '1.35rem 1.65rem' }}>
      {/* Header with Title & DB Engine Info */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.85rem',
        borderBottom: '1px solid var(--border-normal)',
        paddingBottom: '0.85rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Database size={18} color="var(--accent)" />
            <h3 style={{
              fontSize: '1.05rem',
              fontWeight: '600',
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              margin: 0
            }}>
              Persistent Telemetry History
            </h3>
          </div>

          {/* Database Engine Tag */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-normal)',
            borderRadius: '3px',
            padding: '0.2rem 0.6rem',
            fontSize: '0.75rem',
            color: 'var(--text-muted)'
          }}>
            <HardDrive size={12} color="var(--status-normal)" />
            <span>Engine: <strong style={{ color: 'var(--text-primary)' }}>{dbStats?.storage_engine || 'SQLite (WAL)'}</strong></span>
            {dbStats?.total_persisted_records !== undefined && (
              <>
                <span>•</span>
                <span>Total Stored: <strong className="mono" style={{ color: 'var(--accent)' }}>{dbStats.total_persisted_records}</strong></span>
              </>
            )}
          </div>

          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            ({filteredHistory.length} records displayed)
          </span>
        </div>

        {/* Database Query & Reset Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <button
            onClick={handleApplyDbQuery}
            disabled={loading}
            className="btn-tech btn-tech-active"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              fontSize: '0.82rem',
              padding: '0.4rem 0.85rem'
            }}
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>{loading ? 'Querying DB...' : 'Query Database'}</span>
          </button>
          <button
            onClick={handleResetFilters}
            className="btn-tech"
            style={{ fontSize: '0.82rem', padding: '0.4rem 0.75rem' }}
          >
            Reset
          </button>
        </div>
      </div>

      {/* Query Filters Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.85rem',
        flexWrap: 'wrap',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-normal)',
        borderRadius: '4px',
        padding: '0.65rem 0.95rem'
      }}>
        {/* Machine Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Machine:</span>
          <select
            value={selectedMachine}
            onChange={(e) => setSelectedMachine(e.target.value)}
            style={{
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border-normal)',
              borderRadius: '3px',
              color: 'var(--text-primary)',
              fontSize: '0.82rem',
              padding: '0.3rem 0.5rem',
              outline: 'none'
            }}
          >
            <option value="Machine 1">Machine 1 (Active)</option>
            <option value="ALL">All Machines</option>
          </select>
        </div>

        {/* Time Range: Start */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Calendar size={13} color="var(--text-muted)" />
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>From:</span>
          <input
            type="datetime-local"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            style={{
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border-normal)',
              borderRadius: '3px',
              color: 'var(--text-primary)',
              fontSize: '0.78rem',
              padding: '0.25rem 0.45rem',
              outline: 'none'
            }}
          />
        </div>

        {/* Time Range: End */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>To:</span>
          <input
            type="datetime-local"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            style={{
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border-normal)',
              borderRadius: '3px',
              color: 'var(--text-primary)',
              fontSize: '0.78rem',
              padding: '0.25rem 0.45rem',
              outline: 'none'
            }}
          />
        </div>

        {/* Query Limit */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Limit:</span>
          <select
            value={queryLimit}
            onChange={(e) => setQueryLimit(Number(e.target.value))}
            style={{
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border-normal)',
              borderRadius: '3px',
              color: 'var(--text-primary)',
              fontSize: '0.82rem',
              padding: '0.3rem 0.5rem',
              outline: 'none'
            }}
          >
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={250}>250</option>
            <option value={500}>500</option>
          </select>
        </div>

        {/* Text Search */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.45rem',
          backgroundColor: 'var(--bg-elevated)',
          border: '1px solid var(--border-normal)',
          borderRadius: '3px',
          padding: '0.25rem 0.55rem',
          marginLeft: 'auto'
        }}>
          <Search size={13} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search records..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-primary)',
              fontSize: '0.82rem',
              width: '140px'
            }}
          />
        </div>

        {/* Severity Filter Pills */}
        <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
          {['ALL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((sev) => {
            const isActive = severityFilter === sev;
            return (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`btn-tech ${isActive ? 'btn-tech-active' : ''}`}
                style={{
                  fontSize: '0.76rem',
                  padding: '0.25rem 0.6rem'
                }}
              >
                {sev}
              </button>
            );
          })}
        </div>
      </div>

      {/* Table Container */}
      <div style={{ overflowX: 'auto', maxHeight: '520px' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '0.86rem',
          textAlign: 'left'
        }}>
          <thead>
            <tr style={{
              borderBottom: '1px solid var(--border-normal)',
              color: 'var(--text-muted)',
              fontSize: '0.78rem',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              backgroundColor: 'var(--bg-secondary)',
              position: 'sticky',
              top: 0,
              zIndex: 1
            }}>
              <th style={{ padding: '0.65rem 0.5rem', width: '28px' }}></th>
              <th style={{ padding: '0.65rem 0.75rem' }}>Timestamp</th>
              <th style={{ padding: '0.65rem 0.65rem' }}>Machine</th>
              <th style={{ padding: '0.65rem 0.55rem' }}>Type</th>
              <th style={{ padding: '0.65rem 0.55rem' }}>Air (K)</th>
              <th style={{ padding: '0.65rem 0.55rem' }}>Proc (K)</th>
              <th style={{ padding: '0.65rem 0.55rem' }}>Speed</th>
              <th style={{ padding: '0.65rem 0.55rem' }}>Torque</th>
              <th style={{ padding: '0.65rem 0.55rem' }}>Wear</th>
              <th style={{ padding: '0.65rem 0.75rem' }}>Failure Prob</th>
              <th style={{ padding: '0.65rem 0.75rem' }}>Status</th>
              <th style={{ padding: '0.65rem 0.75rem' }}>Severity</th>
            </tr>
          </thead>
          <tbody>
            {filteredHistory.length === 0 ? (
              <tr>
                <td colSpan="12" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-muted)' }}>
                  {loading ? 'Fetching historical records from database...' : 'No historical telemetry records match the current database query.'}
                </td>
              </tr>
            ) : (
              filteredHistory.map((item, idx) => {
                const sev = item.diagnosis?.severity || 'LOW';
                let badgeClass = 'badge-normal';
                if (sev === 'MEDIUM') badgeClass = 'badge-medium';
                if (sev === 'HIGH') badgeClass = 'badge-high';
                if (sev === 'CRITICAL') badgeClass = 'badge-critical';

                const isExpanded = expandedRowId === (item.id || idx);

                return (
                  <React.Fragment key={item.id || idx}>
                    <tr
                      onClick={() => setExpandedRowId(isExpanded ? null : (item.id || idx))}
                      style={{
                        borderBottom: isExpanded ? 'none' : '1px solid var(--border-normal)',
                        backgroundColor: isExpanded ? 'var(--bg-elevated)' : (idx % 2 === 0 ? 'transparent' : 'var(--bg-secondary)'),
                        cursor: 'pointer',
                        transition: 'background-color 0.15s ease'
                      }}
                    >
                      <td style={{ padding: '0.55rem 0.5rem', color: 'var(--text-muted)' }}>
                        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                      </td>
                      <td className="mono" style={{ padding: '0.55rem 0.75rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                        {item.timestamp}
                      </td>
                      <td style={{ padding: '0.55rem 0.65rem', fontWeight: '500', color: 'var(--text-primary)' }}>
                        {item.machine_id || 'Machine 1'}
                      </td>
                      <td style={{ padding: '0.55rem 0.55rem', fontWeight: '600' }}>
                        {item.sensors?.type}
                      </td>
                      <td className="mono" style={{ padding: '0.55rem 0.55rem' }}>
                        {item.sensors?.air_temperature?.toFixed(1)}
                      </td>
                      <td className="mono" style={{ padding: '0.55rem 0.55rem' }}>
                        {item.sensors?.process_temperature?.toFixed(1)}
                      </td>
                      <td className="mono" style={{ padding: '0.55rem 0.55rem' }}>
                        {item.sensors?.rotational_speed}
                      </td>
                      <td className="mono" style={{ padding: '0.55rem 0.55rem' }}>
                        {item.sensors?.torque?.toFixed(1)}
                      </td>
                      <td className="mono" style={{ padding: '0.55rem 0.55rem' }}>
                        {item.sensors?.tool_wear}m
                      </td>
                      <td className="mono" style={{ padding: '0.55rem 0.75rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                        {item.diagnosis?.failure_probability_pct}
                      </td>
                      <td style={{ padding: '0.55rem 0.75rem' }}>
                        <span style={{
                          fontSize: '0.8rem',
                          fontWeight: '600',
                          color: item.diagnosis?.status === 'NORMAL' ? 'var(--status-normal)' : 'var(--status-critical)'
                        }}>
                          {item.diagnosis?.status}
                        </span>
                      </td>
                      <td style={{ padding: '0.55rem 0.75rem' }}>
                        <span className={`badge-status ${badgeClass}`} style={{ fontSize: '0.72rem', padding: '0.15rem 0.5rem' }}>
                          {sev}
                        </span>
                      </td>
                    </tr>

                    {/* Detailed Accordion Inspection Row */}
                    {isExpanded && (
                      <tr style={{ backgroundColor: 'var(--bg-elevated)', borderBottom: '1px solid var(--border-normal)' }}>
                        <td colSpan="12" style={{ padding: '0.75rem 1.25rem 1rem 2rem' }}>
                          <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                            gap: '1rem',
                            borderLeft: '2px solid var(--accent)',
                            paddingLeft: '1rem'
                          }}>
                            {/* Issues */}
                            <div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.35rem' }}>
                                <AlertCircle size={14} color="var(--status-medium)" />
                                <span style={{ fontSize: '0.78rem', fontWeight: '600', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
                                  Diagnosed Issues ({item.diagnosis?.issues?.length || 0})
                                </span>
                              </div>
                              {item.diagnosis?.issues?.length > 0 ? (
                                <ul style={{ margin: 0, paddingLeft: '1.1rem', fontSize: '0.82rem', color: 'var(--text-primary)' }}>
                                  {item.diagnosis.issues.map((iss, i) => (
                                    <li key={i} style={{ marginBottom: '0.2rem' }}>{iss}</li>
                                  ))}
                                </ul>
                              ) : (
                                <span style={{ fontSize: '0.82rem', color: 'var(--status-normal)' }}>
                                  All sensor parameters within nominal operating bounds.
                                </span>
                              )}
                            </div>

                            {/* Recommendation */}
                            <div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.35rem' }}>
                                <Wrench size={14} color="var(--accent)" />
                                <span style={{ fontSize: '0.78rem', fontWeight: '600', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
                                  RAG Engineering Recommendation
                                </span>
                              </div>
                              <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                                {item.diagnosis?.recommendation || 'Continuous monitoring active.'}
                              </p>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
