import React from 'react';
import AlertBanner from '../components/AlertBanner';
import MachineStatusCard from '../components/MachineStatusCard';
import SensorMonitoring from '../components/SensorMonitoring';
import FailureRiskGauge from '../components/FailureRiskGauge';
import DiagnosisPanel from '../components/DiagnosisPanel';
import RecommendedAction from '../components/RecommendedAction';
import SimulationControlBar from '../components/SimulationControlBar';
import { Terminal, Radio, ArrowRight, BookOpen, Layers } from 'lucide-react';

export default function DashboardPage({
  latest,
  history,
  waiting,
  activeAlert,
  acknowledgeAlert,
  mqttConnected,
  setActiveTab
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* 1. Technical Collapsible Scenario Trigger Toolbar */}
      <SimulationControlBar />

      {waiting || !latest ? (
        <div className="card-panel" style={{
          padding: '3.5rem 2rem',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '1.25rem',
          minHeight: '340px'
        }}>
          <div style={{
            padding: '1rem',
            borderRadius: '4px',
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-normal)'
          }}>
            <Radio size={32} color="var(--accent)" />
          </div>

          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
              Awaiting Machine Telemetry Stream
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', maxWidth: '540px', margin: '0 auto', lineHeight: 1.5 }}>
              The ingestion engine is subscribed to MQTT topic <span className="mono" style={{ color: 'var(--text-primary)' }}>factory/machine1/sensors</span>.
              Use the control drawer above or start the Python simulator to transmit telemetry frames.
            </p>
          </div>

          <div style={{
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-normal)',
            borderRadius: '4px',
            padding: '0.65rem 1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            fontSize: '0.825rem'
          }}>
            <Terminal size={14} color="var(--status-normal)" />
            <code className="mono" style={{ color: 'var(--status-normal)', fontWeight: '600' }}>python3 ai4i_machine_simulator.py</code>
          </div>
        </div>
      ) : (
        <>
          {/* 2. Alarm Banner (if HIGH or CRITICAL severity active) */}
          <AlertBanner alert={activeAlert} onAcknowledge={acknowledgeAlert} />

          {/* 3. Machine Status Overview Card */}
          <MachineStatusCard latest={latest} waiting={waiting} />

          {/* 4. Live Sensor Telemetry Strip */}
          <SensorMonitoring latest={latest} history={history} waiting={waiting} />

          {/* 5. Two-Column Diagnostic & Decision Panel */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(340px, 420px) 1fr',
            gap: '1.5rem',
            alignItems: 'stretch'
          }}>
            {/* Left Column: Failure Probability Gauge + Contributing Conditions */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <FailureRiskGauge
                probability={latest.diagnosis?.failure_probability || 0}
                threshold={latest.diagnosis?.threshold || 0.40}
                status={latest.diagnosis?.status || "NORMAL"}
              />
              <DiagnosisPanel issues={latest.diagnosis?.issues} />
            </div>

            {/* Right Column: Prominent Recommended Action + Quick Nav to 3D Twin & RAG */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', justifyContent: 'space-between' }}>
              <RecommendedAction
                recommendation={latest.diagnosis?.recommendation}
                severity={latest.diagnosis?.severity}
              />

              {/* Navigation Cards to 3D Digital Twin and RAG Maintenance Manual */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                gap: '1.25rem'
              }}>
                {/* Link to 3D Digital Twin */}
                <div
                  onClick={() => setActiveTab('digital-twin')}
                  className="card-panel"
                  style={{
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    minHeight: '135px',
                    padding: '1.25rem 1.5rem'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <Layers size={22} color="var(--accent)" />
                    <div>
                      <h4 style={{ fontSize: '1.05rem', fontWeight: '600', color: 'var(--text-primary)', margin: 0 }}>
                        3D Digital Twin
                      </h4>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
                        Inspect asset assembly CAD schematic
                      </p>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.9rem', color: 'var(--accent)', fontWeight: '600', marginTop: '0.85rem' }}>
                    <span>Launch 3D Asset Inspector</span>
                    <ArrowRight size={16} />
                  </div>
                </div>

                {/* Link to RAG Knowledge Manual */}
                <div
                  onClick={() => setActiveTab('diagnostics')}
                  className="card-panel"
                  style={{
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    minHeight: '135px',
                    padding: '1.25rem 1.5rem'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <BookOpen size={22} color="var(--status-normal)" />
                    <div>
                      <h4 style={{ fontSize: '1.05rem', fontWeight: '600', color: 'var(--text-primary)', margin: 0 }}>
                        RAG Maintenance Manual
                      </h4>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
                        {latest.diagnosis?.rag_knowledge?.length || 0} troubleshooting guides active
                      </p>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.9rem', color: 'var(--status-normal)', fontWeight: '600', marginTop: '0.85rem' }}>
                    <span>View Inspection Steps</span>
                    <ArrowRight size={16} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
