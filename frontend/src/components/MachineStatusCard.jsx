import React from 'react';
import { CheckCircle2, AlertTriangle, AlertOctagon, Clock } from 'lucide-react';

export default function MachineStatusCard({ latest, waiting }) {
  if (waiting || !latest) {
    return (
      <div className="card-panel" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '110px'
      }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <Clock size={20} style={{ marginBottom: '0.35rem', opacity: 0.6 }} />
          <p style={{ fontSize: '0.85rem' }}>Waiting for machine telemetry data...</p>
        </div>
      </div>
    );
  }

  const { sensors, diagnosis, timestamp, machine_id } = latest;
  const severity = diagnosis?.severity || 'LOW';
  const status = diagnosis?.status || 'NORMAL';
  const probability = diagnosis?.failure_probability_pct || '0.00%';

  let severityBadgeClass = 'badge-normal';
  let indicatorColor = 'var(--status-normal)';
  let icon = <CheckCircle2 size={18} color="var(--status-normal)" />;

  if (severity === 'MEDIUM') {
    severityBadgeClass = 'badge-medium';
    indicatorColor = 'var(--status-medium)';
    icon = <AlertTriangle size={18} color="var(--status-medium)" />;
  } else if (severity === 'HIGH') {
    severityBadgeClass = 'badge-high';
    indicatorColor = 'var(--status-high)';
    icon = <AlertTriangle size={18} color="var(--status-high)" />;
  } else if (severity === 'CRITICAL') {
    severityBadgeClass = 'badge-critical';
    indicatorColor = 'var(--status-critical)';
    icon = <AlertOctagon size={18} color="var(--status-critical)" />;
  }

  const typeMap = {
    'L': 'Low Quality Variant (L)',
    'M': 'Medium Quality Variant (M)',
    'H': 'High Quality Variant (H)'
  };
  const typeDescription = typeMap[sensors?.type] || `Type ${sensors?.type}`;

  return (
    <div className="card-panel" style={{
      position: 'relative',
      borderLeft: `5px solid ${indicatorColor}`,
      padding: '1.25rem 1.65rem'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1.5rem'
      }}>
        {/* Machine & Status Group */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{
            padding: '0.75rem',
            borderRadius: '4px',
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-normal)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {React.cloneElement(icon, { size: 24 })}
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.3rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>
                {machine_id} Operational State
              </span>
              <span style={{
                fontSize: '0.82rem',
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-normal)',
                padding: '0.15rem 0.55rem',
                borderRadius: '3px',
                color: 'var(--text-secondary)'
              }}>
                {typeDescription}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
              <h2 style={{
                fontSize: '1.75rem',
                fontWeight: '700',
                letterSpacing: '-0.01em',
                margin: 0,
                color: status === 'NORMAL' ? 'var(--status-normal)' : indicatorColor
              }}>
                {status}
              </h2>
              <span className={`badge-status ${severityBadgeClass}`} style={{ fontSize: '0.85rem', padding: '0.3rem 0.75rem' }}>
                {severity} SEVERITY
              </span>
            </div>
          </div>
        </div>

        {/* Readouts */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '2.5rem',
          flexWrap: 'wrap'
        }}>
          <div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.2rem' }}>
              Failure Risk Probability
            </div>
            <div className="mono" style={{
              fontSize: '1.75rem',
              fontWeight: '700',
              color: status === 'NORMAL' ? 'var(--status-normal)' : indicatorColor
            }}>
              {probability}
            </div>
          </div>

          <div style={{ borderLeft: '1px solid var(--border-normal)', paddingLeft: '1.75rem' }}>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.2rem' }}>
              Last Evaluated
            </div>
            <div className="mono" style={{ fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
              {timestamp}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
