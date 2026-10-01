import React, { useState } from 'react';
import { BookOpen, HelpCircle, ListOrdered, Wrench, ShieldAlert } from 'lucide-react';

export default function RAGKnowledgePanel({ knowledge = [] }) {
  const [selectedTopicIdx, setSelectedTopicIdx] = useState(0);

  if (!knowledge || knowledge.length === 0) {
    return (
      <div className="card-panel" style={{ padding: '1.5rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.65rem',
          marginBottom: '0.85rem',
          borderBottom: '1px solid var(--border-normal)',
          paddingBottom: '0.65rem'
        }}>
          <BookOpen size={18} color="var(--accent)" />
          <h3 style={{
            fontSize: '0.98rem',
            fontWeight: '600',
            color: 'var(--text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            margin: 0
          }}>
            RAG Maintenance Knowledge
          </h3>
        </div>

        <div style={{
          padding: '1.75rem',
          textAlign: 'center',
          color: 'var(--text-muted)',
          fontSize: '0.95rem'
        }}>
          <p>No active abnormal condition requiring maintenance retrieval.</p>
          <p style={{ fontSize: '0.85rem', marginTop: '0.45rem' }}>
            When an anomaly or fault risk is identified, the FAISS vector index retrieves contextual repair instructions automatically.
          </p>
        </div>
      </div>
    );
  }

  const currentTopic = knowledge[selectedTopicIdx] || knowledge[0];

  return (
    <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '1.5rem' }}>
      {/* Panel Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
        borderBottom: '1px solid var(--border-normal)',
        paddingBottom: '0.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <BookOpen size={18} color="var(--accent)" />
          <h3 style={{
            fontSize: '0.98rem',
            fontWeight: '600',
            color: 'var(--text-primary)',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            margin: 0
          }}>
            RAG Maintenance Knowledge Base
          </h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          <span style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border-normal)', padding: '0.2rem 0.55rem', borderRadius: '3px' }}>
            FAISS • all-MiniLM-L6-v2
          </span>
          <span style={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border-normal)', padding: '0.2rem 0.55rem', borderRadius: '3px' }}>
            {knowledge.length} {knowledge.length === 1 ? 'Condition matched' : 'Conditions matched'}
          </span>
        </div>
      </div>

      {/* Multi-Condition Selector Tabs if multiple topics are returned */}
      {knowledge.length > 1 && (
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          overflowX: 'auto',
          paddingBottom: '0.45rem',
          borderBottom: '1px solid var(--border-normal)'
        }}>
          {knowledge.map((item, idx) => {
            const isSelected = idx === selectedTopicIdx;
            return (
              <button
                key={idx}
                onClick={() => setSelectedTopicIdx(idx)}
                className={`btn-tech ${isSelected ? 'btn-tech-active' : ''}`}
                style={{
                  fontSize: '0.85rem',
                  padding: '0.45rem 0.85rem',
                  whiteSpace: 'nowrap'
                }}
              >
                {item.topic}
              </button>
            );
          })}
        </div>
      )}

      {/* Structured Topic Display */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Topic Title */}
        <div style={{
          backgroundColor: 'var(--bg-elevated)',
          padding: '0.75rem 1rem',
          borderRadius: '4px',
          border: '1px solid var(--border-normal)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.65rem'
        }}>
          <ShieldAlert size={18} color="var(--status-high)" />
          <span style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--text-primary)', letterSpacing: '0.02em' }}>
            TOPIC: {currentTopic.topic}
          </span>
        </div>

        {/* 1. Condition Section */}
        {currentTopic.condition && (
          <div style={{
            backgroundColor: 'var(--bg-elevated)',
            borderLeft: '4px solid var(--accent)',
            padding: '0.85rem 1.15rem',
            borderRadius: '0 4px 4px 0'
          }}>
            <h4 style={{
              fontSize: '0.82rem',
              fontWeight: '700',
              textTransform: 'uppercase',
              color: 'var(--accent)',
              marginBottom: '0.35rem',
              letterSpacing: '0.04em'
            }}>
              Condition
            </h4>
            <p style={{ fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.5, margin: 0 }}>
              {currentTopic.condition}
            </p>
          </div>
        )}

        {/* 2. Side-by-side: Causes and Corrective Actions */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1rem'
        }}>
          {/* Causes */}
          <div style={{
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-normal)',
            borderRadius: '4px',
            padding: '1rem 1.15rem'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              marginBottom: '0.65rem',
              color: 'var(--status-medium)',
              fontSize: '0.85rem',
              fontWeight: '700',
              textTransform: 'uppercase',
              letterSpacing: '0.04em'
            }}>
              <HelpCircle size={16} />
              <span>Possible Causes</span>
            </div>
            <ul style={{
              margin: 0,
              paddingLeft: '1.25rem',
              fontSize: '0.88rem',
              color: 'var(--text-secondary)',
              lineHeight: 1.6
            }}>
              {currentTopic.possible_causes && currentTopic.possible_causes.length > 0 ? (
                currentTopic.possible_causes.map((cause, i) => (
                  <li key={i}>{cause}</li>
                ))
              ) : (
                <li>Inspect telemetry logs for anomaly correlation</li>
              )}
            </ul>
          </div>

          {/* Recommended Actions */}
          <div style={{
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-normal)',
            borderRadius: '4px',
            padding: '1rem 1.15rem'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              marginBottom: '0.65rem',
              color: 'var(--status-normal)',
              fontSize: '0.85rem',
              fontWeight: '700',
              textTransform: 'uppercase',
              letterSpacing: '0.04em'
            }}>
              <Wrench size={16} />
              <span>Recommended Actions</span>
            </div>
            <ul style={{
              margin: 0,
              paddingLeft: '1.25rem',
              fontSize: '0.88rem',
              color: 'var(--text-secondary)',
              lineHeight: 1.6
            }}>
              {currentTopic.recommended_actions && currentTopic.recommended_actions.length > 0 ? (
                currentTopic.recommended_actions.map((act, i) => (
                  <li key={i}>{act}</li>
                ))
              ) : (
                <li>Proceed with standard diagnostic maintenance checklist</li>
              )}
            </ul>
          </div>
        </div>

        {/* 3. Inspection Steps */}
        {currentTopic.inspection_steps && currentTopic.inspection_steps.length > 0 && (
          <div style={{
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-normal)',
            borderRadius: '4px',
            padding: '1rem 1.15rem'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              marginBottom: '0.65rem',
              color: 'var(--accent)',
              fontSize: '0.85rem',
              fontWeight: '700',
              textTransform: 'uppercase',
              letterSpacing: '0.04em'
            }}>
              <ListOrdered size={16} />
              <span>Standard Operating Inspection Steps</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.55rem' }}>
              {currentTopic.inspection_steps.map((step, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                  <span className="mono" style={{
                    backgroundColor: 'var(--bg-panel)',
                    border: '1px solid var(--border-normal)',
                    color: 'var(--text-primary)',
                    padding: '0.15rem 0.5rem',
                    borderRadius: '3px',
                    fontSize: '0.78rem',
                    fontWeight: '600',
                    flexShrink: 0
                  }}>
                    {i + 1}
                  </span>
                  <span style={{ lineHeight: 1.5 }}>
                    {step.replace(/^\d+[\.\)]\s*/, '')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
