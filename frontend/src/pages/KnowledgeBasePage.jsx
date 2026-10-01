import React, { useState, useEffect } from 'react';
import { BookOpen, Search, HelpCircle, ListOrdered, Wrench, ShieldAlert } from 'lucide-react';
import { fetchAllKnowledge, searchKnowledge } from '../services/api';

export default function KnowledgeBasePage() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTopic, setSelectedTopic] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await fetchAllKnowledge();
        setTopics(data);
        if (data.length > 0) setSelectedTopic(data[0]);
      } catch (e) {
        console.error("Failed to load knowledge topics", e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      const data = await fetchAllKnowledge();
      setTopics(data);
      if (data.length > 0) setSelectedTopic(data[0]);
      return;
    }

    try {
      setLoading(true);
      const results = await searchKnowledge(searchQuery);
      setTopics(results);
      if (results.length > 0) setSelectedTopic(results[0]);
    } catch (e) {
      console.error("Search failed", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Search Bar & Header */}
      <div className="card-panel" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.05rem', fontWeight: '600', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)' }}>
            <BookOpen size={18} color="var(--accent)" />
            Machine Maintenance Knowledge Base
          </h2>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
            Curated engineering repair guides indexed into FAISS dense vector space
          </p>
        </div>

        <form onSubmit={handleSearch} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-normal)',
            borderRadius: '4px',
            padding: '0.35rem 0.65rem'
          }}>
            <Search size={14} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Search guides (e.g. high torque)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: 'var(--text-primary)',
                fontSize: '0.8rem',
                width: '240px'
              }}
            />
          </div>
          <button type="submit" className="btn-tech" style={{ fontSize: '0.78rem', padding: '0.4rem 0.75rem' }}>
            Search
          </button>
        </form>
      </div>

      {/* Main 2-Column Layout: Sidebar of topics + Detailed document view */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(240px, 320px) 1fr', gap: '1.25rem' }}>
        {/* Left Topic Sidebar */}
        <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '680px', overflowY: 'auto' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.25rem', letterSpacing: '0.04em' }}>
            Knowledge Articles ({topics.length})
          </div>

          {loading ? (
            <div style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>Loading vector index...</div>
          ) : topics.length === 0 ? (
            <div style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>No matching maintenance guides found.</div>
          ) : (
            topics.map((t, idx) => {
              const isSelected = selectedTopic?.topic === t.topic;
              return (
                <button
                  key={idx}
                  onClick={() => setSelectedTopic(t)}
                  style={{
                    textAlign: 'left',
                    padding: '0.65rem 0.85rem',
                    borderRadius: '4px',
                    border: `1px solid ${isSelected ? 'var(--accent)' : 'var(--border-normal)'}`,
                    backgroundColor: isSelected ? 'var(--accent-subtle)' : 'transparent',
                    color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    fontWeight: isSelected ? '600' : '400',
                    transition: 'background-color 0.15s ease, border-color 0.15s ease'
                  }}
                >
                  <div style={{ color: isSelected ? 'var(--text-primary)' : 'var(--text-primary)', marginBottom: '0.15rem' }}>
                    {t.topic}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {t.condition}
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Right Topic Details */}
        {selectedTopic ? (
          <div className="card-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              backgroundColor: 'var(--bg-secondary)',
              padding: '0.85rem 1rem',
              borderRadius: '4px',
              border: '1px solid var(--border-normal)'
            }}>
              <ShieldAlert size={18} color="var(--accent)" />
              <h3 style={{ fontSize: '1rem', fontWeight: '600', color: 'var(--text-primary)', margin: 0 }}>
                {selectedTopic.topic}
              </h3>
            </div>

            {/* Condition */}
            {selectedTopic.condition && (
              <div style={{
                backgroundColor: 'var(--bg-secondary)',
                borderLeft: '3px solid var(--accent)',
                padding: '0.85rem 1rem',
                borderRadius: '0 4px 4px 0'
              }}>
                <div style={{ fontSize: '0.72rem', fontWeight: '600', textTransform: 'uppercase', color: 'var(--accent)', marginBottom: '0.25rem', letterSpacing: '0.04em' }}>
                  Condition Overview
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
                  {selectedTopic.condition}
                </p>
              </div>
            )}

            {/* Possible Causes & Recommended Actions Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
              {/* Causes */}
              <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-normal)', borderRadius: '4px', padding: '1rem' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', fontWeight: '600', color: 'var(--status-medium)', textTransform: 'uppercase', marginBottom: '0.65rem', letterSpacing: '0.04em' }}>
                  <HelpCircle size={15} color="var(--status-medium)" />
                  Possible Causes
                </h4>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {selectedTopic.possible_causes?.map((c, i) => (
                    <li key={i} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', gap: '0.5rem' }}>
                      <span style={{ color: 'var(--status-medium)' }}>•</span>
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Recommended Actions */}
              <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-normal)', borderRadius: '4px', padding: '1rem' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', fontWeight: '600', color: 'var(--status-normal)', textTransform: 'uppercase', marginBottom: '0.65rem', letterSpacing: '0.04em' }}>
                  <Wrench size={15} color="var(--status-normal)" />
                  Recommended Corrective Actions
                </h4>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {selectedTopic.recommended_actions?.map((a, i) => (
                    <li key={i} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', gap: '0.5rem' }}>
                      <span style={{ color: 'var(--status-normal)' }}>✓</span>
                      <span>{a}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Inspection Steps */}
            {selectedTopic.inspection_steps && (
              <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-normal)', borderRadius: '4px', padding: '1rem' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', fontWeight: '600', color: 'var(--accent)', textTransform: 'uppercase', marginBottom: '0.65rem', letterSpacing: '0.04em' }}>
                  <ListOrdered size={15} color="var(--accent)" />
                  Standard Operating Inspection Steps
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {selectedTopic.inspection_steps.map((s, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.65rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      <span className="mono" style={{ backgroundColor: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border-normal)', padding: '0.1rem 0.4rem', borderRadius: '3px', fontSize: '0.72rem', fontWeight: '600' }}>
                        {i + 1}
                      </span>
                      <span>{s.replace(/^\d+[\.\)]\s*/, '')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="card-panel" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Select a maintenance guide to view detailed troubleshooting instructions.
          </div>
        )}
      </div>
    </div>
  );
}
