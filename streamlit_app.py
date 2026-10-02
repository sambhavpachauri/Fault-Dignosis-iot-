"""
P_311 Industrial IoT Fault Diagnosis System — Streamlit SCADA Console
=============================================================================
A high-fidelity industrial SCADA console visually aligned with the React SCADA UI.
Consumes existing FastAPI REST APIs without modifying or duplicating backend logic.

Design Tokens & Aesthetic:
  - Background: #151719 (Primary), #1C1F21 (Secondary), #222628 (Panels)
  - Borders: #3A3F42 (Normal), #50565A (Strong)
  - Typography: Inter & JetBrains Mono
  - Status Palette: #6FA36F (Normal), #C39A4A (Medium), #C8753D (High), #B65353 (Critical)
  - Semi-Circle Radial SVG Failure Risk Gauge & 5 Industrial Sensor Metric Cards
=============================================================================
"""

import os
import math
import time
import textwrap
from typing import Dict, Any, List, Optional

import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
DEFAULT_MACHINE = "Machine 1"
ALARM_THRESHOLD = 0.40

# -----------------------------------------------------------------------------
# Streamlit Page Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="P_311 | SCADA Fault Diagnosis Workstation",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Industrial SCADA Design System (Matching React frontend/src/index.css)
# -----------------------------------------------------------------------------
SCADA_CSS = textwrap.dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
  --bg-primary: #151719;
  --bg-secondary: #1C1F21;
  --bg-panel: #222628;
  --bg-elevated: #292D30;
  --border-normal: #3A3F42;
  --border-strong: #50565A;
  --text-primary: #E6E8E9;
  --text-secondary: #A7ADB1;
  --text-muted: #737A7F;
  --accent: #5B7C99;
  --accent-subtle: rgba(91, 124, 153, 0.18);
  --status-normal: #6FA36F;
  --status-normal-bg: rgba(111, 163, 111, 0.12);
  --status-medium: #C39A4A;
  --status-medium-bg: rgba(195, 154, 74, 0.12);
  --status-high: #C8753D;
  --status-high-bg: rgba(200, 117, 61, 0.12);
  --status-critical: #B65353;
  --status-critical-bg: rgba(182, 83, 83, 0.15);
}

/* Global Reset for Industrial Look */
.stApp {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.block-container {
  padding-top: 1rem;
  padding-bottom: 2rem;
  padding-left: 2rem;
  padding-right: 2rem;
}

.mono {
  font-family: 'JetBrains Mono', monospace;
}

/* Header Banner */
.scada-top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.4rem;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-normal);
  border-radius: 4px;
  margin-bottom: 1.25rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.brand-badge {
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-normal);
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.scada-main-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}

.scada-sub-title {
  font-size: 0.84rem;
  color: var(--text-muted);
  margin: 0.15rem 0 0 0;
}

/* Technical Status Pill Badges */
.badge-status {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.22rem 0.65rem;
  font-size: 0.76rem;
  font-weight: 600;
  border-radius: 3px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.badge-normal {
  color: var(--status-normal);
  background-color: var(--status-normal-bg);
  border: 1px solid var(--status-normal);
}

.badge-medium {
  color: var(--status-medium);
  background-color: var(--status-medium-bg);
  border: 1px solid var(--status-medium);
}

.badge-high {
  color: var(--status-high);
  background-color: var(--status-high-bg);
  border: 1px solid var(--status-high);
}

.badge-critical {
  color: var(--status-critical);
  background-color: var(--status-critical-bg);
  border: 1px solid var(--status-critical);
}

/* Technical Status Dots */
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.status-dot-normal { background-color: var(--status-normal); }
.status-dot-critical { background-color: var(--status-critical); }
.status-dot-warn { background-color: var(--status-medium); }

/* Industrial Card Panel */
.card-panel {
  background-color: var(--bg-panel);
  border: 1px solid var(--border-normal);
  border-radius: 4px;
  padding: 1.25rem;
  height: 100%;
}

.card-panel-elevated {
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-normal);
  border-radius: 4px;
  padding: 1.25rem;
}

/* Alert Banner */
.alert-box {
  padding: 1rem 1.25rem;
  border-radius: 4px;
  margin-bottom: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.alert-normal {
  background-color: var(--status-normal-bg);
  border-left: 5px solid var(--status-normal);
  border-top: 1px solid var(--status-normal-bg);
  border-right: 1px solid var(--status-normal-bg);
  border-bottom: 1px solid var(--status-normal-bg);
}

.alert-medium {
  background-color: var(--status-medium-bg);
  border-left: 5px solid var(--status-medium);
  border-top: 1px solid var(--status-medium-bg);
  border-right: 1px solid var(--status-medium-bg);
  border-bottom: 1px solid var(--status-medium-bg);
}

.alert-high {
  background-color: var(--status-high-bg);
  border-left: 5px solid var(--status-high);
  border-top: 1px solid var(--status-high-bg);
  border-right: 1px solid var(--status-high-bg);
  border-bottom: 1px solid var(--status-high-bg);
}

.alert-critical {
  background-color: var(--status-critical-bg);
  border-left: 5px solid var(--status-critical);
  border-top: 1px solid var(--status-critical-bg);
  border-right: 1px solid var(--status-critical-bg);
  border-bottom: 1px solid var(--status-critical-bg);
}

/* Range Bar Track */
.range-track {
  width: 100%;
  height: 4px;
  background-color: var(--bg-secondary);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 0.5rem;
}
.range-fill {
  height: 100%;
  border-radius: 2px;
}
</style>
""")

st.markdown(SCADA_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# REST Client Helpers
# -----------------------------------------------------------------------------
def fetch_api(endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: float = 3.0) -> Optional[Any]:
    url = f"{BACKEND_URL}{endpoint}"
    try:
        r = requests.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

def post_api(endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: float = 4.0) -> Optional[Any]:
    url = f"{BACKEND_URL}{endpoint}"
    try:
        r = requests.post(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

def render_scada_html(html_str: str):
    """
    Renders custom HTML in Streamlit safely.
    Strips all leading whitespace from every line and removes comments to ensure
    CommonMark never confuses indentation with Markdown indented code blocks (<pre><code>).
    """
    lines = [line.strip() for line in html_str.strip().splitlines()]
    clean = "\n".join(l for l in lines if l and not l.startswith("<!--"))
    st.markdown(clean, unsafe_allow_html=True)
# -----------------------------------------------------------------------------
def generate_radial_gauge_svg(prob_val: float, threshold: float = 0.40) -> str:
    prob_percent = max(0.0, min(100.0, prob_val * 100))
    threshold_percent = threshold * 100

    radius = 86
    stroke_width = 10
    total_length = math.pi * radius  # approx 270.18

    # Status color selection
    if prob_percent >= 75:
        status_color = "#B65353"  # Critical
    elif prob_percent >= threshold_percent:
        status_color = "#C8753D"  # High
    elif prob_percent >= 20:
        status_color = "#C39A4A"  # Medium
    else:
        status_color = "#6FA36F"  # Normal

    active_length = (prob_percent / 100.0) * total_length
    dash_offset = max(0.0, total_length - active_length)

    # Needle angle (180deg on left to 0deg on right)
    angle_deg = 180.0 - (prob_percent / 100.0) * 180.0
    rad = math.radians(angle_deg)
    nx = 110 + 70 * math.cos(rad)
    ny = 110 - 70 * math.sin(rad)

    # Threshold marker line coordinates
    trad = math.radians(180.0 - (threshold_percent / 100.0) * 180.0)
    tx1 = 110 + 72 * math.cos(trad)
    ty1 = 110 - 72 * math.sin(trad)
    tx2 = 110 + 98 * math.cos(trad)
    ty2 = 110 - 98 * math.sin(trad)

    svg = f"""<svg width="220" height="125" viewBox="0 0 220 125" style="display:block; margin:0 auto;">
  <path d="M 24 110 A 86 86 0 0 1 196 110" fill="none" stroke="#292D30" stroke-width="{stroke_width}" stroke-linecap="square"/>
  <path d="M 24 110 A 86 86 0 0 1 196 110" fill="none" stroke="{status_color}" stroke-width="{stroke_width}" stroke-dasharray="{total_length:.2f}" stroke-dashoffset="{dash_offset:.2f}" stroke-linecap="square"/>
  <line x1="{tx1:.2f}" y1="{ty1:.2f}" x2="{tx2:.2f}" y2="{ty2:.2f}" stroke="#C39A4A" stroke-width="2.5"/>
  <circle cx="110" cy="110" r="5" fill="#E6E8E9"/>
  <line x1="110" y1="110" x2="{nx:.2f}" y2="{ny:.2f}" stroke="#E6E8E9" stroke-width="2.5" stroke-linecap="round"/>
</svg>"""
    return svg, status_color, prob_percent

# -----------------------------------------------------------------------------
# Helper: Sensor Sparkline SVG (Identical to React component)
# -----------------------------------------------------------------------------
def generate_sparkline_svg(history_values: List[float], color: str = "#5B7C99", width: int = 80, height: int = 24) -> str:
    if not history_values or len(history_values) < 2:
        return f'<div style="width:{width}px; height:{height}px; display:flex; align-items:center; justify-content:center; color:#737A7F; font-size:0.65rem;">--</div>'
    
    clean_vals = [float(v) for v in history_values[-15:] if v is not None]
    if len(clean_vals) < 2:
        return f'<div style="width:{width}px; height:{height}px; display:flex; align-items:center; justify-content:center; color:#737A7F; font-size:0.65rem;">--</div>'

    min_v = min(clean_vals)
    max_v = max(clean_vals)
    rng = max_v - min_v or 1.0

    points = []
    n = len(clean_vals)
    for i, v in enumerate(clean_vals):
        x = (i / (n - 1)) * width
        y = height - ((v - min_v) / rng) * (height - 4) - 2
        points.append(f"{x:.1f},{y:.1f}")

    poly_pts = " ".join(points)
    return f"""<svg width="{width}" height="{height}" style="overflow:visible;">
  <polyline fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="square" stroke-linejoin="round" points="{poly_pts}"/>
</svg>"""

# -----------------------------------------------------------------------------
# Sidebar: SCADA Controls & Backend Targeting
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ SCADA Station Control")

    backend_input = st.text_input(
        "FastAPI Service URL",
        value=BACKEND_URL,
        help="Target endpoint of the core FastAPI pipeline"
    )
    if backend_input != BACKEND_URL:
        BACKEND_URL = backend_input.rstrip("/")

    sys_status = fetch_api("/api/status", timeout=2.0)
    db_stats = fetch_api("/api/database/stats", timeout=2.0)

    st.markdown("---")
    st.markdown("#### 📡 Connectivity Matrix")
    c1, c2 = st.columns(2)
    with c1:
        if sys_status and sys_status.get("backend_connected"):
            st.markdown('<span class="badge-status badge-normal"><span class="status-dot status-dot-normal"></span> API 200</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-status badge-critical"><span class="status-dot status-dot-critical"></span> API OFF</span>', unsafe_allow_html=True)
    with c2:
        if sys_status and sys_status.get("mqtt_connected"):
            st.markdown('<span class="badge-status badge-normal"><span class="status-dot status-dot-normal"></span> MQTT OK</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-status badge-critical"><span class="status-dot status-dot-critical"></span> MQTT OFF</span>', unsafe_allow_html=True)

    if db_stats:
        st.markdown(f"**Database:** `{db_stats.get('storage_engine', 'PostgreSQL')}`")
        st.markdown(f"**Persisted Telemetry:** `{db_stats.get('total_persisted_records', 0):,}`")
    elif sys_status:
        st.markdown(f"**Database Records:** `{sys_status.get('database_records', 0):,}`")

    st.markdown("---")
    st.markdown("#### 🔄 Polling Cycle")
    auto_refresh = st.checkbox("Live Polling Active", value=True)
    refresh_rate = st.slider("Cycle Rate (Seconds)", min_value=2, max_value=10, value=3, step=1)
    if st.button("Poll Immediate", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🧪 Hardware Simulation")
    st.caption("Publish calibrated AI4I scenario directly to MQTT broker:")
    scenario_choice = st.selectbox(
        "Fault Scenario",
        ["NORMAL", "HIGH_TEMP", "HIGH_TORQUE", "HIGH_WEAR", "CRITICAL"],
        index=0
    )
    if st.button("Inject into Broker", use_container_width=True):
        res = post_api("/api/simulate", params={"scenario": scenario_choice, "machine_id": DEFAULT_MACHINE})
        if res and res.get("published"):
            st.toast(f"Published scenario '{scenario_choice}' to MQTT", icon="📡")
            time.sleep(0.4)
            st.rerun()
        else:
            st.toast("Simulation failed: Backend unreachable", icon="⚠️")

# -----------------------------------------------------------------------------
# Dynamic Machine Fetching & Data Ingestion
# -----------------------------------------------------------------------------
machine_list = fetch_api("/api/machines", timeout=2.0) or [DEFAULT_MACHINE]

# Top Technical Header Bar (Matching React SCADA layout)
top_h_col1, top_h_col2 = st.columns([3, 1])
with top_h_col1:
    st.markdown(
        """
        <div class="scada-top-header">
            <div style="display:flex; align-items:center; gap:0.9rem;">
                <div class="brand-badge">P_311</div>
                <div>
                    <h1 class="scada-main-title">Knowledge-Driven IoT Fault Diagnosis Assistant</h1>
                    <p class="scada-sub-title">Industrial Supervisory & Predictive Maintenance SCADA Console</p>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:0.6rem;">
                <span class="badge-status badge-normal"><span class="status-dot status-dot-normal"></span> MQTT:1883</span>
                <span class="badge-status badge-normal"><span class="status-dot status-dot-normal"></span> REST:8000</span>
                <span class="badge-status badge-normal"><span class="status-dot status-dot-normal"></span> POSTGRES 16</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with top_h_col2:
    selected_machine = st.selectbox(
        "Monitored Asset",
        options=machine_list,
        index=0,
        label_visibility="collapsed"
    )

# Retrieve Machine Telemetry & Historical Window
latest_data = fetch_api(f"/api/latest/{selected_machine}", timeout=3.0)
hist_records = fetch_api(f"/api/history/{selected_machine}", params={"limit": 50}, timeout=3.0) or []

# Check Connection State
if latest_data is None:
    st.markdown(
        f"""
        <div class="alert-box alert-critical">
            <div>
                <strong style="color:var(--status-critical);">⚠️ FastAPI Backend Unreachable at {BACKEND_URL}</strong>
                <p style="margin:0.25rem 0 0 0; color:var(--text-secondary); font-size:0.85rem;">
                    Ensure the core FastAPI backend is running via <code>uvicorn backend.main:app --port 8000</code> or check the sidebar URL.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()
    st.stop()

if latest_data.get("waiting"):
    st.markdown(
        f"""
        <div class="alert-box alert-normal">
            <div>
                <strong style="color:var(--status-normal);">⏳ Telemetry Pipeline Initialized</strong>
                <p style="margin:0.25rem 0 0 0; color:var(--text-secondary); font-size:0.85rem;">
                    {latest_data.get('message', 'Awaiting first telemetry frame from sensor simulator...')}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()
    st.stop()

# Parse Core Telemetry Attributes
sensors = latest_data.get("sensors", {})
diagnosis = latest_data.get("diagnosis", {})
evaluations = diagnosis.get("sensor_evaluations", {})
rag_topics = diagnosis.get("rag_knowledge", [])
issues = diagnosis.get("issues", [])
severity = diagnosis.get("severity", "LOW")
status_label = diagnosis.get("status", "NORMAL")
prob_val = float(diagnosis.get("failure_probability", 0.0))
timestamp_str = latest_data.get("timestamp", "N/A")

# Precompute historical sparklines
hist_chrono = list(reversed(hist_records))
air_hist = [h.get("sensors", {}).get("air_temperature") for h in hist_chrono]
proc_hist = [h.get("sensors", {}).get("process_temperature") for h in hist_chrono]
speed_hist = [h.get("sensors", {}).get("rotational_speed") for h in hist_chrono]
torque_hist = [h.get("sensors", {}).get("torque") for h in hist_chrono]
wear_hist = [h.get("sensors", {}).get("tool_wear") for h in hist_chrono]

# -----------------------------------------------------------------------------
# Main Navigation Tabs (Matching React SCADA layout)
# -----------------------------------------------------------------------------
tab_dash, tab_diag, tab_trends, tab_history, tab_system = st.tabs([
    "DASHBOARD",
    "DIAGNOSTICS & SOP",
    "SENSOR TRENDS",
    "HISTORICAL RECORDS",
    "SYSTEM ARCHITECTURE"
])

# =============================================================================
# TAB 1: DASHBOARD
# =============================================================================
with tab_dash:
    # 1. Alert Banner matching AlertBanner.jsx
    alert_class = "alert-normal"
    badge_cls = "badge-normal"
    if severity == "CRITICAL":
        alert_class = "alert-critical"
        badge_cls = "badge-critical"
    elif severity == "HIGH":
        alert_class = "alert-high"
        badge_cls = "badge-high"
    elif severity == "MEDIUM":
        alert_class = "alert-medium"
        badge_cls = "badge-medium"

    rec_action = diagnosis.get("recommendation", "System operating within nominal factory thresholds.")

    st.markdown(
        f"""
        <div class="alert-box {alert_class}">
            <div style="display:flex; align-items:center; justify-content:space-between; width:100%; flex-wrap:wrap; gap:0.5rem;">
                <div>
                    <span style="font-size:1.05rem; font-weight:700; color:var(--text-primary); letter-spacing:0.02em;">
                        {selected_machine} — {status_label}
                    </span>
                    <div style="font-size:0.85rem; color:var(--text-secondary); margin-top:0.25rem;">
                        {rec_action}
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <span style="font-size:0.78rem; color:var(--text-muted); font-family:'JetBrains Mono', monospace;">
                        {timestamp_str}
                    </span>
                    <span class="badge-status {badge_cls}">{severity}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Main Dashboard Split: Failure Risk Gauge + Machine Status Card
    g_col1, g_col2 = st.columns([1, 1])

    with g_col1:
        svg_gauge, status_color, prob_percent = generate_radial_gauge_svg(prob_val, threshold=ALARM_THRESHOLD)
        st.markdown(
            f"""
            <div class="card-panel" style="display:flex; flex-direction:column; justify-content:space-between; min-height:265px;">
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <span style="font-size:0.85rem; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.04em; font-weight:600;">
                        PREDICTIVE FAILURE RISK
                    </span>
                    <span style="font-size:0.82rem; color:var(--status-medium); font-weight:600;">
                        Cutoff: {ALARM_THRESHOLD * 100:.0f}%
                    </span>
                </div>
                <div style="position:relative; width:220px; height:125px; margin:0.85rem auto 0 auto;">
                    {svg_gauge}
                    <div style="position:absolute; bottom:0; left:0; right:0; text-align:center;">
                        <div class="mono" style="font-size:2.3rem; font-weight:700; color:{status_color}; line-height:1;">
                            {prob_percent:.2f}%
                        </div>
                        <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.25rem;">
                            Gradient Boosting Model
                        </div>
                    </div>
                </div>
                <div style="margin-top:0.95rem; padding:0.55rem 0.95rem; border-radius:4px; background-color:var(--bg-elevated); border:1px solid var(--border-normal); display:flex; align-items:center; justify-content:space-between; font-size:0.85rem;">
                    <span style="color:var(--text-secondary);">Evaluated Status:</span>
                    <strong style="color:{status_color}; font-size:0.9rem;">{status_label}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with g_col2:
        is_all_clear = not issues or len(issues) == 0 or (len(issues) == 1 and "No major abnormal" in issues[0])
        real_issues = [i for i in issues if "No major abnormal" not in i]

        if is_all_clear:
            anomalies_html = '<div style="font-size:0.85rem; color:var(--status-normal); padding:0.45rem 0.65rem; border-radius:4px; background-color:var(--status-normal-bg); border:1px solid var(--status-normal);">• ✅ No major abnormal sensor condition detected</div>'
            anomaly_count = 0
        else:
            anomaly_count = len(real_issues)
            issue_lines = [f'<div style="font-size:0.85rem; color:#fca5a5; margin-bottom:0.3rem;">• ⚠️ <strong>{iss}</strong></div>' for iss in real_issues]
            anomalies_html = "".join(issue_lines)

        asset_card_html = f"""
        <div class="card-panel" style="display:flex; flex-direction:column; justify-content:space-between; min-height:265px;">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <span style="font-size:0.85rem; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.04em; font-weight:600;">
                    ASSET STATUS & DIAGNOSTICS
                </span>
                <span class="badge-status {badge_cls}">{severity}</span>
            </div>
            <div style="margin: 0.75rem 0;">
                <div style="font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; margin-bottom:0.4rem;">
                    Detected Operating Anomalies ({anomaly_count})
                </div>
                <div>
                    {anomalies_html}
                </div>
            </div>
            <div style="padding:0.6rem 0.85rem; border-radius:4px; background-color:var(--bg-elevated); border:1px solid var(--border-normal); font-size:0.82rem; color:var(--text-secondary);">
                <strong style="color:var(--text-primary);">Recommendation:</strong> {rec_action}
            </div>
        </div>
        """
        st.markdown(asset_card_html, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 3. 5 Industrial Sensor Monitoring Cards (Matching SensorMonitoring.jsx)
    st.markdown(
        """
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.65rem;">
            <span style="font-size:0.92rem; font-weight:600; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.05em;">
                Live Sensor Telemetry
            </span>
            <span style="font-size:0.8rem; color:var(--text-muted);">
                Physical Operating Limits (diagnosis.py)
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    s1, s2, s3, s4, s5 = st.columns(5)

    def render_scada_sensor(col, title, val, unit, min_v, max_v, limit_txt, key, hist_list):
        ev = evaluations.get(key, {})
        is_norm = ev.get("is_normal", True)
        st_label = ev.get("status_label", "NORMAL")

        if st_label in ["ELEVATED", "INCREASING", "LOW"]:
            s_badge = "badge-medium"
            s_color = "var(--status-medium)"
        elif st_label == "HIGH":
            s_badge = "badge-high"
            s_color = "var(--status-high)"
        elif st_label == "CRITICAL":
            s_badge = "badge-critical"
            s_color = "var(--status-critical)"
        else:
            s_badge = "badge-normal"
            s_color = "var(--status-normal)"

        # Range bar percentage
        clamped = max(min_v, min(max_v, float(val or min_v)))
        pct = max(0.0, min(100.0, ((clamped - min_v) / (max_v - min_v)) * 100))
        fill_color = "var(--border-strong)" if is_norm else s_color

        spark_svg = generate_sparkline_svg(hist_list, color="var(--accent)" if is_norm else s_color)

        formatted_val = f"{val:,.1f}" if isinstance(val, (int, float)) and key in ["air_temperature", "process_temperature", "torque"] else str(val)

        with col:
            st.markdown(
                f"""
                <div class="card-panel" style="padding:1.15rem 1rem; display:flex; flex-direction:column; justify-content:space-between; min-height:175px;">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.4rem;">
                        <span style="font-size:0.78rem; color:var(--text-secondary); font-weight:600; letter-spacing:0.03em;">
                            {title}
                        </span>
                        <span class="badge-status {s_badge}" style="font-size:0.72rem; padding:0.2rem 0.5rem;">
                            {st_label}
                        </span>
                    </div>
                    <div style="display:flex; align-items:baseline; gap:0.4rem; margin:0.3rem 0;">
                        <span class="mono" style="font-size:2.25rem; font-weight:700; color:var(--text-primary); line-height:1;">
                            {formatted_val}
                        </span>
                        <span style="font-size:0.9rem; color:var(--text-muted); font-weight:500;">
                            {unit}
                        </span>
                    </div>
                    <div>
                        <div style="font-size:0.75rem; color:{s_color if not is_norm else 'var(--text-muted)'}; font-weight:500;">
                            {limit_txt}
                        </div>
                        <div class="range-track">
                            <div class="range-fill" style="width:{pct:.1f}%; background-color:{fill_color};"></div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; justify-content:space-between; border-top:1px solid var(--border-normal); padding-top:0.45rem; margin-top:0.55rem;">
                        <span style="font-size:0.72rem; color:var(--text-muted);">Trend</span>
                        {spark_svg}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    render_scada_sensor(s1, "AIR TEMPERATURE", sensors.get("air_temperature", 0.0), "K", 290, 310, "Limit: < 301.0 K", "air_temperature", air_hist)
    render_scada_sensor(s2, "PROCESS TEMP", sensors.get("process_temperature", 0.0), "K", 300, 320, "Limit: < 312.0 K", "process_temperature", proc_hist)
    render_scada_sensor(s3, "ROTATIONAL SPEED", sensors.get("rotational_speed", 0), "RPM", 1000, 2000, "Band: 1300 - 1650 RPM", "rotational_speed", speed_hist)
    render_scada_sensor(s4, "SHAFT TORQUE", sensors.get("torque", 0.0), "Nm", 20, 80, "Limit: < 55.0 Nm", "torque", torque_hist)
    render_scada_sensor(s5, "TOOL WEAR", sensors.get("tool_wear", 0), "min", 0, 250, "Limit: < 100 min", "tool_wear", wear_hist)

# =============================================================================
# TAB 2: DIAGNOSTICS & SOP
# =============================================================================
with tab_diag:
    st.markdown("### 🛠️ Diagnostic Evaluation & SOP Procedures")

    if rag_topics:
        st.markdown(f"**Matched Knowledge Topics ({len(rag_topics)})** directly linked to current machine state:")
        for topic in rag_topics:
            with st.expander(f"📘 SOP Procedure: {topic.get('topic', 'Standard Maintenance')}", expanded=True):
                st.markdown(f"**Condition:** {topic.get('condition')}")
                dc1, dc2 = st.columns(2)
                with dc1:
                    st.markdown("**Inspection Steps:**")
                    for stp in topic.get("inspection_steps", []):
                        st.markdown(f"- {stp}")
                with dc2:
                    st.markdown("**Recommended Corrective Actions:**")
                    for act in topic.get("recommended_actions", []):
                        st.markdown(f"- {act}")
    else:
        st.info("No active fault conditions requiring specialized SOP intervention.")

    st.markdown("---")
    st.markdown("#### 🔍 Semantic Maintenance Knowledge Search (FAISS Dense RAG)")
    q = st.text_input("Query SOP database (Sentence Transformers)", placeholder="e.g. tool replacement interval, cooling system overheating...")
    if q and len(q.strip()) >= 2:
        search_res = fetch_api("/api/knowledge/search", params={"q": q.strip()}, timeout=4.0)
        if search_res:
            for item in search_res:
                with st.expander(f"📖 {item.get('topic')}", expanded=True):
                    st.markdown(f"**Condition:** {item.get('condition')}")
                    sc1, sc2 = st.columns(2)
                    with sc1:
                        st.markdown("**Inspection Steps:**")
                        for s in item.get("inspection_steps", []):
                            st.markdown(f"- {s}")
                    with sc2:
                        st.markdown("**Recommended Actions:**")
                        for a in item.get("recommended_actions", []):
                            st.markdown(f"- {a}")
        else:
            st.warning("No matching maintenance procedures found for this query.")

# =============================================================================
# TAB 3: SENSOR TRENDS
# =============================================================================
with tab_trends:
    st.markdown(f"### 📈 Real-Time Multi-Metric Trends — {selected_machine}")

    if hist_chrono:
        df_chart = pd.DataFrame([
            {
                "Time": h.get("timestamp"),
                "Air Temp (K)": h.get("sensors", {}).get("air_temperature"),
                "Process Temp (K)": h.get("sensors", {}).get("process_temperature"),
                "Speed (RPM)": h.get("sensors", {}).get("rotational_speed"),
                "Torque (Nm)": h.get("sensors", {}).get("torque"),
                "Tool Wear (min)": h.get("sensors", {}).get("tool_wear"),
                "Failure Risk": h.get("diagnosis", {}).get("failure_probability")
            }
            for h in hist_chrono
        ])

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Thermal Profiles (Air vs Process Temperature)",
                "Rotational Speed Dynamics (RPM)",
                "Shaft Torque Loading (Nm)",
                "Cumulative Tool Wear (min)"
            ),
            vertical_spacing=0.16,
            horizontal_spacing=0.08
        )

        fig.add_trace(go.Scatter(x=df_chart["Time"], y=df_chart["Air Temp (K)"], name="Air Temp (K)", line=dict(color="#5B7C99", width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_chart["Time"], y=df_chart["Process Temp (K)"], name="Process Temp (K)", line=dict(color="#C8753D", width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_chart["Time"], y=df_chart["Speed (RPM)"], name="Speed (RPM)", line=dict(color="#6FA36F", width=2)), row=1, col=2)
        fig.add_trace(go.Scatter(x=df_chart["Time"], y=df_chart["Torque (Nm)"], name="Torque (Nm)", line=dict(color="#C39A4A", width=2)), row=2, col=1)
        fig.add_trace(go.Scatter(x=df_chart["Time"], y=df_chart["Tool Wear (min)"], name="Tool Wear (min)", line=dict(color="#B65353", width=2)), row=2, col=2)

        fig.update_layout(
            height=540,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="#222628",
            plot_bgcolor="#151719",
            font=dict(color="#A7ADB1", size=11, family="Inter"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_xaxes(showgrid=True, gridcolor="#3A3F42")
        fig.update_yaxes(showgrid=True, gridcolor="#3A3F42")

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Gathering historical records from PostgreSQL...")

# =============================================================================
# TAB 4: HISTORICAL RECORDS
# =============================================================================
with tab_history:
    st.markdown(f"### 📋 Telemetry & Diagnostic Event Logs — {selected_machine}")

    fc1, fc2 = st.columns([1, 3])
    with fc1:
        f_sev = st.selectbox("Filter Severity", ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"])

    records_list = fetch_api(f"/api/history/{selected_machine}", params={"limit": 100}, timeout=4.0) or []
    if records_list:
        table_rows = []
        for r in records_list:
            s = r.get("sensors", {})
            d = r.get("diagnosis", {})
            table_rows.append({
                "Frame ID": r.get("id"),
                "Timestamp": r.get("timestamp"),
                "Air Temp": s.get("air_temperature"),
                "Process Temp": s.get("process_temperature"),
                "Speed": s.get("rotational_speed"),
                "Torque": s.get("torque"),
                "Tool Wear": s.get("tool_wear"),
                "Failure Risk": d.get("failure_probability"),
                "Severity": d.get("severity"),
                "Status": d.get("status")
            })
        df_tbl = pd.DataFrame(table_rows)
        if f_sev != "ALL":
            df_tbl = df_tbl[df_tbl["Severity"] == f_sev]

        st.dataframe(
            df_tbl,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Failure Risk": st.column_config.ProgressColumn(
                    "Failure Risk",
                    format="%.2f",
                    min_value=0.0,
                    max_value=1.0
                )
            }
        )
    else:
        st.info("No records in database.")

# =============================================================================
# TAB 5: SYSTEM ARCHITECTURE
# =============================================================================
with tab_system:
    st.markdown("### 🗄️ System Architecture & Database Diagnostics")
    ic1, ic2 = st.columns(2)
    total_db_records = f"{db_stats.get('total_persisted_records', 0):,}" if db_stats else "0"
    storage_engine_name = db_stats.get('storage_engine', 'PostgreSQL') if db_stats else 'PostgreSQL 16'
    total_ingested_frames = f"{sys_status.get('total_readings_received', 0):,}" if sys_status else "0"
    ring_buffer_size = sys_status.get('buffer_count', 0) if sys_status else 0

    with ic1:
        st.markdown(
            f"""
            <div class="card-panel">
                <h4 style="margin-top:0; color:var(--text-primary);">PostgreSQL 16 Persistence</h4>
                <p style="color:var(--text-secondary); font-size:0.88rem;">
                    <strong>Storage Engine:</strong> {storage_engine_name}<br>
                    <strong>Persisted Records:</strong> {total_db_records}<br>
                    <strong>Database Host:</strong> 127.0.0.1:5432 (Docker)<br>
                    <strong>Schema Tables:</strong> <code>telemetry_records</code>, <code>diagnosis_logs</code>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with ic2:
        st.markdown(
            f"""
            <div class="card-panel">
                <h4 style="margin-top:0; color:var(--text-primary);">MQTT & Messaging Pipeline</h4>
                <p style="color:var(--text-secondary); font-size:0.88rem;">
                    <strong>Broker Engine:</strong> Eclipse Mosquitto (Port 1883)<br>
                    <strong>MQTT Topic:</strong> <code>factory/machine1/sensors</code><br>
                    <strong>Ingested Frames:</strong> {total_ingested_frames}<br>
                    <strong>Ring Buffer:</strong> {ring_buffer_size} frames
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🔄 End-to-End Component Pipeline")

    pipeline_card_html = """
    <div class="card-panel" style="padding:1.4rem; overflow-x:auto;">
        <div style="display:flex; align-items:center; justify-content:space-between; gap:0.9rem; min-width:860px;">
            <div style="flex:1; background-color:var(--bg-elevated); border:1px solid var(--border-normal); border-radius:4px; padding:1rem 0.85rem; text-align:center;">
                <div style="font-size:0.72rem; color:var(--text-muted); text-transform:uppercase; font-weight:600; letter-spacing:0.04em;">Telemetry Source</div>
                <div style="font-size:0.95rem; font-weight:700; color:var(--text-primary); margin:0.35rem 0;">IoT Simulator</div>
                <div class="mono" style="font-size:0.75rem; color:var(--accent);">ai4i_machine_simulator.py</div>
                <div style="margin-top:0.5rem;"><span class="badge-status badge-normal" style="font-size:0.68rem;">5 Sensor Feeds</span></div>
            </div>

            <div style="color:var(--text-muted); font-size:1.15rem; font-weight:bold; display:flex; flex-direction:column; align-items:center; flex-shrink:0;">
                <span class="mono" style="font-size:0.68rem; color:var(--text-muted); margin-bottom:0.15rem;">MQTT</span>
                <span style="color:var(--accent);">➔</span>
            </div>

            <div style="flex:1; background-color:var(--bg-elevated); border:1px solid var(--border-normal); border-radius:4px; padding:1rem 0.85rem; text-align:center;">
                <div style="font-size:0.72rem; color:var(--text-muted); text-transform:uppercase; font-weight:600; letter-spacing:0.04em;">Broker Hub</div>
                <div style="font-size:0.95rem; font-weight:700; color:var(--text-primary); margin:0.35rem 0;">Eclipse Mosquitto</div>
                <div class="mono" style="font-size:0.75rem; color:var(--accent);">Port 1883</div>
                <div style="margin-top:0.5rem;"><span class="badge-status badge-normal" style="font-size:0.68rem;">QoS 0 Stream</span></div>
            </div>

            <div style="color:var(--text-muted); font-size:1.15rem; font-weight:bold; display:flex; flex-direction:column; align-items:center; flex-shrink:0;">
                <span class="mono" style="font-size:0.68rem; color:var(--text-muted); margin-bottom:0.15rem;">Ingest</span>
                <span style="color:var(--accent);">➔</span>
            </div>

            <div style="flex:1.4; background-color:var(--bg-elevated); border:1px solid var(--accent); border-radius:4px; padding:1rem 0.95rem; text-align:center;">
                <div style="font-size:0.72rem; color:var(--accent); text-transform:uppercase; font-weight:700; letter-spacing:0.04em;">Core Engine</div>
                <div style="font-size:1.05rem; font-weight:700; color:var(--text-primary); margin:0.35rem 0;">FastAPI Backend</div>
                <div class="mono" style="font-size:0.75rem; color:var(--text-muted);">Port 8000 • REST & WebSocket</div>
                <div style="display:flex; justify-content:center; gap:0.35rem; margin-top:0.55rem; flex-wrap:wrap;">
                    <span class="badge-status badge-medium" style="font-size:0.65rem;">Gradient Boosting</span>
                    <span class="badge-status badge-medium" style="font-size:0.65rem;">FAISS RAG</span>
                    <span class="badge-status badge-normal" style="font-size:0.65rem;">PostgreSQL 16</span>
                </div>
            </div>

            <div style="color:var(--text-muted); font-size:1.15rem; font-weight:bold; display:flex; flex-direction:column; align-items:center; flex-shrink:0;">
                <span class="mono" style="font-size:0.68rem; color:var(--text-muted); margin-bottom:0.15rem;">REST/WS</span>
                <span style="color:var(--accent);">➔</span>
            </div>

            <div style="flex:1.3; display:flex; flex-direction:column; gap:0.55rem;">
                <div style="background-color:var(--bg-elevated); border:1px solid var(--border-strong); border-radius:4px; padding:0.65rem 0.85rem; text-align:left;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.85rem; font-weight:700; color:var(--text-primary);">React SCADA UI</span>
                        <span class="badge-status badge-normal" style="font-size:0.65rem;">Port 5173</span>
                    </div>
                    <div style="font-size:0.72rem; color:var(--text-muted); margin-top:0.25rem;">Primary Operator Station • Digital Twin • WebSocket</div>
                </div>
                <div style="background-color:var(--bg-elevated); border:1px solid var(--border-normal); border-radius:4px; padding:0.65rem 0.85rem; text-align:left;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.85rem; font-weight:700; color:var(--text-primary);">Streamlit Console</span>
                        <span class="badge-status badge-normal" style="font-size:0.65rem;">Port 8501</span>
                    </div>
                    <div style="font-size:0.72rem; color:var(--text-muted); margin-top:0.25rem;">Cloud Deployment • Diagnostics & Telemetry Client</div>
                </div>
            </div>
        </div>
    </div>
    """
    render_scada_html(pipeline_card_html)

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### ⚙️ Technical Engine Specifications")

    spec_c1, spec_c2, spec_c3 = st.columns(3)
    with spec_c1:
        render_scada_html("""
            <div class="card-panel">
                <h4 style="margin-top:0; color:var(--text-primary); font-size:0.88rem; text-transform:uppercase; letter-spacing:0.04em;">
                    Predictive ML Pipeline
                </h4>
                <div style="font-size:0.8rem; color:var(--text-secondary); line-height:1.7;">
                    <strong>Classifier:</strong> Gradient Boosting (n=150, d=3)<br>
                    <strong>Decision Threshold:</strong> <span class="mono" style="color:var(--status-medium); font-weight:600;">0.40 (40.0%)</span><br>
                    <strong>Dataset:</strong> UCI AI4I 2020 Predictive Maint.<br>
                    <strong>Model Artifact:</strong> <code>models/fault_model.pkl</code>
                </div>
            </div>
        """)

    with spec_c2:
        render_scada_html("""
            <div class="card-panel">
                <h4 style="margin-top:0; color:var(--text-primary); font-size:0.88rem; text-transform:uppercase; letter-spacing:0.04em;">
                    RAG Knowledge Architecture
                </h4>
                <div style="font-size:0.8rem; color:var(--text-secondary); line-height:1.7;">
                    <strong>Vector Index:</strong> FAISS IndexFlatL2<br>
                    <strong>Embedding Model:</strong> all-MiniLM-L6-v2 (384-dim)<br>
                    <strong>Vector Store:</strong> <code>rag/maintenance.index</code><br>
                    <strong>Knowledge Corpus:</strong> <code>maintenance_knowledge.txt</code>
                </div>
            </div>
        """)

    with spec_c3:
        render_scada_html("""
            <div class="card-panel">
                <h4 style="margin-top:0; color:var(--text-primary); font-size:0.88rem; text-transform:uppercase; letter-spacing:0.04em;">
                    Diagnostic Threshold Rules
                </h4>
                <div style="font-size:0.8rem; color:var(--text-secondary); line-height:1.7;">
                    <strong>Air Temperature:</strong> Elevated &ge; 301.0 K<br>
                    <strong>Process Temp:</strong> High &ge; 312.0 K<br>
                    <strong>Rotational Speed:</strong> &lt; 1300 or &gt; 1650 RPM<br>
                    <strong>Torque & Wear:</strong> &ge; 55.0 Nm | &ge; 100 min
                </div>
            </div>
        """)

# -----------------------------------------------------------------------------
# Auto-Refresh Execution
# -----------------------------------------------------------------------------
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
