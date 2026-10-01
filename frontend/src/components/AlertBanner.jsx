import React from 'react';
import { AlertOctagon, AlertTriangle, Check } from 'lucide-react';

export default function AlertBanner({ alert, onAcknowledge }) {
  if (!alert) return null;

  const isCritical = alert.severity === 'CRITICAL';
  const borderColor = isCritical ? 'var(--status-critical-border)' : 'var(--status-high-border)';
  const statusColor = isCritical ? 'var(--status-critical)' : 'var(--status-high)';

  return (
    <div style={{
      backgroundColor: 'var(--bg-panel)',
      border: `1px solid ${borderColor}`,
      borderLeft: `5px solid ${statusColor}`,
      borderRadius: '4px',
      padding: '1.15rem 1.65rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '1.25rem',
      flexWrap: 'wrap'
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <div style={{
          padding: '0.55rem',
          backgroundColor: 'var(--bg-elevated)',
          border: '1px solid var(--border-normal)',
          borderRadius: '4px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}>
          {isCritical ? (
            <AlertOctagon size={24} color="var(--status-critical)" />
          ) : (
            <AlertTriangle size={24} color="var(--status-high)" />
          )}
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <span style={{
              fontSize: '0.95rem',
              fontWeight: '700',
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
              color: statusColor
            }}>
              {isCritical ? 'CRITICAL MACHINE CONDITION' : 'HIGH SEVERITY ALARM'}
            </span>
            <span className="mono" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Time: {alert.time}
            </span>
            <span className="mono" style={{
              fontSize: '0.85rem',
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border-normal)',
              padding: '0.15rem 0.5rem',
              borderRadius: '3px',
              color: statusColor,
              fontWeight: '600'
            }}>
              Risk: {alert.probability}
            </span>
          </div>

          <p style={{
            fontSize: '0.95rem',
            color: 'var(--text-primary)',
            margin: '0.35rem 0 0.2rem 0',
            fontWeight: '500',
            lineHeight: 1.45
          }}>
            {alert.message}
          </p>

          {alert.recommendation && (
            <p style={{
              fontSize: '0.88rem',
              color: 'var(--text-secondary)',
              margin: '0.2rem 0 0 0'
            }}>
              {alert.recommendation}
            </p>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.35rem' }}>
        <button
          onClick={onAcknowledge}
          className="btn-tech"
          style={{
            fontSize: '0.88rem',
            padding: '0.45rem 1rem',
            borderColor: borderColor,
            color: 'var(--text-primary)'
          }}
        >
          <Check size={16} color="var(--status-normal)" />
          <span>Acknowledge</span>
        </button>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          (UI state dismissal only)
        </span>
      </div>
    </div>
  );
}
