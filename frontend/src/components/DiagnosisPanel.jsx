import React from 'react';
import { Stethoscope, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function DiagnosisPanel({ issues = [] }) {
  const isAllClear = !issues || issues.length === 0 || (issues.length === 1 && issues[0].includes("No major abnormal"));

  return (
    <div className="card-panel" style={{ height: '100%', display: 'flex', flexDirection: 'column', padding: '1.25rem 1.45rem' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '0.75rem',
        borderBottom: '1px solid var(--border-normal)',
        paddingBottom: '0.55rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Stethoscope size={16} color="var(--accent)" />
          <h3 style={{
            fontSize: '0.92rem',
            fontWeight: '600',
            color: 'var(--text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            margin: 0
          }}>
            Machine Diagnosis
          </h3>
        </div>
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Rule Engine Active
        </span>
      </div>

      <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.65rem' }}>
        Possible Contributing Conditions:
      </div>

      {isAllClear ? (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.65rem',
          padding: '0.85rem 1rem',
          borderRadius: '4px',
          backgroundColor: 'var(--status-normal-bg)',
          border: '1px solid var(--status-normal-border)',
          color: 'var(--status-normal)',
          fontSize: '0.88rem'
        }}>
          <CheckCircle2 size={18} color="var(--status-normal)" />
          <span>No major abnormal sensor condition detected</span>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.55rem', flex: 1 }}>
          {issues.map((issue, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.65rem',
                padding: '0.65rem 0.85rem',
                borderRadius: '4px',
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-normal)',
                fontSize: '0.88rem',
                color: 'var(--text-primary)'
              }}
            >
              <AlertTriangle size={16} color="var(--status-medium)" style={{ flexShrink: 0, marginTop: '0.15rem' }} />
              <span>{issue}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
