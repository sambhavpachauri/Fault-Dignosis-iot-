import React from 'react';
import DiagnosisPanel from '../components/DiagnosisPanel';
import RecommendedAction from '../components/RecommendedAction';
import RAGKnowledgePanel from '../components/RAGKnowledgePanel';
import FailureRiskGauge from '../components/FailureRiskGauge';
import { Stethoscope } from 'lucide-react';

export default function DiagnosticsPage({ latest, waiting }) {
  if (waiting || !latest) {
    return (
      <div className="card-panel" style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Stethoscope size={32} color="var(--accent)" style={{ marginBottom: '0.75rem', opacity: 0.6 }} />
        <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>Diagnostic Engine Standing By</h3>
        <p style={{ fontSize: '0.825rem' }}>Awaiting live telemetry from MQTT broker to perform heuristic and vector evaluations...</p>
      </div>
    );
  }

  const { diagnosis } = latest;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner */}
      <div className="card-panel" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1.05rem', fontWeight: '600', color: 'var(--text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Stethoscope size={18} color="var(--accent)" />
            Machine Diagnostics & RAG Knowledge Manual
          </h2>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0.15rem 0 0 0' }}>
            Multi-tier heuristic evaluation correlated with dense FAISS vector maintenance database
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'center' }}>
          <span className={`badge-status ${diagnosis.severity === 'CRITICAL' ? 'badge-critical' : diagnosis.severity === 'HIGH' ? 'badge-high' : 'badge-normal'}`}>
            {diagnosis.severity} SEVERITY
          </span>
          <span className="mono" style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border-normal)', padding: '0.2rem 0.55rem', borderRadius: '3px' }}>
            Risk: {diagnosis.failure_probability_pct}
          </span>
        </div>
      </div>

      {/* Recommended Action */}
      <RecommendedAction
        recommendation={diagnosis.recommendation}
        severity={diagnosis.severity}
      />

      {/* 2-Column: Left Side Risk Gauge & Contributing Issues | Right Side Full RAG Knowledge */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(300px, 360px) 1fr',
        gap: '1.25rem',
        alignItems: 'start'
      }}>
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <FailureRiskGauge
            probability={diagnosis.failure_probability || 0}
            threshold={diagnosis.threshold || 0.40}
            status={diagnosis.status || "NORMAL"}
          />
          <DiagnosisPanel issues={diagnosis.issues} />
        </div>

        {/* Right Column: Full RAG Knowledge */}
        <div>
          <RAGKnowledgePanel knowledge={diagnosis.rag_knowledge} />
        </div>
      </div>
    </div>
  );
}
