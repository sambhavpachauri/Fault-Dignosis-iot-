import React, { useState } from 'react';
import { Layers, RotateCw, Flame, Wrench } from 'lucide-react';

export default function MachineSchematic({ sensors, diagnosis }) {
  const [selectedPart, setSelectedPart] = useState('all');
  const evals = diagnosis?.sensor_evaluations || {};

  const motorAlert = !evals.rotational_speed?.is_normal || !evals.torque?.is_normal;
  const thermalAlert = !evals.air_temperature?.is_normal || !evals.process_temperature?.is_normal;
  const toolAlert = !evals.tool_wear?.is_normal;

  return (
    <div className="card-panel" style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '1.25rem'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
        borderBottom: '1px solid var(--border-normal)',
        paddingBottom: '0.95rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Layers size={20} color="var(--accent)" />
          <div>
            <h3 style={{
              fontSize: '1.2rem',
              fontWeight: '600',
              color: 'var(--text-primary)',
              letterSpacing: '-0.01em',
              margin: 0
            }}>
              Asset Subsystem Schematic
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.2rem 0 0 0' }}>
              Technical Assembly Layout • Spindle Drive (Machine 1)
            </p>
          </div>
        </div>

        {/* Subsystem Toggles */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {[
            { id: 'all', label: 'Complete Asset' },
            { id: 'motor', label: 'Drive Motor', alert: motorAlert },
            { id: 'thermal', label: 'Thermal Sleeve', alert: thermalAlert },
            { id: 'tool', label: 'Tool Head', alert: toolAlert }
          ].map(tab => {
            const isSelected = selectedPart === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedPart(tab.id)}
                className={`btn-tech ${isSelected ? 'btn-tech-active' : ''}`}
                style={{
                  fontSize: '0.85rem',
                  padding: '0.45rem 0.85rem'
                }}
              >
                {tab.alert && <span className="status-dot status-dot-high" style={{ width: '7px', height: '7px' }} />}
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Technical Schematic Vector Canvas (Flat, Technical, Matte) */}
      <div style={{
        position: 'relative',
        width: '100%',
        backgroundColor: 'var(--bg-secondary)',
        borderRadius: '4px',
        border: '1px solid var(--border-normal)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.25rem',
        overflow: 'hidden'
      }}>
        <svg
          viewBox="0 0 960 330"
          style={{ width: '100%', height: 'auto', maxHeight: '350px' }}
        >
          {/* Engineering Centerline Axis */}
          <line x1="60" y1="185" x2="900" y2="185" stroke="var(--border-normal)" strokeWidth="1" strokeDasharray="6,4" />

          {/* ============================================================== */}
          {/* SECTION 1: DRIVE MOTOR                                         */}
          {/* ============================================================== */}
          <g opacity={selectedPart === 'all' || selectedPart === 'motor' ? 1 : 0.25} style={{ transition: 'opacity 0.2s' }}>
            {/* Motor Main Housing */}
            <rect
              x="90"
              y="110"
              width="170"
              height="150"
              rx="4"
              fill="var(--bg-panel)"
              stroke={motorAlert ? 'var(--status-high)' : 'var(--border-strong)'}
              strokeWidth="1.5"
            />
            {/* Cooling Fin Lines */}
            {[120, 150, 180, 210, 240].map((x) => (
              <line key={x} x1={x} y1="95" x2={x} y2="110" stroke={motorAlert ? 'var(--status-high)' : 'var(--border-strong)'} strokeWidth="2" />
            ))}

            {/* Motor Center Label */}
            <text x="175" y="175" fill="var(--text-primary)" fontSize="12" fontWeight="600" textAnchor="middle" letterSpacing="0.04em">
              DRIVE MOTOR
            </text>
            <text x="175" y="195" fill="var(--text-secondary)" fontSize="10" textAnchor="middle" fontFamily="JetBrains Mono">
              {sensors?.rotational_speed} RPM | {sensors?.torque} Nm
            </text>
          </g>

          {/* Shaft Coupling */}
          <rect x="260" y="170" width="80" height="30" fill="var(--bg-elevated)" stroke="var(--border-normal)" strokeWidth="1.5" />
          <text x="300" y="190" fill="var(--text-muted)" fontSize="8.5" textAnchor="middle" fontWeight="500">SHAFT</text>

          {/* ============================================================== */}
          {/* SECTION 2: SPINDLE & THERMAL SLEEVE                            */}
          {/* ============================================================== */}
          <g opacity={selectedPart === 'all' || selectedPart === 'thermal' ? 1 : 0.25} style={{ transition: 'opacity 0.2s' }}>
            {/* Spindle Housing */}
            <rect
              x="340"
              y="120"
              width="240"
              height="130"
              rx="4"
              fill="var(--bg-panel)"
              stroke={thermalAlert ? 'var(--status-high)' : 'var(--border-strong)'}
              strokeWidth="1.5"
            />
            {/* Bearing Inspection Ports */}
            <rect x="375" y="155" width="40" height="60" rx="3" fill="var(--bg-elevated)" stroke="var(--border-normal)" strokeWidth="1" />
            <text x="395" y="190" fill="var(--text-muted)" fontSize="9" textAnchor="middle" fontWeight="600">BRG-1</text>

            <rect x="505" y="155" width="40" height="60" rx="3" fill="var(--bg-elevated)" stroke="var(--border-normal)" strokeWidth="1" />
            <text x="525" y="190" fill="var(--text-muted)" fontSize="9" textAnchor="middle" fontWeight="600">BRG-2</text>

            {/* Sleeve Label */}
            <text x="460" y="145" fill="var(--text-primary)" fontSize="12" fontWeight="600" textAnchor="middle" letterSpacing="0.04em">
              SPINDLE & THERMAL SLEEVE
            </text>
            <text x="460" y="235" fill="var(--text-secondary)" fontSize="10" textAnchor="middle" fontFamily="JetBrains Mono">
              Proc: {sensors?.process_temperature} K | Air: {sensors?.air_temperature} K
            </text>
          </g>

          {/* Collet Chuck */}
          <polygon points="580,145 660,160 660,210 580,225" fill="var(--bg-elevated)" stroke="var(--border-normal)" strokeWidth="1.5" />
          <text x="615" y="190" fill="var(--text-muted)" fontSize="8.5" textAnchor="middle" fontWeight="500">CHUCK</text>

          {/* ============================================================== */}
          {/* SECTION 3: CUTTING TOOL HEAD                                   */}
          {/* ============================================================== */}
          <g opacity={selectedPart === 'all' || selectedPart === 'tool' ? 1 : 0.25} style={{ transition: 'opacity 0.2s' }}>
            <polygon
              points="660,175 790,178 840,185 790,192 660,195"
              fill="var(--bg-panel)"
              stroke={toolAlert ? 'var(--status-critical)' : 'var(--border-strong)'}
              strokeWidth="1.5"
            />
            {/* Tool Tip Focal Indicator */}
            <circle cx="840" cy="185" r="4" fill={toolAlert ? 'var(--status-critical)' : 'var(--status-normal)'} />

            <text x="740" y="165" fill="var(--text-primary)" fontSize="11" fontWeight="600" textAnchor="middle" letterSpacing="0.04em">
              CUTTING TOOL
            </text>
            <text x="740" y="215" fill="var(--text-secondary)" fontSize="10" textAnchor="middle" fontFamily="JetBrains Mono">
              Wear: {sensors?.tool_wear} min
            </text>
          </g>

          {/* Technical Data Annotation Banners (Above Parts with Clear Dashed Leader Lines) */}
          {/* Motor Callout Pin */}
          <g transform="translate(175, 40)">
            <rect x="-80" y="-22" width="160" height="40" rx="4" fill="var(--bg-elevated)" stroke={motorAlert ? 'var(--status-high)' : 'var(--border-normal)'} strokeWidth="1" />
            <text x="0" y="-7" fill={motorAlert ? 'var(--status-high)' : 'var(--text-primary)'} fontSize="11" fontWeight="700" textAnchor="middle" fontFamily="JetBrains Mono">
              {sensors?.rotational_speed} RPM
            </text>
            <text x="0" y="10" fill="var(--text-secondary)" fontSize="9.5" textAnchor="middle" fontFamily="JetBrains Mono">
              Torque: {sensors?.torque} Nm
            </text>
            <line x1="0" y1="18" x2="0" y2="70" stroke={motorAlert ? 'var(--status-high)' : 'var(--border-normal)'} strokeWidth="1" strokeDasharray="3,3" />
          </g>

          {/* Spindle Callout Pin */}
          <g transform="translate(460, 40)">
            <rect x="-90" y="-22" width="180" height="40" rx="4" fill="var(--bg-elevated)" stroke={thermalAlert ? 'var(--status-high)' : 'var(--border-normal)'} strokeWidth="1" />
            <text x="0" y="-7" fill={thermalAlert ? 'var(--status-high)' : 'var(--text-primary)'} fontSize="11" fontWeight="700" textAnchor="middle" fontFamily="JetBrains Mono">
              Proc Temp: {sensors?.process_temperature} K
            </text>
            <text x="0" y="10" fill="var(--text-secondary)" fontSize="9.5" textAnchor="middle" fontFamily="JetBrains Mono">
              Air Ambient: {sensors?.air_temperature} K
            </text>
            <line x1="0" y1="18" x2="0" y2="80" stroke={thermalAlert ? 'var(--status-high)' : 'var(--border-normal)'} strokeWidth="1" strokeDasharray="3,3" />
          </g>

          {/* Tooling Callout Pin */}
          <g transform="translate(740, 50)">
            <rect x="-75" y="-22" width="150" height="40" rx="4" fill="var(--bg-elevated)" stroke={toolAlert ? 'var(--status-critical)' : 'var(--border-normal)'} strokeWidth="1" />
            <text x="0" y="-7" fill={toolAlert ? 'var(--status-critical)' : 'var(--status-normal)'} fontSize="11" fontWeight="700" textAnchor="middle" fontFamily="JetBrains Mono">
              Wear: {sensors?.tool_wear} min
            </text>
            <text x="0" y="10" fill="var(--text-secondary)" fontSize="9.5" textAnchor="middle" fontFamily="JetBrains Mono">
              {evals.tool_wear?.status_label || 'NORMAL'}
            </text>
            <line x1="0" y1="18" x2="0" y2="115" stroke={toolAlert ? 'var(--status-critical)' : 'var(--border-normal)'} strokeWidth="1" strokeDasharray="3,3" />
          </g>
        </svg>
      </div>

      {/* Subsystem Metric Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '1.25rem'
      }}>
        {/* Subsystem 1: Motor */}
        <div style={{
          backgroundColor: 'var(--bg-elevated)',
          border: `1px solid ${motorAlert ? 'var(--status-high)' : 'var(--border-normal)'}`,
          borderRadius: '4px',
          padding: '1.2rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
              <RotateCw size={17} color="var(--text-muted)" />
              <span style={{ fontSize: '0.95rem', fontWeight: '600', color: 'var(--text-primary)' }}>Motor & Drivetrain</span>
            </div>
            <span className={`badge-status ${motorAlert ? 'badge-high' : 'badge-normal'}`} style={{ fontSize: '0.8rem' }}>
              {motorAlert ? 'ATTENTION' : 'NOMINAL'}
            </span>
          </div>
          <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Rotational Speed:</span>
              <strong className="mono" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{sensors?.rotational_speed} RPM</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Drive Torque:</span>
              <strong className="mono" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{sensors?.torque} Nm</strong>
            </div>
          </div>
        </div>

        {/* Subsystem 2: Thermal */}
        <div style={{
          backgroundColor: 'var(--bg-elevated)',
          border: `1px solid ${thermalAlert ? 'var(--status-high)' : 'var(--border-normal)'}`,
          borderRadius: '4px',
          padding: '1.2rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
              <Flame size={17} color="var(--text-muted)" />
              <span style={{ fontSize: '0.95rem', fontWeight: '600', color: 'var(--text-primary)' }}>Thermal Dissipation</span>
            </div>
            <span className={`badge-status ${thermalAlert ? 'badge-high' : 'badge-normal'}`} style={{ fontSize: '0.8rem' }}>
              {thermalAlert ? 'OVERHEATING' : 'OPTIMAL'}
            </span>
          </div>
          <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Process Temperature:</span>
              <strong className="mono" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{sensors?.process_temperature} K</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Ambient Air:</span>
              <strong className="mono" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{sensors?.air_temperature} K</strong>
            </div>
          </div>
        </div>

        {/* Subsystem 3: Tooling */}
        <div style={{
          backgroundColor: 'var(--bg-elevated)',
          border: `1px solid ${toolAlert ? 'var(--status-critical)' : 'var(--border-normal)'}`,
          borderRadius: '4px',
          padding: '1.2rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
              <Wrench size={17} color="var(--text-muted)" />
              <span style={{ fontSize: '0.95rem', fontWeight: '600', color: 'var(--text-primary)' }}>Spindle Tooling</span>
            </div>
            <span className={`badge-status ${toolAlert ? 'badge-critical' : 'badge-normal'}`} style={{ fontSize: '0.8rem' }}>
              {toolAlert ? 'WEAR DETECTED' : 'SERVICEABLE'}
            </span>
          </div>
          <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Accumulated Wear:</span>
              <strong className="mono" style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{sensors?.tool_wear} min</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Threshold Range:</span>
              <span className="mono" style={{ color: 'var(--text-secondary)' }}>&lt; 100 min nominal</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
