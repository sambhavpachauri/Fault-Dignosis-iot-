import React from 'react';
import { Activity, RefreshCw, Pause, Play, Server, Cpu, Database, Layers, BookOpen } from 'lucide-react';

export default function Header({
  mqttConnected,
  backendConnected,
  lastReceived,
  activeMachine,
  setActiveMachine,
  isPaused,
  togglePause,
  refreshManual,
  activeTab,
  setActiveTab
}) {
  return (
    <header style={{
      borderBottom: '1px solid var(--border-normal)',
      backgroundColor: 'var(--bg-secondary)',
      padding: '1.1rem 2.25rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '0.95rem'
    }}>
      {/* Top Bar: Title & High-level status */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1.25rem'
      }}>
        {/* System ID & Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-normal)',
            padding: '0.45rem 0.85rem',
            borderRadius: '4px',
            fontSize: '1.05rem',
            fontWeight: '700',
            letterSpacing: '0.05em',
            color: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <Cpu size={18} color="var(--accent)" />
            P_311
          </div>
          <div>
            <h1 style={{
              fontSize: '1.35rem',
              fontWeight: '600',
              color: 'var(--text-primary)',
              letterSpacing: '-0.01em',
              margin: 0
            }}>
              Knowledge-Driven IoT Fault Diagnosis Assistant
            </h1>
            <p style={{
              fontSize: '0.88rem',
              color: 'var(--text-muted)',
              margin: '0.15rem 0 0 0'
            }}>
              Industrial Supervisory & Predictive Maintenance Console
            </p>
          </div>
        </div>

        {/* Status Indicators & Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Machine Selector */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontSize: '0.88rem',
            backgroundColor: 'var(--bg-panel)',
            border: '1px solid var(--border-normal)',
            padding: '0.45rem 0.85rem',
            borderRadius: '4px'
          }}>
            <span style={{ color: 'var(--text-muted)' }}>Target:</span>
            <select
              value={activeMachine}
              onChange={(e) => setActiveMachine(e.target.value)}
              style={{
                backgroundColor: 'transparent',
                color: 'var(--text-primary)',
                border: 'none',
                fontWeight: '600',
                fontSize: '0.88rem',
                cursor: 'pointer',
                outline: 'none'
              }}
            >
              <option value="Machine 1" style={{ background: '#222628' }}>Machine 1 (Active)</option>
              <option value="Machine 2" disabled style={{ background: '#222628' }}>Machine 2 (Offline)</option>
              <option value="Machine 3" disabled style={{ background: '#222628' }}>Machine 3 (Offline)</option>
            </select>
          </div>

          {/* MQTT Status */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.55rem',
            fontSize: '0.88rem',
            backgroundColor: 'var(--bg-panel)',
            padding: '0.45rem 0.85rem',
            borderRadius: '4px',
            border: '1px solid var(--border-normal)'
          }}>
            <span className="status-dot" style={{ backgroundColor: mqttConnected ? 'var(--status-normal)' : 'var(--status-critical)' }} />
            <span style={{ color: mqttConnected ? 'var(--text-secondary)' : 'var(--status-critical)', fontWeight: '500' }}>
              {mqttConnected ? 'MQTT Connected' : 'MQTT Offline'}
            </span>
          </div>

          {/* Backend Status */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.55rem',
            fontSize: '0.88rem',
            backgroundColor: 'var(--bg-panel)',
            padding: '0.45rem 0.85rem',
            borderRadius: '4px',
            border: '1px solid var(--border-normal)'
          }}>
            <span className="status-dot" style={{ backgroundColor: backendConnected ? 'var(--status-normal)' : 'var(--status-critical)' }} />
            <span style={{ color: backendConnected ? 'var(--text-secondary)' : 'var(--status-critical)', fontWeight: '500' }}>
              {backendConnected ? 'Backend Connected' : 'Backend Lost'}
            </span>
          </div>

          {/* Last Received Timestamp */}
          <div style={{
            fontSize: '0.88rem',
            backgroundColor: 'var(--bg-panel)',
            padding: '0.45rem 0.85rem',
            borderRadius: '4px',
            border: '1px solid var(--border-normal)'
          }}>
            <span style={{ color: 'var(--text-muted)', marginRight: '0.4rem' }}>Updated:</span>
            <span className="mono" style={{ color: lastReceived ? 'var(--text-primary)' : 'var(--text-muted)' }}>
              {lastReceived || 'Waiting for data...'}
            </span>
          </div>

          {/* Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <button
              onClick={togglePause}
              className="btn-tech"
              title={isPaused ? "Resume live stream" : "Pause live stream"}
              style={{
                padding: '0.45rem 0.85rem',
                fontSize: '0.85rem',
                borderColor: isPaused ? 'var(--status-medium)' : 'var(--border-normal)',
                color: isPaused ? 'var(--status-medium)' : 'var(--text-primary)'
              }}
            >
              {isPaused ? (
                <>
                  <Play size={14} color="var(--status-medium)" />
                  <span>Resume</span>
                </>
              ) : (
                <>
                  <Pause size={14} color="var(--text-secondary)" />
                  <span>Pause</span>
                </>
              )}
            </button>

            <button
              onClick={refreshManual}
              className="btn-tech"
              title="Manual fetch"
              style={{
                padding: '0.45rem 0.75rem',
                fontSize: '0.85rem'
              }}
            >
              <RefreshCw size={14} color="var(--text-secondary)" />
            </button>
          </div>
        </div>
      </div>

      {/* Prominent Industrial Workstation Navigation Bar */}
      <nav style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.65rem',
        borderTop: '1px solid var(--border-normal)',
        paddingTop: '0.85rem',
        flexWrap: 'wrap'
      }}>
        {[
          { id: 'dashboard', label: 'Live Monitor', icon: Activity },
          { id: 'digital-twin', label: '3D Digital Twin', icon: Layers },
          { id: 'diagnostics', label: 'Diagnostics & RAG Manual', icon: BookOpen },
          { id: 'history', label: 'History & Sensor Trends', icon: Database },
          { id: 'system', label: 'System Architecture', icon: Server }
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.6rem',
                padding: '0.65rem 1.25rem',
                borderRadius: '4px',
                fontSize: '0.95rem',
                fontWeight: isActive ? '600' : '500',
                cursor: 'pointer',
                border: isActive ? '1px solid var(--accent)' : '1px solid var(--border-normal)',
                backgroundColor: isActive ? 'var(--accent-subtle)' : 'var(--bg-panel)',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                transition: 'background-color 0.15s ease, border-color 0.15s ease'
              }}
            >
              <Icon size={18} color={isActive ? 'var(--accent)' : 'var(--text-muted)'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>
    </header>
  );
}
