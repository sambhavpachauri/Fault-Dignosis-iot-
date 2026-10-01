import React from 'react';
import { AlertOctagon, CheckCircle2, ShieldAlert, Wrench } from 'lucide-react';

export default function RecommendedAction({ recommendation, severity = 'LOW' }) {
  let title = "Standard Operating Procedure";
  let border = "var(--border-normal)";
  let accentColor = "var(--status-normal)";
  let icon = <CheckCircle2 size={24} color="var(--status-normal)" />;

  if (severity === 'CRITICAL') {
    title = "Immediate Inspection Required";
    border = "var(--status-critical-border)";
    accentColor = "var(--status-critical)";
    icon = <AlertOctagon size={24} color="var(--status-critical)" />;
  } else if (severity === 'HIGH') {
    title = "High Priority Maintenance Scheduled";
    border = "var(--status-high-border)";
    accentColor = "var(--status-high)";
    icon = <ShieldAlert size={24} color="var(--status-high)" />;
  } else if (severity === 'MEDIUM') {
    title = "Preventive Maintenance Recommended";
    border = "var(--status-medium-border)";
    accentColor = "var(--status-medium)";
    icon = <Wrench size={24} color="var(--status-medium)" />;
  }

  return (
    <div className="card-panel" style={{
      borderColor: border,
      borderLeft: `5px solid ${accentColor}`,
      display: 'flex',
      alignItems: 'flex-start',
      gap: '1.25rem',
      padding: '1.35rem 1.65rem'
    }}>
      <div style={{
        padding: '0.65rem',
        borderRadius: '4px',
        backgroundColor: 'var(--bg-elevated)',
        border: '1px solid var(--border-normal)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0
      }}>
        {icon}
      </div>

      <div style={{ flex: 1 }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.65rem',
          marginBottom: '0.35rem'
        }}>
          <span style={{
            fontSize: '0.85rem',
            textTransform: 'uppercase',
            fontWeight: '600',
            letterSpacing: '0.04em',
            color: 'var(--text-secondary)'
          }}>
            Recommended Action
          </span>
          <span style={{
            fontSize: '0.8rem',
            color: accentColor,
            fontWeight: '600',
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-normal)',
            padding: '0.15rem 0.5rem',
            borderRadius: '3px'
          }}>
            {title}
          </span>
        </div>

        <p style={{
          fontSize: '1.15rem',
          fontWeight: '600',
          color: 'var(--text-primary)',
          margin: '0.35rem 0',
          lineHeight: 1.45
        }}>
          {recommendation || "Machine operating within nominal envelope. Maintain scheduled telemetry logging."}
        </p>

        <p style={{
          fontSize: '0.85rem',
          color: 'var(--text-muted)',
          margin: '0.2rem 0 0 0'
        }}>
          Correlated with FAISS RAG engineering manual and domain diagnosis rules.
        </p>
      </div>
    </div>
  );
}
