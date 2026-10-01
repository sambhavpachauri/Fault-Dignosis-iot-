import React, { useState } from 'react';
import { PlayCircle, Flame, Gauge, Wrench, AlertOctagon, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';

export default function SimulationControlBar() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [lastScenario, setLastScenario] = useState(null);

  const API_BASE = window.location.origin.includes('5173')
    ? 'http://127.0.0.1:8000'
    : window.location.origin;

  const triggerScenario = async (scenarioKey) => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/simulate?scenario=${scenarioKey}`, {
        method: 'POST'
      });
      if (res.ok) {
        setLastScenario(scenarioKey);
      }
    } catch (e) {
      console.error("Failed to trigger simulation scenario", e);
    } finally {
      setLoading(false);
    }
  };

  const scenarios = [
    { key: 'NORMAL', label: 'Nominal Baseline', icon: CheckCircle2, color: 'var(--status-normal)' },
    { key: 'HIGH_TEMP', label: 'Thermal Anomaly', icon: Flame, color: 'var(--status-high)' },
    { key: 'HIGH_TORQUE', label: 'High Torque Load', icon: Gauge, color: 'var(--status-medium)' },
    { key: 'HIGH_WEAR', label: 'Tool Wear Anomaly', icon: Wrench, color: 'var(--status-high)' },
    { key: 'CRITICAL', label: 'Critical Failure Risk', icon: AlertOctagon, color: 'var(--status-critical)' }
  ];

  return (
    <div style={{
      backgroundColor: 'var(--bg-panel)',
      border: '1px solid var(--border-normal)',
      borderRadius: '4px',
      overflow: 'hidden'
    }}>
      {/* Collapsible Header */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.75rem 1.45rem',
          cursor: 'pointer',
          backgroundColor: isExpanded ? 'var(--bg-elevated)' : 'transparent',
          transition: 'background-color 0.15s ease'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <PlayCircle size={17} color="var(--accent)" />
          <span style={{ fontSize: '0.88rem', fontWeight: '600', color: 'var(--text-secondary)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            Telemetry Scenario Injection Console
          </span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            (Publish test payload to MQTT topic)
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.85rem', color: 'var(--accent)', fontWeight: '500' }}>
          <span>{isExpanded ? 'Minimize' : 'Open Injector'}</span>
          {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </div>
      </div>

      {/* Expanded Controls Drawer */}
      {isExpanded && (
        <div style={{
          padding: '0.95rem 1.45rem',
          borderTop: '1px solid var(--border-normal)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.85rem',
          backgroundColor: 'var(--bg-secondary)'
        }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Select test condition:
          </span>

          <div style={{ display: 'flex', gap: '0.65rem', flexWrap: 'wrap' }}>
            {scenarios.map(s => {
              const Icon = s.icon;
              const isLast = lastScenario === s.key;
              return (
                <button
                  key={s.key}
                  onClick={() => triggerScenario(s.key)}
                  disabled={loading}
                  className="btn-tech"
                  style={{
                    fontSize: '0.85rem',
                    padding: '0.45rem 0.85rem',
                    borderColor: isLast ? s.color : 'var(--border-normal)',
                    backgroundColor: isLast ? 'var(--bg-elevated)' : 'var(--bg-panel)'
                  }}
                >
                  <Icon size={14} color={s.color} />
                  <span>{s.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
