import React from 'react';
import { Server, Radio, Cpu, Database, ShieldCheck } from 'lucide-react';

export default function SystemStatusPage({ statusMeta, dbStats, mqttConnected, backendConnected, historyLength = 0 }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner */}
      <div className="card-panel">
        <h2 style={{ fontSize: '1.05rem', fontWeight: '600', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)' }}>
          <Server size={18} color="var(--accent)" />
          System Health & Diagnostic Architecture
        </h2>
        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
          Broker telemetry status, ML model parameters, rule-engine thresholds, FAISS vector store, and persistent database telemetry
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {/* Connection & Ingestion Node */}
        <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', borderBottom: '1px solid var(--border-normal)', paddingBottom: '0.6rem' }}>
            <Radio size={16} color="var(--accent)" />
            <h3 style={{ fontSize: '0.82rem', fontWeight: '600', textTransform: 'uppercase', margin: 0, letterSpacing: '0.04em', color: 'var(--text-primary)' }}>
              IoT Telemetry Ingestion (MQTT)
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>MQTT Broker Endpoint</span>
              <span className="mono" style={{ color: 'var(--text-primary)' }}>127.0.0.1:1883</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Subscribed Topic</span>
              <span className="mono" style={{ color: 'var(--text-primary)' }}>factory/machine1/sensors</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Broker Connection Status</span>
              <span className={`badge-status ${mqttConnected ? 'badge-normal' : 'badge-critical'}`}>
                {mqttConnected ? 'CONNECTED' : 'DISCONNECTED'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Backend WebSocket Pipeline</span>
              <span className={`badge-status ${backendConnected ? 'badge-normal' : 'badge-critical'}`}>
                {backendConnected ? 'ACTIVE' : 'OFFLINE'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Total Readings Processed</span>
              <span className="mono" style={{ fontWeight: '600', color: 'var(--text-primary)' }}>
                {statusMeta?.total_readings_received ?? historyLength}
              </span>
            </div>
          </div>
        </div>

        {/* Database Persistence Storage */}
        <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', borderBottom: '1px solid var(--border-normal)', paddingBottom: '0.6rem' }}>
            <Database size={16} color="var(--accent)" />
            <h3 style={{ fontSize: '0.82rem', fontWeight: '600', textTransform: 'uppercase', margin: 0, letterSpacing: '0.04em', color: 'var(--text-primary)' }}>
              Persistent Relational Storage
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Storage Engine</span>
              <span style={{ color: 'var(--text-primary)', fontWeight: '500' }}>{dbStats?.storage_engine || 'SQLite (WAL Mode)'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Total Persisted Records</span>
              <span className="mono" style={{ color: 'var(--accent)', fontWeight: '600' }}>
                {dbStats?.total_persisted_records ?? statusMeta?.database_records ?? '0'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Active Machine ID</span>
              <span className="mono" style={{ color: 'var(--text-primary)' }}>Machine 1</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Deployment Compatibility</span>
              <span style={{ color: 'var(--status-normal)', fontWeight: '500' }}>Docker & Azure Ready</span>
            </div>
          </div>
        </div>

        {/* Machine Learning Model Spec */}
        <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', borderBottom: '1px solid var(--border-normal)', paddingBottom: '0.6rem' }}>
            <Cpu size={16} color="var(--accent)" />
            <h3 style={{ fontSize: '0.82rem', fontWeight: '600', textTransform: 'uppercase', margin: 0, letterSpacing: '0.04em', color: 'var(--text-primary)' }}>
              Predictive ML Pipeline
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Classifier Architecture</span>
              <span style={{ color: 'var(--text-primary)', fontWeight: '500' }}>Gradient Boosting (n=150, d=3)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Decision Threshold</span>
              <span className="mono" style={{ color: 'var(--status-medium)', fontWeight: '600' }}>0.40 (40.0%)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Dataset Origin</span>
              <span style={{ color: 'var(--text-primary)' }}>UCI AI4I 2020 Predictive Maint.</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Model Artifact</span>
              <span className="mono" style={{ color: 'var(--accent)' }}>models/fault_model.pkl</span>
            </div>
          </div>
        </div>

        {/* RAG Vector Database Spec */}
        <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', borderBottom: '1px solid var(--border-normal)', paddingBottom: '0.6rem' }}>
            <Database size={16} color="var(--accent)" />
            <h3 style={{ fontSize: '0.82rem', fontWeight: '600', textTransform: 'uppercase', margin: 0, letterSpacing: '0.04em', color: 'var(--text-primary)' }}>
              RAG Knowledge Architecture
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Vector Index Type</span>
              <span style={{ color: 'var(--text-primary)', fontWeight: '500' }}>FAISS IndexFlatL2</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Dense Embedding Model</span>
              <span className="mono" style={{ color: 'var(--accent)' }}>all-MiniLM-L6-v2 (384-dim)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0', borderBottom: '1px solid var(--border-normal)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Vector Store Location</span>
              <span className="mono" style={{ color: 'var(--text-primary)' }}>rag/maintenance.index</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.35rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Knowledge Source</span>
              <span className="mono" style={{ color: 'var(--text-secondary)' }}>knowledge_base/maintenance_knowledge.txt</span>
            </div>
          </div>
        </div>

        {/* Rule Engine Specifications */}
        <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', borderBottom: '1px solid var(--border-normal)', paddingBottom: '0.6rem' }}>
            <ShieldCheck size={16} color="var(--accent)" />
            <h3 style={{ fontSize: '0.82rem', fontWeight: '600', textTransform: 'uppercase', margin: 0, letterSpacing: '0.04em', color: 'var(--text-primary)' }}>
              Diagnostic Threshold Rules (diagnosis.py)
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.78rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.2rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Air Temperature</span>
              <span className="mono" style={{ color: 'var(--text-primary)' }}>Elevated if &ge; 301.0 K</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.2rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Process Temperature</span>
              <span className="mono" style={{ color: 'var(--text-primary)' }}>High if &ge; 312.0 K</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.2rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Rotational Speed</span>
              <span className="mono" style={{ color: 'var(--text-primary)' }}>Low &lt; 1300 RPM | High &gt; 1650 RPM</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.2rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Torque</span>
              <span className="mono" style={{ color: 'var(--text-primary)' }}>High if &ge; 55.0 Nm</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.2rem 0' }}>
              <span style={{ color: 'var(--text-muted)' }}>Tool Wear</span>
              <span className="mono" style={{ color: 'var(--text-primary)' }}>Increasing &ge; 100 min | High &ge; 150 min</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
