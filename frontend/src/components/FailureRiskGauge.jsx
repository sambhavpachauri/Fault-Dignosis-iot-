import React from 'react';
import { Target, Activity } from 'lucide-react';

export default function FailureRiskGauge({ probability = 0, threshold = 0.40, status = "NORMAL" }) {
  const probPercent = Math.min(100, Math.max(0, probability * 100));
  const thresholdPercent = threshold * 100;

  const radius = 86;
  const strokeWidth = 10;
  const totalLength = Math.PI * radius; // 180 deg semi-circle
  const activeLength = (probPercent / 100) * totalLength;

  let statusColor = 'var(--status-normal)';
  if (probPercent >= 75) {
    statusColor = 'var(--status-critical)';
  } else if (probPercent >= thresholdPercent) {
    statusColor = 'var(--status-high)';
  } else if (probPercent >= 20) {
    statusColor = 'var(--status-medium)';
  }

  // Needle angle for semi-circle: 180 (left) to 0 (right)
  const angleDeg = 180 - (probPercent / 100) * 180;

  return (
    <div className="card-panel" style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '1.45rem',
      height: '100%',
      minHeight: '265px'
    }}>
      {/* Header */}
      <div style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={16} color="var(--text-muted)" />
          <span style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: '600' }}>
            Predictive Failure Risk
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', color: 'var(--status-medium)' }}>
          <Target size={14} color="var(--status-medium)" />
          <span>Cutoff: {thresholdPercent.toFixed(0)}%</span>
        </div>
      </div>

      {/* Scaled Engineering Arc Gauge (Flat, Matte, Zero Glow) */}
      <div style={{ position: 'relative', width: '220px', height: '125px', marginTop: '0.85rem' }}>
        <svg width="220" height="125" viewBox="0 0 220 125">
          {/* Neutral Track */}
          <path
            d="M 24 110 A 86 86 0 0 1 196 110"
            fill="none"
            stroke="var(--bg-elevated)"
            strokeWidth={strokeWidth}
            strokeLinecap="square"
          />

          {/* Active Status Arc */}
          <path
            d="M 24 110 A 86 86 0 0 1 196 110"
            fill="none"
            stroke={statusColor}
            strokeWidth={strokeWidth}
            strokeDasharray={totalLength}
            strokeDashoffset={totalLength - activeLength}
            strokeLinecap="square"
            style={{ transition: 'stroke-dashoffset 0.25s ease' }}
          />

          {/* Threshold Marker Line */}
          {(() => {
            const rad = ((180 - (thresholdPercent / 100) * 180) * Math.PI) / 180;
            const x1 = 110 + 72 * Math.cos(rad);
            const y1 = 110 - 72 * Math.sin(rad);
            const x2 = 110 + 98 * Math.cos(rad);
            const y2 = 110 - 98 * Math.sin(rad);
            return (
              <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--status-medium)" strokeWidth="2.5" />
            );
          })()}

          {/* Pivot Point */}
          <circle cx="110" cy="110" r="5" fill="var(--text-primary)" />

          {/* Needle */}
          {(() => {
            const rad = (angleDeg * Math.PI) / 180;
            const nx = 110 + 70 * Math.cos(rad);
            const ny = 110 - 70 * Math.sin(rad);
            return (
              <line x1="110" y1="110" x2={nx} y2={ny} stroke="var(--text-primary)" strokeWidth="2.5" strokeLinecap="round" />
            );
          })()}
        </svg>

        {/* Big Solid Text Percentage (NO GLOW, NO SHADOW) */}
        <div style={{
          position: 'absolute',
          bottom: '0',
          left: '0',
          right: '0',
          textAlign: 'center'
        }}>
          <div className="mono" style={{
            fontSize: '2.4rem',
            fontWeight: '700',
            color: statusColor,
            lineHeight: 1
          }}>
            {probPercent.toFixed(2)}%
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Gradient Boosting Model
          </div>
        </div>
      </div>

      {/* Footer Operating State */}
      <div style={{
        width: '100%',
        marginTop: '0.95rem',
        padding: '0.55rem 0.95rem',
        borderRadius: '4px',
        backgroundColor: 'var(--bg-elevated)',
        border: '1px solid var(--border-normal)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '0.85rem'
      }}>
        <span style={{ color: 'var(--text-secondary)' }}>Evaluated Status:</span>
        <strong style={{ color: statusColor, fontSize: '0.9rem' }}>
          {status}
        </strong>
      </div>
    </div>
  );
}
