import React, { useState } from 'react';
import { LineChart as ChartIcon } from 'lucide-react';

export default function SensorTrendsChart({ history = [] }) {
  const [selectedMetric, setSelectedMetric] = useState('probability');
  const [hoveredPoint, setHoveredPoint] = useState(null);

  const data = [...history].reverse();

  const metricsConfig = {
    probability: {
      label: 'Failure Risk Probability',
      unit: '%',
      threshold: 40,
      thresholdLabel: 'Risk Cutoff (40%)',
      color: 'var(--status-critical)',
      getValue: (r) => (r.diagnosis?.failure_probability || 0) * 100,
      format: (v) => `${v.toFixed(2)}%`
    },
    temperatures: {
      label: 'Temperatures (Process & Air)',
      unit: 'K',
      threshold: 301,
      thresholdLabel: 'Air Limit (301 K)',
      color: 'var(--accent)',
      colorSecondary: 'var(--status-high)',
      getValue: (r) => r.sensors?.process_temperature || 0,
      getValueSecondary: (r) => r.sensors?.air_temperature || 0,
      format: (v) => `${v.toFixed(1)} K`
    },
    speed: {
      label: 'Rotational Speed',
      unit: 'RPM',
      threshold: 1300,
      thresholdLabel: 'Lower Bound (1300 RPM)',
      color: 'var(--status-normal)',
      getValue: (r) => r.sensors?.rotational_speed || 0,
      format: (v) => `${Math.round(v)} RPM`
    },
    torque: {
      label: 'Shaft Torque',
      unit: 'Nm',
      threshold: 55,
      thresholdLabel: 'Upper Limit (55 Nm)',
      color: 'var(--status-medium)',
      getValue: (r) => r.sensors?.torque || 0,
      format: (v) => `${v.toFixed(1)} Nm`
    },
    tool_wear: {
      label: 'Tool Degradation',
      unit: 'min',
      threshold: 100,
      thresholdLabel: 'Wear Limit (100 min)',
      color: 'var(--text-secondary)',
      getValue: (r) => r.sensors?.tool_wear || 0,
      format: (v) => `${Math.round(v)} min`
    }
  };

  const currentMetric = metricsConfig[selectedMetric];

  if (!data || data.length < 2) {
    return (
      <div className="card-panel" style={{ padding: '1.75rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
          Collecting live telemetry data points for trend analysis (Current data points: {data.length})...
        </p>
      </div>
    );
  }

  // Calculate Chart Coordinates
  const width = 720;
  const height = 210;
  const padding = { top: 20, right: 25, bottom: 30, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const valuesPrimary = data.map(d => currentMetric.getValue(d));
  const valuesSecondary = currentMetric.getValueSecondary ? data.map(d => currentMetric.getValueSecondary(d)) : [];
  const allValues = [...valuesPrimary, ...valuesSecondary];
  if (currentMetric.threshold) allValues.push(currentMetric.threshold);

  const rawMin = Math.min(...allValues);
  const rawMax = Math.max(...allValues);
  const margin = (rawMax - rawMin) * 0.15 || 5;
  const minY = Math.floor(rawMin - margin);
  const maxY = Math.ceil(rawMax + margin);
  const rangeY = maxY - minY || 1;

  function getY(val) {
    return padding.top + chartHeight - ((val - minY) / rangeY) * chartHeight;
  }

  function getX(idx) {
    return padding.left + (idx / (data.length - 1)) * chartWidth;
  }

  const primaryPoints = valuesPrimary.map((val, idx) => `${getX(idx).toFixed(1)},${getY(val).toFixed(1)}`).join(' ');
  const secondaryPoints = valuesSecondary.length > 0
    ? valuesSecondary.map((val, idx) => `${getX(idx).toFixed(1)},${getY(val).toFixed(1)}`).join(' ')
    : null;

  const thresholdY = currentMetric.threshold ? getY(currentMetric.threshold) : null;

  return (
    <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {/* Header and Metric selector buttons */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.85rem',
        borderBottom: '1px solid var(--border-normal)',
        paddingBottom: '0.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <ChartIcon size={18} color="var(--accent)" />
          <h3 style={{
            fontSize: '1.05rem',
            fontWeight: '600',
            color: 'var(--text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            margin: 0
          }}>
            Telemetry Trends
          </h3>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            ({data.length} buffered)
          </span>
        </div>

        {/* Metric Toggles */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {Object.entries(metricsConfig).map(([key, config]) => {
            const isActive = selectedMetric === key;
            return (
              <button
                key={key}
                onClick={() => setSelectedMetric(key)}
                className={`btn-tech ${isActive ? 'btn-tech-active' : ''}`}
                style={{
                  fontSize: '0.85rem',
                  padding: '0.45rem 0.85rem'
                }}
              >
                {config.label.split(' ')[0]}
              </button>
            );
          })}
        </div>
      </div>

      {/* SVG Chart */}
      <div style={{ width: '100%', overflowX: 'auto', position: 'relative' }}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={{ width: '100%', height: 'auto', display: 'block', minWidth: '550px' }}
          onMouseLeave={() => setHoveredPoint(null)}
        >
          {/* Background grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct, idx) => {
            const yVal = minY + pct * rangeY;
            const yCoord = getY(yVal);
            return (
              <g key={idx}>
                <line
                  x1={padding.left}
                  y1={yCoord}
                  x2={width - padding.right}
                  y2={yCoord}
                  stroke="var(--border-normal)"
                  strokeWidth="1"
                  strokeDasharray="2,2"
                />
                <text
                  x={padding.left - 6}
                  y={yCoord + 3}
                  fill="var(--text-muted)"
                  fontSize="9"
                  fontFamily="JetBrains Mono"
                  textAnchor="end"
                >
                  {Math.round(yVal)}
                </text>
              </g>
            );
          })}

          {/* Threshold Line */}
          {thresholdY !== null && thresholdY >= padding.top && thresholdY <= padding.top + chartHeight && (
            <g>
              <line
                x1={padding.left}
                y1={thresholdY}
                x2={width - padding.right}
                y2={thresholdY}
                stroke="var(--status-medium)"
                strokeWidth="1.5"
                strokeDasharray="4,3"
              />
              <text
                x={width - padding.right - 4}
                y={thresholdY - 4}
                fill="var(--status-medium)"
                fontSize="8.5"
                fontWeight="600"
                textAnchor="end"
              >
                {currentMetric.thresholdLabel}
              </text>
            </g>
          )}

          {/* Primary Series Line (Solid, No Glow) */}
          <polyline
            fill="none"
            stroke={currentMetric.color}
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={primaryPoints}
          />

          {/* Secondary Series Line */}
          {secondaryPoints && (
            <polyline
              fill="none"
              stroke={currentMetric.colorSecondary}
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray="3,2"
              points={secondaryPoints}
            />
          )}

          {/* Data Points */}
          {data.map((record, idx) => {
            const x = getX(idx);
            const val = currentMetric.getValue(record);
            const y = getY(val);
            const isHovered = hoveredPoint?.idx === idx;

            return (
              <g key={idx}>
                <circle
                  cx={x}
                  cy={y}
                  r={isHovered ? 4 : 2}
                  fill={isHovered ? 'var(--text-primary)' : currentMetric.color}
                  stroke="var(--bg-panel)"
                  strokeWidth={1}
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={() => setHoveredPoint({ idx, record, x, y, val })}
                />
              </g>
            );
          })}

          {/* X Axis Time Labels */}
          {data.length > 0 && (
            <>
              <text x={padding.left} y={height - 8} fill="var(--text-muted)" fontSize="8.5" fontFamily="JetBrains Mono">
                {data[0].timestamp?.split(' ')[1] || ''}
              </text>
              <text x={width - padding.right} y={height - 8} fill="var(--text-muted)" fontSize="8.5" fontFamily="JetBrains Mono" textAnchor="end">
                {data[data.length - 1].timestamp?.split(' ')[1] || ''}
              </text>
            </>
          )}
        </svg>

        {/* Hover Tooltip Overlay (Flat, No Shadows) */}
        {hoveredPoint && (
          <div style={{
            position: 'absolute',
            left: `${(hoveredPoint.x / width) * 100}%`,
            top: `${(hoveredPoint.y / height) * 100}%`,
            transform: 'translate(-50%, -125%)',
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-strong)',
            borderRadius: '3px',
            padding: '0.25rem 0.5rem',
            pointerEvents: 'none',
            whiteSpace: 'nowrap',
            zIndex: 10
          }}>
            <div className="mono" style={{ fontSize: '0.75rem', fontWeight: '700', color: currentMetric.color }}>
              {currentMetric.format(hoveredPoint.val)}
            </div>
            <div className="mono" style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
              {hoveredPoint.record.timestamp}
            </div>
          </div>
        )}
      </div>

      {/* Legend Footer */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '0.7rem',
        color: 'var(--text-muted)',
        borderTop: '1px solid var(--border-normal)',
        paddingTop: '0.35rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span style={{ width: '8px', height: '2px', backgroundColor: currentMetric.color, display: 'inline-block' }} />
            <span>{currentMetric.label}</span>
          </div>
          {currentMetric.colorSecondary && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <span style={{ width: '8px', height: '2px', backgroundColor: currentMetric.colorSecondary, display: 'inline-block' }} />
              <span>Air Temperature (K)</span>
            </div>
          )}
        </div>
        <span>Hover node to inspect reading</span>
      </div>
    </div>
  );
}
