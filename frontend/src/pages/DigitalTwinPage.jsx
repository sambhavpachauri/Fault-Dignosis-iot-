import React from 'react';
import MachineSchematic from '../components/MachineSchematic';
import { Activity, Cpu } from 'lucide-react';

export default function DigitalTwinPage({ latest, waiting }) {
  if (waiting || !latest) {
    return (
      <div className="card-panel" style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Cpu size={32} color="var(--accent)" style={{ marginBottom: '0.75rem', opacity: 0.6 }} />
        <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>Digital Twin Standing By</h3>
        <p style={{ fontSize: '0.825rem' }}>Awaiting live telemetry from MQTT broker to render real-time CAD kinematics...</p>
      </div>
    );
  }

  const { sensors } = latest;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Schematic Component */}
      <MachineSchematic sensors={sensors} diagnosis={latest.diagnosis} />

      {/* Real-Time CAD Kinematics & Physical Spec Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '1rem'
      }}>
        <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={16} color="var(--accent)" />
            <h4 style={{ fontSize: '0.85rem', fontWeight: '600', textTransform: 'uppercase', color: 'var(--text-primary)', margin: 0 }}>
              Operating Thermodynamics
            </h4>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Thermal Differential (&Delta;T)</span>
              <strong className="mono" style={{ color: 'var(--text-primary)' }}>
                {(sensors.process_temperature - sensors.air_temperature).toFixed(2)} K
              </strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Heat Dissipation Status</span>
              <span className={`badge-status ${(sensors.process_temperature - sensors.air_temperature) > 12 ? 'badge-high' : 'badge-normal'}`}>
                {(sensors.process_temperature - sensors.air_temperature) > 12 ? 'CONSTRAINED' : 'NOMINAL'}
              </span>
            </div>
          </div>
        </div>

        <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Cpu size={16} color="var(--status-normal)" />
            <h4 style={{ fontSize: '0.85rem', fontWeight: '600', textTransform: 'uppercase', color: 'var(--text-primary)', margin: 0 }}>
              Mechanical Power & Torque
            </h4>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Estimated Shaft Power (P = &tau; &times; &omega;)</span>
              <strong className="mono" style={{ color: 'var(--text-primary)' }}>
                {((sensors.torque * (sensors.rotational_speed * 2 * Math.PI / 60)) / 1000).toFixed(2)} kW
              </strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Torsional Load Margin</span>
              <strong className="mono" style={{ color: sensors.torque > 55 ? 'var(--status-critical)' : 'var(--text-primary)' }}>
                {Math.max(0, 55 - sensors.torque).toFixed(1)} Nm to limit
              </strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
