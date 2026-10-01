import React, { useState } from 'react';
import Header from './components/Header';
import DashboardPage from './pages/DashboardPage';
import DigitalTwinPage from './pages/DigitalTwinPage';
import DiagnosticsPage from './pages/DiagnosticsPage';
import TelemetryHistoryTable from './components/TelemetryHistoryTable';
import SensorTrendsChart from './components/SensorTrendsChart';
import SystemStatusPage from './pages/SystemStatusPage';
import { useTelemetry } from './hooks/useTelemetry';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const {
    latest,
    history,
    backendConnected,
    mqttConnected,
    isPaused,
    waiting,
    lastReceived,
    activeAlert,
    activeMachine,
    setActiveMachine,
    statusMeta,
    dbStats,
    historyLoading,
    loadHistory,
    togglePause,
    acknowledgeAlert,
    refreshManual
  } = useTelemetry();

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: 'var(--bg-primary)',
      color: 'var(--text-primary)',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header Bar */}
      <Header
        mqttConnected={mqttConnected}
        backendConnected={backendConnected}
        lastReceived={lastReceived}
        activeMachine={activeMachine}
        setActiveMachine={setActiveMachine}
        isPaused={isPaused}
        togglePause={togglePause}
        refreshManual={refreshManual}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Main Content Area */}
      <main style={{
        flex: 1,
        maxWidth: '1680px',
        width: '100%',
        margin: '0 auto',
        padding: '2rem 2.5rem',
        boxSizing: 'border-box'
      }}>
        {activeTab === 'dashboard' && (
          <DashboardPage
            latest={latest}
            history={history}
            waiting={waiting}
            activeAlert={activeAlert}
            acknowledgeAlert={acknowledgeAlert}
            mqttConnected={mqttConnected}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === 'digital-twin' && (
          <DigitalTwinPage
            latest={latest}
            waiting={waiting}
          />
        )}

        {activeTab === 'diagnostics' && (
          <DiagnosticsPage
            latest={latest}
            waiting={waiting}
          />
        )}

        {activeTab === 'history' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <SensorTrendsChart history={history} />
            <TelemetryHistoryTable
              history={history}
              dbStats={dbStats}
              loading={historyLoading}
              onQueryDatabase={loadHistory}
              activeMachine={activeMachine}
            />
          </div>
        )}

        {activeTab === 'system' && (
          <SystemStatusPage
            statusMeta={statusMeta}
            dbStats={dbStats}
            mqttConnected={mqttConnected}
            backendConnected={backendConnected}
            historyLength={history.length}
          />
        )}
      </main>

      {/* Industrial Console Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-normal)',
        backgroundColor: 'var(--bg-secondary)',
        padding: '1.1rem 2.5rem',
        fontSize: '0.85rem',
        color: 'var(--text-muted)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.85rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>P_311 Industrial Fault Diagnosis System</span>
          <span>•</span>
          <span className="mono">Topic: factory/machine1/sensors</span>
          <span>•</span>
          <span className="mono">FAISS Vector Index (384-dim)</span>
        </div>
        <div>
          <span>Stratified Gradient Boosting Classifier • Threshold: 0.40</span>
        </div>
      </footer>
    </div>
  );
}
