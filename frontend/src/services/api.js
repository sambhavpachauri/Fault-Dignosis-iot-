const API_BASE = window.location.origin.includes('5173') 
  ? 'http://127.0.0.1:8000' 
  : window.location.origin;

export async function fetchLatestTelemetry() {
  const res = await fetch(`${API_BASE}/api/latest`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchSystemStatus() {
  const res = await fetch(`${API_BASE}/api/status`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchTelemetryHistory(limitOrOptions = 50, severity = 'ALL') {
  let machine_id = 'Machine 1';
  let limit = 50;
  let sev = severity;
  let start_time = null;
  let end_time = null;

  if (typeof limitOrOptions === 'object' && limitOrOptions !== null) {
    machine_id = limitOrOptions.machine_id ?? 'Machine 1';
    limit = limitOrOptions.limit ?? 50;
    sev = limitOrOptions.severity ?? 'ALL';
    start_time = limitOrOptions.start_time ?? null;
    end_time = limitOrOptions.end_time ?? null;
  } else {
    limit = limitOrOptions;
  }

  const params = new URLSearchParams();
  if (machine_id && machine_id !== 'ALL') params.append('machine_id', machine_id);
  if (limit) params.append('limit', limit);
  if (sev && sev !== 'ALL') params.append('severity', sev);
  if (start_time) params.append('start_time', start_time);
  if (end_time) params.append('end_time', end_time);
  
  const res = await fetch(`${API_BASE}/api/history?${params.toString()}`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchMachinesList() {
  const res = await fetch(`${API_BASE}/api/machines`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchDatabaseStats() {
  const res = await fetch(`${API_BASE}/api/database/stats`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchAllKnowledge() {
  const res = await fetch(`${API_BASE}/api/knowledge`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function searchKnowledge(query) {
  const res = await fetch(`${API_BASE}/api/knowledge/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export function subscribeToTelemetry(onTelemetry, onStatusChange) {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = window.location.origin.includes('5173') 
    ? '127.0.0.1:8000' 
    : window.location.host;
  
  const wsUrl = `${wsProtocol}//${wsHost}/ws/telemetry`;
  let socket = null;
  let reconnectTimeout = null;
  let isClosedManually = false;

  function connect() {
    try {
      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        onStatusChange({ connected: true, error: null });
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          onTelemetry(payload);
        } catch (e) {
          console.error("Failed to parse websocket telemetry message", e);
        }
      };

      socket.onerror = (err) => {
        onStatusChange({ connected: false, error: "WebSocket connection error" });
      };

      socket.onclose = () => {
        onStatusChange({ connected: false, error: "Connection closed" });
        if (!isClosedManually) {
          reconnectTimeout = setTimeout(connect, 3000);
        }
      };
    } catch (e) {
      onStatusChange({ connected: false, error: e.message });
      if (!isClosedManually) {
        reconnectTimeout = setTimeout(connect, 3000);
      }
    }
  }

  connect();

  return () => {
    isClosedManually = true;
    if (reconnectTimeout) clearTimeout(reconnectTimeout);
    if (socket) socket.close();
  };
}
