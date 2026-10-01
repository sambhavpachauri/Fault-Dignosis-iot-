import { useState, useEffect, useRef, useCallback } from 'react';
import { subscribeToTelemetry, fetchLatestTelemetry, fetchTelemetryHistory, fetchSystemStatus, fetchDatabaseStats } from '../services/api';

export function useTelemetry() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [backendConnected, setBackendConnected] = useState(false);
  const [mqttConnected, setMqttConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [waiting, setWaiting] = useState(true);
  const [lastReceived, setLastReceived] = useState(null);
  const [activeAlert, setActiveAlert] = useState(null);
  const [alertAcknowledged, setAlertAcknowledged] = useState(false);
  const [activeMachine, setActiveMachine] = useState("Machine 1");
  const [statusMeta, setStatusMeta] = useState(null);
  const [dbStats, setDbStats] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  const isPausedRef = useRef(isPaused);
  isPausedRef.current = isPaused;

  // Poll system status & db stats periodically
  const checkStatus = useCallback(async () => {
    try {
      const [status, dbInfo] = await Promise.allSettled([
        fetchSystemStatus(),
        fetchDatabaseStats()
      ]);

      if (status.status === 'fulfilled') {
        setMqttConnected(status.value.mqtt_connected);
        setBackendConnected(true);
        setStatusMeta(status.value);
        if (status.value.last_data_received) {
          setLastReceived(status.value.last_data_received);
        }
      } else {
        setBackendConnected(false);
        setMqttConnected(false);
      }

      if (dbInfo.status === 'fulfilled') {
        setDbStats(dbInfo.value);
      }
    } catch (e) {
      setBackendConnected(false);
      setMqttConnected(false);
    }
  }, []);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, [checkStatus]);

  // Load historical telemetry from the database
  const loadHistory = useCallback(async (filters = {}) => {
    try {
      setHistoryLoading(true);
      const queryParams = {
        machine_id: filters.machine_id !== undefined ? filters.machine_id : activeMachine,
        limit: filters.limit || 100,
        severity: filters.severity || 'ALL',
        start_time: filters.start_time || null,
        end_time: filters.end_time || null
      };

      const records = await fetchTelemetryHistory(queryParams);
      if (Array.isArray(records)) {
        setHistory(records);
      }
    } catch (e) {
      console.warn("Failed to load telemetry history from database:", e);
    } finally {
      setHistoryLoading(false);
    }
  }, [activeMachine]);

  // Initial fetch and reload when machine changes
  useEffect(() => {
    loadHistory({ machine_id: activeMachine, limit: 100 });
  }, [activeMachine, loadHistory]);

  // Manual refresh of latest and database history
  const refreshManual = useCallback(async () => {
    try {
      const data = await fetchLatestTelemetry();
      if (data.waiting) {
        setWaiting(true);
      } else if (data.id) {
        setWaiting(false);
        setLatest(data);
        setLastReceived(data.timestamp);
      }
      await loadHistory();
      await checkStatus();
    } catch (e) {
      console.warn("Manual refresh failed", e);
    }
  }, [loadHistory, checkStatus]);

  useEffect(() => {
    refreshManual();
  }, [refreshManual]);

  // WebSocket Live Subscription
  useEffect(() => {
    const unsubscribe = subscribeToTelemetry(
      (message) => {
        if (message.type === 'waiting') {
          setWaiting(true);
          return;
        }

        if (message.type === 'telemetry' && message.data) {
          const record = message.data;
          setWaiting(false);
          setLastReceived(record.timestamp);

          // Check for critical / high alerts
          if (record.diagnosis?.severity === 'CRITICAL' || record.diagnosis?.severity === 'HIGH') {
            setActiveAlert({
              severity: record.diagnosis.severity,
              time: record.timestamp,
              issues: record.diagnosis.issues,
              recommendation: record.diagnosis.recommendation,
              probability: record.diagnosis.failure_probability_pct,
              machine_id: record.machine_id
            });
            // Reset acknowledge if severity is newly updated
            setAlertAcknowledged(false);
          }

          if (!isPausedRef.current) {
            setLatest(record);
            setHistory(prev => {
              // Avoid duplicate if same id exists
              if (prev.some(r => r.id === record.id)) return prev;
              return [record, ...prev].slice(0, 200);
            });
          }
        }
      },
      (status) => {
        setBackendConnected(status.connected);
      }
    );

    return () => unsubscribe();
  }, []);

  const togglePause = () => {
    setIsPaused(prev => !prev);
  };

  const acknowledgeAlert = () => {
    setAlertAcknowledged(true);
  };

  return {
    latest,
    history,
    backendConnected,
    mqttConnected,
    isPaused,
    waiting,
    lastReceived,
    activeAlert: alertAcknowledged ? null : activeAlert,
    isAlertAcknowledged: alertAcknowledged,
    activeMachine,
    setActiveMachine,
    statusMeta,
    dbStats,
    historyLoading,
    loadHistory,
    togglePause,
    acknowledgeAlert,
    refreshManual
  };
}
