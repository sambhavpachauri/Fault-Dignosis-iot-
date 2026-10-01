import React from 'react';
import { Thermometer, Gauge, RotateCw, Wrench, Flame } from 'lucide-react';

function TechnicalSparkline({ data = [], color = '#5B7C99', height = 24, width = 80 }) {
  if (!data || data.length < 2) {
    return (
      <div style={{ width, height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>--</span>
      </div>
    );
  }

  const values = data.map(d => Number(d) || 0);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const points = values.map((val, idx) => {
    const x = (idx / (values.length - 1)) * width;
    const y = height - ((val - min) / range) * (height - 4) - 2;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');

  return (
    <svg width={width} height={height} style={{ overflow: 'visible' }}>
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="square"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
}

function TechnicalRangeBar({ value, min, max, normalMax, normalMin, unit, isNormal, statusColor }) {
  const clampedVal = Math.min(max, Math.max(min, value || 0));
  const pct = Math.min(100, Math.max(0, ((clampedVal - min) / (max - min)) * 100));

  return (
    <div style={{ width: '100%', marginTop: '0.65rem' }}>
      <div style={{
        position: 'relative',
        width: '100%',
        height: '4px',
        backgroundColor: 'var(--bg-secondary)',
        borderRadius: '2px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${pct}%`,
          height: '100%',
          backgroundColor: isNormal ? 'var(--border-strong)' : statusColor,
          borderRadius: '2px',
          transition: 'width 0.3s ease'
        }} />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
        <span>{min} {unit}</span>
        <span>{max} {unit}</span>
      </div>
    </div>
  );
}

export default function SensorMonitoring({ latest, history = [], waiting }) {
  if (waiting || !latest) {
    return (
      <div className="card-panel" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        Waiting for sensor telemetry...
      </div>
    );
  }

  const { sensors, diagnosis } = latest;
  const evals = diagnosis?.sensor_evaluations || {};

  const chronologicalHistory = [...history].reverse();
  const airHistory = chronologicalHistory.map(h => h.sensors?.air_temperature);
  const procHistory = chronologicalHistory.map(h => h.sensors?.process_temperature);
  const speedHistory = chronologicalHistory.map(h => h.sensors?.rotational_speed);
  const torqueHistory = chronologicalHistory.map(h => h.sensors?.torque);
  const wearHistory = chronologicalHistory.map(h => h.sensors?.tool_wear);

  const sensorConfigs = [
    {
      key: 'air_temperature',
      label: 'AIR TEMPERATURE',
      value: sensors?.air_temperature,
      unit: 'K',
      min: 290,
      max: 310,
      thresholdLabel: 'Limit: < 301.0 K',
      eval: evals.air_temperature,
      history: airHistory,
      icon: Thermometer
    },
    {
      key: 'process_temperature',
      label: 'PROCESS TEMPERATURE',
      value: sensors?.process_temperature,
      unit: 'K',
      min: 300,
      max: 320,
      thresholdLabel: 'Limit: < 312.0 K',
      eval: evals.process_temperature,
      history: procHistory,
      icon: Flame
    },
    {
      key: 'rotational_speed',
      label: 'ROTATIONAL SPEED',
      value: sensors?.rotational_speed,
      unit: 'RPM',
      min: 1000,
      max: 2000,
      thresholdLabel: 'Band: 1300 - 1650 RPM',
      eval: evals.rotational_speed,
      history: speedHistory,
      icon: RotateCw
    },
    {
      key: 'torque',
      label: 'SHAFT TORQUE',
      value: sensors?.torque,
      unit: 'Nm',
      min: 20,
      max: 80,
      thresholdLabel: 'Limit: < 55.0 Nm',
      eval: evals.torque,
      history: torqueHistory,
      icon: Gauge
    },
    {
      key: 'tool_wear',
      label: 'TOOL DEGRADATION',
      value: sensors?.tool_wear,
      unit: 'min',
      min: 0,
      max: 250,
      thresholdLabel: 'Limit: < 100 min',
      eval: evals.tool_wear,
      history: wearHistory,
      icon: Wrench
    }
  ];

  return (
    <section style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 0.15rem'
      }}>
        <h3 style={{
          fontSize: '0.95rem',
          fontWeight: '600',
          color: 'var(--text-secondary)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          Live Sensor Telemetry
        </h3>
        <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Operating Thresholds: diagnosis.py
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1rem'
      }}>
        {sensorConfigs.map(s => {
          const Icon = s.icon;
          const isNormal = s.eval ? s.eval.is_normal : true;
          const statusLabel = s.eval?.status_label || 'NORMAL';

          let statusBadgeClass = 'badge-normal';
          let statusColor = 'var(--status-normal)';
          if (statusLabel === 'ELEVATED' || statusLabel === 'INCREASING' || statusLabel === 'LOW') {
            statusBadgeClass = 'badge-medium';
            statusColor = 'var(--status-medium)';
          } else if (statusLabel === 'HIGH') {
            statusBadgeClass = 'badge-high';
            statusColor = 'var(--status-high)';
          } else if (statusLabel === 'CRITICAL') {
            statusBadgeClass = 'badge-critical';
            statusColor = 'var(--status-critical)';
          }

          return (
            <div
              key={s.key}
              className="card-panel"
              style={{
                padding: '1.25rem 1.15rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                minHeight: '175px'
              }}
            >
              {/* Header: Label + Status Badge */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.45rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Icon size={16} color="var(--text-muted)" />
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: '600', letterSpacing: '0.03em' }}>
                    {s.label}
                  </span>
                </div>
                <span className={`badge-status ${statusBadgeClass}`} style={{ fontSize: '0.78rem', padding: '0.22rem 0.6rem' }}>
                  {statusLabel}
                </span>
              </div>

              {/* Large, Crisp, Solid Numerical Value (NO GLOW, NO SHADOW) */}
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.45rem', margin: '0.35rem 0' }}>
                <span className="mono" style={{
                  fontSize: '2.35rem',
                  fontWeight: '700',
                  color: 'var(--text-primary)',
                  lineHeight: 1
                }}>
                  {typeof s.value === 'number' ? s.value.toLocaleString() : '--'}
                </span>
                <span style={{ fontSize: '0.95rem', color: 'var(--text-muted)', fontWeight: '500' }}>
                  {s.unit}
                </span>
              </div>

              {/* Underneath: Technical Range & Threshold */}
              <div>
                <div style={{ fontSize: '0.8rem', color: isNormal ? 'var(--text-muted)' : statusColor, fontWeight: '500', marginBottom: '0.15rem' }}>
                  {s.thresholdLabel}
                </div>
                <TechnicalRangeBar
                  value={s.value}
                  min={s.min}
                  max={s.max}
                  unit={s.unit}
                  isNormal={isNormal}
                  statusColor={statusColor}
                />
              </div>

              {/* Sparkline in lower corner */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderTop: '1px solid var(--border-normal)',
                paddingTop: '0.5rem',
                marginTop: '0.6rem'
              }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Recent trend</span>
                <TechnicalSparkline data={s.history} color={isNormal ? 'var(--accent)' : statusColor} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
