"""
P_311 Industrial IoT Fault Diagnosis System — Streamlit SCADA Console

Knowledge-driven predictive maintenance and SCADA supervisory workstation.
Visually and functionally aligned with the P_311 React SCADA dashboard.
Consumes the existing FastAPI backend REST API.
"""

import os
import math
import html
import time
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ==============================================================================
# Page Configuration & Industrial SCADA Style Tokens
# ==============================================================================
st.set_page_config(
    page_title="P_311 SCADA | Industrial IoT Fault Diagnosis",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injected SCADA CSS: Flat, matte, high-contrast, zero-glow, matching React index.css
st.markdown("""
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
        --status-medium: #C39A4A;
        --status-high: #C8753D;
        --status-critical: #B65353;
    }

    /* Streamlit Global Overrides */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    header[data-testid="stHeader"] {
        background-color: var(--bg-primary);
        border-bottom: 1px solid var(--border-normal);
    }

    .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Flat Industrial Card Panels */
    .card-panel {
        background-color: var(--bg-panel);
        border: 1px solid var(--border-normal);
        border-radius: 4px;
        padding: 1.25rem;
        box-sizing: border-box;
    }

    .card-panel-elevated {
        background-color: var(--bg-elevated);
        border: 1px solid var(--border-normal);
        border-radius: 4px;
        padding: 1.25rem;
        box-sizing: border-box;
    }

    /* Badges */
    .badge-status {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.22rem 0.65rem;
        font-size: 0.78rem;
        font-weight: 600;
        border-radius: 3px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .badge-normal {
        color: var(--status-normal);
        background-color: rgba(111, 163, 111, 0.12);
        border: 1px solid var(--status-normal);
    }
    .badge-medium {
        color: var(--status-medium);
        background-color: rgba(195, 154, 74, 0.12);
        border: 1px solid var(--status-medium);
    }
    .badge-high {
        color: var(--status-high);
        background-color: rgba(200, 117, 61, 0.12);
        border: 1px solid var(--status-high);
    }
    .badge-critical {
        color: var(--status-critical);
        background-color: rgba(182, 83, 83, 0.15);
        border: 1px solid var(--status-critical);
    }

    /* Status Dots */
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }
    .status-dot-normal { background-color: var(--status-normal); }
    .status-dot-medium { background-color: var(--status-medium); }
    .status-dot-high { background-color: var(--status-high); }
    .status-dot-critical { background-color: var(--status-critical); }

    /* Workstation Navigation Tabs */
    div[data-baseweb="tab-list"] {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-normal) !important;
        border-radius: 4px !important;
        padding: 6px 10px !important;
        gap: 8px !important;
        margin-bottom: 1.25rem !important;
    }
    button[data-baseweb="tab"] {
        background-color: var(--bg-panel) !important;
        border: 1px solid var(--border-normal) !important;
        border-radius: 4px !important;
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.90rem !important;
        padding: 0.55rem 1.15rem !important;
        transition: all 0.15s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        background-color: var(--bg-elevated) !important;
        border-color: var(--border-strong) !important;
        color: var(--text-primary) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--accent-subtle) !important;
        border-color: var(--accent) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* Technical Buttons */
    div.stButton > button {
        background-color: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-normal) !important;
        border-radius: 4px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.45rem 0.9rem !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button:hover {
        background-color: #32373B !important;
        border-color: var(--border-strong) !important;
    }

    /* Expander styling */
    div[data-testid="stExpander"] {
        background-color: var(--bg-panel) !important;
        border: 1px solid var(--border-normal) !important;
        border-radius: 4px !important;
    }
    div[data-testid="stExpander"] summary {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    /* Tables */
    .scada-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
        text-align: left;
    }
    .scada-table th {
        background-color: var(--bg-secondary);
        color: var(--text-muted);
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 0.65rem 0.75rem;
        border-bottom: 1px solid var(--border-normal);
    }
    .scada-table td {
        padding: 0.6rem 0.75rem;
        border-bottom: 1px solid var(--border-normal);
        color: var(--text-primary);
    }
    .scada-table tr:hover {
        background-color: var(--bg-elevated);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# Backend Configuration & Session State
# ==============================================================================
default_backend = "http://127.0.0.1:8000"
try:
    if hasattr(st, "secrets") and "BACKEND_URL" in st.secrets:
        default_backend = st.secrets["BACKEND_URL"]
except Exception:
    pass
if "BACKEND_URL" in os.environ:
    default_backend = os.environ["BACKEND_URL"]

# Sidebar connection settings
with st.sidebar:
    st.markdown("### ⚙️ SCADA Cloud Settings")
    st.markdown("<p style='font-size:0.8rem; color:#A7ADB1;'>Configure backend API connectivity for cloud deployments.</p>", unsafe_allow_html=True)
    custom_backend = st.text_input("FastAPI Endpoint URL", value=default_backend, help="Points to local or cloud-deployed FastAPI REST server.")
    BACKEND_URL = custom_backend.rstrip("/")
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#737A7F;'>
        <strong>Cloud Deployment Notes:</strong><br>
        • Deploy on Streamlit Cloud from your GitHub repo.<br>
        • If backend is local, set up an ngrok or public tunnel URL here.<br>
        • Standalone engine activates automatically if backend is offline.
    </div>
    """, unsafe_allow_html=True)

if "active_machine" not in st.session_state:
    st.session_state.active_machine = "Machine 1"
if "is_paused" not in st.session_state:
    st.session_state.is_paused = False
if "schematic_part" not in st.session_state:
    st.session_state.schematic_part = "all"
if "trends_metric" not in st.session_state:
    st.session_state.trends_metric = "probability"
if "local_sim_history" not in st.session_state:
    st.session_state.local_sim_history = []
if "local_sim_reading" not in st.session_state:
    st.session_state.local_sim_reading = None

# ==============================================================================
# Helper Functions: FastAPI REST Clients
# ==============================================================================
@st.cache_data(ttl=2)
def fetch_system_status(url: str):
    try:
        r = requests.get(f"{url}/api/status", timeout=2)
        return r.json() if r.ok else None
    except Exception:
        return None

@st.cache_data(ttl=3)
def fetch_database_stats(url: str):
    try:
        r = requests.get(f"{url}/api/database/stats", timeout=2)
        return r.json() if r.ok else None
    except Exception:
        return None

@st.cache_data(ttl=1)
def fetch_latest_reading(url: str, machine_id: str):
    try:
        r = requests.get(f"{url}/api/latest/{machine_id}", timeout=2.5)
        return r.json() if r.ok else None
    except Exception:
        return None

@st.cache_data(ttl=2)
def fetch_history(url: str, machine_id: str, limit: int = 50, severity: str = "ALL"):
    try:
        params = {"machine_id": machine_id, "limit": limit}
        if severity != "ALL":
            params["severity"] = severity
        r = requests.get(f"{url}/api/history", params=params, timeout=3)
        return r.json() if r.ok else []
    except Exception:
        return []

@st.cache_data(ttl=10)
def fetch_all_knowledge(url: str):
    try:
        r = requests.get(f"{url}/api/knowledge", timeout=3)
        return r.json() if r.ok else []
    except Exception:
        return []

def search_knowledge(url: str, query: str):
    try:
        r = requests.get(f"{url}/api/knowledge/search", params={"q": query}, timeout=3)
        return r.json() if r.ok else []
    except Exception:
        return []

def trigger_simulation(url: str, scenario: str, machine_id: str):
    try:
        r = requests.post(f"{url}/api/simulate", params={"scenario": scenario, "machine_id": machine_id}, timeout=3)
        return r.ok
    except Exception:
        return False

# ==============================================================================
# SVG Visual Generator Functions (Gauge, Sparkline, Range Bar, Schematic)
# ==============================================================================
def render_sparkline_svg(data, color="#5B7C99", width=80, height=22):
    if not data or len(data) < 2:
        return f'<span style="font-size:0.65rem; color:#737A7F;">--</span>'
    nums = [float(x) for x in data if x is not None]
    if len(nums) < 2:
        return f'<span style="font-size:0.65rem; color:#737A7F;">--</span>'
    min_v, max_v = min(nums), max(nums)
    rng = max_v - min_v or 1.0
    pts = []
    for i, v in enumerate(nums):
        x = (i / (len(nums) - 1)) * width
        y = height - ((v - min_v) / rng) * (height - 4) - 2
        pts.append(f"{x:.1f},{y:.1f}")
    return f"""
    <svg width="{width}" height="{height}" style="overflow:visible;">
        <polyline fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="square" stroke-linejoin="round" points="{' '.join(pts)}" />
    </svg>
    """

def render_range_bar_html(val, min_v, max_v, unit, is_normal, status_color):
    clamped = max(min_v, min(max_v, float(val or 0)))
    pct = max(0, min(100, ((clamped - min_v) / (max_v - min_v)) * 100))
    bar_color = "var(--border-strong)" if is_normal else status_color
    return f"""
    <div style="width:100%; margin-top:0.65rem;">
        <div style="position:relative; width:100%; height:4px; background-color:var(--bg-secondary); border-radius:2px; overflow:hidden;">
            <div style="width:{pct:.1f}%; height:100%; background-color:{bar_color}; border-radius:2px;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.68rem; color:var(--text-muted); margin-top:0.25rem;">
            <span>{min_v} {unit}</span>
            <span>{max_v} {unit}</span>
        </div>
    </div>
    """

def render_failure_risk_gauge_svg(probability=0.0, threshold=0.40, status="NORMAL"):
    prob_pct = max(0.0, min(100.0, probability * 100))
    thresh_pct = threshold * 100.0

    radius = 86
    stroke_width = 10
    total_len = math.pi * radius
    active_len = (prob_pct / 100.0) * total_len

    if prob_pct >= 75.0:
        status_color = "#B65353"
    elif prob_pct >= thresh_pct:
        status_color = "#C8753D"
    elif prob_pct >= 20.0:
        status_color = "#C39A4A"
    else:
        status_color = "#6FA36F"

    angle_deg = 180.0 - (prob_pct / 100.0) * 180.0

    # Threshold marker line coordinates
    trad = ((180.0 - (thresh_pct / 100.0) * 180.0) * math.pi) / 180.0
    tx1 = 110 + 72 * math.cos(trad)
    ty1 = 110 - 72 * math.sin(trad)
    tx2 = 110 + 98 * math.cos(trad)
    ty2 = 110 - 98 * math.sin(trad)

    # Needle tip coordinates
    nrad = (angle_deg * math.pi) / 180.0
    nx = 110 + 70 * math.cos(nrad)
    ny = 110 - 70 * math.sin(nrad)

    return f"""
    <div class="card-panel" style="display:flex; flex-direction:column; align-items:center; justify-content:space-between; padding:1.45rem; min-height:265px;">
        <div style="width:100%; display:flex; align-items:center; justify-content:space-between;">
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <span style="font-size:0.88rem; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.04em; fontWeight:600;">
                    Predictive Failure Risk
                </span>
            </div>
            <div style="display:flex; align-items:center; gap:0.4rem; font-size:0.82rem; color:var(--status-medium);">
                <span>Cutoff: {thresh_pct:.0f}%</span>
            </div>
        </div>

        <div style="position:relative; width:220px; height:125px; margin-top:0.85rem;">
            <svg width="220" height="125" viewBox="0 0 220 125">
                <path d="M 24 110 A 86 86 0 0 1 196 110" fill="none" stroke="var(--bg-elevated)" stroke-width="{stroke_width}" stroke-linecap="square" />
                <path d="M 24 110 A 86 86 0 0 1 196 110" fill="none" stroke="{status_color}" stroke-width="{stroke_width}" stroke-dasharray="{total_len:.1f}" stroke-dashoffset="{(total_len - active_len):.1f}" stroke-linecap="square" />
                <line x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" stroke="var(--status-medium)" stroke-width="2.5" />
                <circle cx="110" cy="110" r="5" fill="var(--text-primary)" />
                <line x1="110" y1="110" x2="{nx:.1f}" y2="{ny:.1f}" stroke="var(--text-primary)" stroke-width="2.5" stroke-linecap="round" />
            </svg>
            <div style="position:absolute; bottom:0; left:0; right:0; text-align:center;">
                <div class="mono" style="font-size:2.4rem; font-weight:700; color:{status_color}; line-height:1;">
                    {prob_pct:.2f}%
                </div>
                <div style="font-size:0.78rem; color:var(--text-muted); margin-top:0.25rem;">
                    Gradient Boosting Model
                </div>
            </div>
        </div>

        <div style="width:100%; margin-top:0.95rem; padding:0.55rem 0.95rem; border-radius:4px; background-color:var(--bg-elevated); border:1px solid var(--border-normal); display:flex; align-items:center; justify-content:space-between; font-size:0.85rem;">
            <span style="color:var(--text-secondary);">Evaluated Status:</span>
            <strong style="color:{status_color}; font-size:0.9rem;">{status}</strong>
        </div>
    </div>
    """

def render_machine_schematic_svg(sensors, evals, selected_part="all"):
    motor_alert = not evals.get("rotational_speed", {}).get("is_normal", True) or not evals.get("torque", {}).get("is_normal", True)
    thermal_alert = not evals.get("air_temperature", {}).get("is_normal", True) or not evals.get("process_temperature", {}).get("is_normal", True)
    tool_alert = not evals.get("tool_wear", {}).get("is_normal", True)

    op_motor = 1.0 if selected_part in ["all", "motor"] else 0.25
    op_thermal = 1.0 if selected_part in ["all", "thermal"] else 0.25
    op_tool = 1.0 if selected_part in ["all", "tool"] else 0.25

    motor_stroke = "var(--status-high)" if motor_alert else "var(--border-strong)"
    thermal_stroke = "var(--status-high)" if thermal_alert else "var(--border-strong)"
    tool_stroke = "var(--status-critical)" if tool_alert else "var(--border-strong)"
    tool_tip = "var(--status-critical)" if tool_alert else "var(--status-normal)"

    speed_val = sensors.get("rotational_speed", 0)
    torque_val = sensors.get("torque", 0.0)
    proc_val = sensors.get("process_temperature", 0.0)
    air_val = sensors.get("air_temperature", 0.0)
    wear_val = sensors.get("tool_wear", 0)

    return f"""
    <div style="position:relative; width:100%; background-color:var(--bg-secondary); border-radius:4px; border:1px solid var(--border-normal); display:flex; align-items:center; justify-content:center; padding:1.25rem; overflow:hidden;">
        <svg viewBox="0 0 960 330" style="width:100%; height:auto; max-height:350px;">
            <!-- Centerline Axis -->
            <line x1="60" y1="185" x2="900" y2="185" stroke="var(--border-normal)" stroke-width="1" stroke-dasharray="6,4" />

            <!-- SECTION 1: DRIVE MOTOR -->
            <g opacity="{op_motor}">
                <rect x="90" y="110" width="170" height="150" rx="4" fill="var(--bg-panel)" stroke="{motor_stroke}" stroke-width="1.5" />
                <line x1="120" y1="95" x2="120" y2="110" stroke="{motor_stroke}" stroke-width="2" />
                <line x1="150" y1="95" x2="150" y2="110" stroke="{motor_stroke}" stroke-width="2" />
                <line x1="180" y1="95" x2="180" y2="110" stroke="{motor_stroke}" stroke-width="2" />
                <line x1="210" y1="95" x2="210" y2="110" stroke="{motor_stroke}" stroke-width="2" />
                <line x1="240" y1="95" x2="240" y2="110" stroke="{motor_stroke}" stroke-width="2" />
                <text x="175" y="175" fill="var(--text-primary)" font-size="12" font-weight="600" text-anchor="middle" letter-spacing="0.04em">DRIVE MOTOR</text>
                <text x="175" y="195" fill="var(--text-secondary)" font-size="10" text-anchor="middle" font-family="JetBrains Mono">{speed_val} RPM | {torque_val:.1f} Nm</text>
            </g>

            <!-- Shaft Coupling -->
            <rect x="260" y="170" width="80" height="30" fill="var(--bg-elevated)" stroke="var(--border-normal)" stroke-width="1.5" />
            <text x="300" y="190" fill="var(--text-muted)" font-size="8.5" text-anchor="middle" font-weight="500">SHAFT</text>

            <!-- SECTION 2: SPINDLE & THERMAL SLEEVE -->
            <g opacity="{op_thermal}">
                <rect x="340" y="120" width="240" height="130" rx="4" fill="var(--bg-panel)" stroke="{thermal_stroke}" stroke-width="1.5" />
                <rect x="375" y="155" width="40" height="60" rx="3" fill="var(--bg-elevated)" stroke="var(--border-normal)" stroke-width="1" />
                <text x="395" y="190" fill="var(--text-muted)" font-size="9" text-anchor="middle" font-weight="600">BRG-1</text>
                <rect x="505" y="155" width="40" height="60" rx="3" fill="var(--bg-elevated)" stroke="var(--border-normal)" stroke-width="1" />
                <text x="525" y="190" fill="var(--text-muted)" font-size="9" text-anchor="middle" font-weight="600">BRG-2</text>
                <text x="460" y="145" fill="var(--text-primary)" font-size="12" font-weight="600" text-anchor="middle" letter-spacing="0.04em">SPINDLE & THERMAL SLEEVE</text>
                <text x="460" y="235" fill="var(--text-secondary)" font-size="10" text-anchor="middle" font-family="JetBrains Mono">Proc: {proc_val:.1f} K | Air: {air_val:.1f} K</text>
            </g>

            <!-- Collet Chuck -->
            <polygon points="580,145 660,160 660,210 580,225" fill="var(--bg-elevated)" stroke="var(--border-normal)" stroke-width="1.5" />
            <text x="615" y="190" fill="var(--text-muted)" font-size="8.5" text-anchor="middle" font-weight="500">CHUCK</text>

            <!-- SECTION 3: CUTTING TOOL HEAD -->
            <g opacity="{op_tool}">
                <polygon points="660,175 790,178 840,185 790,192 660,195" fill="var(--bg-panel)" stroke="{tool_stroke}" stroke-width="1.5" />
                <circle cx="840" cy="185" r="4" fill="{tool_tip}" />
                <text x="740" y="165" fill="var(--text-primary)" font-size="11" font-weight="600" text-anchor="middle" letter-spacing="0.04em">CUTTING TOOL</text>
                <text x="740" y="215" fill="var(--text-secondary)" font-size="10" text-anchor="middle" font-family="JetBrains Mono">Wear: {wear_val} min</text>
            </g>

            <!-- Annotation Callout Pins with Dashed Leader Lines -->
            <!-- Motor Callout -->
            <g transform="translate(175, 40)">
                <rect x="-80" y="-22" width="160" height="40" rx="4" fill="var(--bg-elevated)" stroke="{motor_stroke}" stroke-width="1" />
                <text x="0" y="-7" fill="{motor_stroke if motor_alert else 'var(--text-primary)'}" font-size="11" font-weight="700" text-anchor="middle" font-family="JetBrains Mono">{speed_val} RPM</text>
                <text x="0" y="10" fill="var(--text-secondary)" font-size="9.5" text-anchor="middle" font-family="JetBrains Mono">Torque: {torque_val:.1f} Nm</text>
                <line x1="0" y1="18" x2="0" y2="70" stroke="{motor_stroke}" stroke-width="1" stroke-dasharray="3,3" />
            </g>

            <!-- Spindle Callout -->
            <g transform="translate(460, 40)">
                <rect x="-90" y="-22" width="180" height="40" rx="4" fill="var(--bg-elevated)" stroke="{thermal_stroke}" stroke-width="1" />
                <text x="0" y="-7" fill="{thermal_stroke if thermal_alert else 'var(--text-primary)'}" font-size="11" font-weight="700" text-anchor="middle" font-family="JetBrains Mono">Proc Temp: {proc_val:.1f} K</text>
                <text x="0" y="10" fill="var(--text-secondary)" font-size="9.5" text-anchor="middle" font-family="JetBrains Mono">Air: {air_val:.1f} K (ΔT: {(proc_val - air_val):.1f} K)</text>
                <line x1="0" y1="18" x2="0" y2="80" stroke="{thermal_stroke}" stroke-width="1" stroke-dasharray="3,3" />
            </g>

            <!-- Tool Callout -->
            <g transform="translate(740, 40)">
                <rect x="-80" y="-22" width="160" height="40" rx="4" fill="var(--bg-elevated)" stroke="{tool_stroke}" stroke-width="1" />
                <text x="0" y="-7" fill="{tool_stroke if tool_alert else 'var(--text-primary)'}" font-size="11" font-weight="700" text-anchor="middle" font-family="JetBrains Mono">Tool Wear: {wear_val} min</text>
                <text x="0" y="10" fill="var(--text-secondary)" font-size="9.5" text-anchor="middle" font-family="JetBrains Mono">Limit: &lt; 100 min</text>
                <line x1="0" y1="18" x2="0" y2="125" stroke="{tool_stroke}" stroke-width="1" stroke-dasharray="3,3" />
            </g>
        </svg>
    </div>
    """

# ==============================================================================
# Fetch Real-Time Data from FastAPI
# ==============================================================================
sys_status = fetch_system_status(BACKEND_URL)
db_stats = fetch_database_stats(BACKEND_URL)
mqtt_connected = sys_status.get("mqtt_connected", False) if sys_status else False
backend_connected = sys_status is not None

# Query available machines
machines_list = ["Machine 1"]
try:
    m_res = requests.get(f"{BACKEND_URL}/api/machines", timeout=1.5)
    if m_res.ok and m_res.json():
        machines_list = m_res.json()
except Exception:
    pass

# Current active telemetry reading
latest_data = fetch_latest_reading(BACKEND_URL, st.session_state.active_machine)
history_records = fetch_history(BACKEND_URL, st.session_state.active_machine, limit=60)

# ==============================================================================
# 1. TOP SCADA HEADER BAR (Matching React Header.jsx)
# ==============================================================================
header_col1, header_col2 = st.columns([1.3, 2.2])

with header_col1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.9rem; margin-bottom:0.25rem;">
        <div style="background-color:var(--bg-elevated); border:1px solid var(--border-normal); padding:0.45rem 0.85rem; border-radius:4px; font-size:1.05rem; font-weight:700; letter-spacing:0.05em; color:var(--text-primary); display:flex; align-items:center; gap:0.5rem;">
            ⚙️ P_311
        </div>
        <div>
            <h1 style="font-size:1.35rem; font-weight:600; color:var(--text-primary); letter-spacing:-0.01em; margin:0; line-height:1.2;">
                Knowledge-Driven IoT Fault Diagnosis Assistant
            </h1>
            <p style="font-size:0.85rem; color:var(--text-muted); margin:0.15rem 0 0 0;">
                Industrial Supervisory & Predictive Maintenance Console
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    # Machine selection, Connection status pills, updated time, controls
    c_m, c_mqtt, c_backend, c_time, c_pause, c_refresh = st.columns([1.4, 1.4, 1.4, 1.6, 0.9, 0.8])

    with c_m:
        selected_m = st.selectbox(
            "Target Machine",
            options=machines_list,
            index=0 if st.session_state.active_machine not in machines_list else machines_list.index(st.session_state.active_machine),
            label_visibility="collapsed"
        )
        if selected_m != st.session_state.active_machine:
            st.session_state.active_machine = selected_m
            st.rerun()

    with c_mqtt:
        dot_color = "var(--status-normal)" if mqtt_connected else "var(--status-critical)"
        status_txt = "MQTT Connected" if mqtt_connected else "MQTT Offline"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.55rem; font-size:0.82rem; background-color:var(--bg-panel); padding:0.45rem 0.65rem; border-radius:4px; border:1px solid var(--border-normal); height:38px; box-sizing:border-box;">
            <span class="status-dot" style="background-color:{dot_color};"></span>
            <span style="color:var(--text-secondary); font-weight:500;">{status_txt}</span>
        </div>
        """, unsafe_allow_html=True)

    with c_backend:
        b_color = "var(--status-normal)" if backend_connected else "var(--status-critical)"
        b_txt = "Backend Active" if backend_connected else "Backend Lost"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.55rem; font-size:0.82rem; background-color:var(--bg-panel); padding:0.45rem 0.65rem; border-radius:4px; border:1px solid var(--border-normal); height:38px; box-sizing:border-box;">
            <span class="status-dot" style="background-color:{b_color};"></span>
            <span style="color:var(--text-secondary); font-weight:500;">{b_txt}</span>
        </div>
        """, unsafe_allow_html=True)

    with c_time:
        last_time = latest_data.get("timestamp", "Waiting...") if latest_data else "No telemetry"
        st.markdown(f"""
        <div style="font-size:0.82rem; background-color:var(--bg-panel); padding:0.45rem 0.65rem; border-radius:4px; border:1px solid var(--border-normal); height:38px; box-sizing:border-box; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
            <span style="color:var(--text-muted); margin-right:0.25rem;">Sync:</span>
            <span class="mono" style="color:var(--text-primary);">{last_time[-8:] if len(last_time) >= 8 else last_time}</span>
        </div>
        """, unsafe_allow_html=True)

    with c_pause:
        btn_label = "▶" if st.session_state.is_paused else "⏸"
        if st.button(btn_label, help="Pause/Resume live auto refresh"):
            st.session_state.is_paused = not st.session_state.is_paused
            st.rerun()

    with c_refresh:
        if st.button("🔄", help="Manual refresh"):
            st.cache_data.clear()
            st.rerun()

# ==============================================================================
# Quick Scenario Simulation Bar (Matching SimulationControlBar.jsx)
# ==============================================================================
with st.expander("🧪 SCADA Telemetry & Fault Scenario Injection Toolbar", expanded=False):
    s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
    with s_col1:
        if st.button("🟢 Nominal Normal", use_container_width=True):
            trigger_simulation(BACKEND_URL, "NORMAL", st.session_state.active_machine)
            st.cache_data.clear()
            st.rerun()
    with s_col2:
        if st.button("🔥 Thermal Overload", use_container_width=True):
            trigger_simulation(BACKEND_URL, "HIGH_TEMP", st.session_state.active_machine)
            st.cache_data.clear()
            st.rerun()
    with s_col3:
        if st.button("⚙️ High Torque Overload", use_container_width=True):
            trigger_simulation(BACKEND_URL, "HIGH_TORQUE", st.session_state.active_machine)
            st.cache_data.clear()
            st.rerun()
    with s_col4:
        if st.button("🔧 Severe Tool Wear", use_container_width=True):
            trigger_simulation(BACKEND_URL, "HIGH_WEAR", st.session_state.active_machine)
            st.cache_data.clear()
            st.rerun()
    with s_col5:
        if st.button("🚨 Critical Runaway", use_container_width=True):
            trigger_simulation(BACKEND_URL, "CRITICAL", st.session_state.active_machine)
            st.cache_data.clear()
            st.rerun()

st.markdown("<hr style='border:none; border-top:1px solid var(--border-normal); margin:0.65rem 0 1.15rem 0;'>", unsafe_allow_html=True)

# Parse Latest Telemetry
is_waiting = not latest_data or latest_data.get("waiting", False)
sensors = latest_data.get("sensors", {}) if not is_waiting else {}
diagnosis = latest_data.get("diagnosis", {}) if not is_waiting else {}
evals = diagnosis.get("sensor_evaluations", {}) if not is_waiting else {}
severity = diagnosis.get("severity", "LOW")
status_label = diagnosis.get("status", "NORMAL")
failure_prob = diagnosis.get("failure_probability", 0.0)
failure_prob_pct = diagnosis.get("failure_probability_pct", f"{failure_prob*100:.2f}%")
recommendation = diagnosis.get("recommendation", "Machine operating within nominal envelope. Maintain scheduled telemetry logging.")
issues = diagnosis.get("issues", [])
rag_items = diagnosis.get("rag_knowledge", [])

# ==============================================================================
# 2. WORKSTATION NAVIGATION TABS (5 Tabs Matching React UI)
# ==============================================================================
tab_dashboard, tab_twin, tab_diagnostics, tab_history, tab_system = st.tabs([
    "⚡ Live Monitor",
    "📐 3D Digital Twin",
    "📖 Diagnostics & RAG Manual",
    "📊 History & Sensor Trends",
    "🖥️ System Architecture"
])

# ==============================================================================
# TAB 1: LIVE MONITOR (DashboardPage.jsx)
# ==============================================================================
with tab_dashboard:
    if is_waiting:
        st.markdown("""
        <div class="card-panel" style="padding:3.5rem 2rem; text-align:center; min-height:280px; display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <div style="font-size:1.8rem; margin-bottom:0.75rem;">📡</div>
            <h2 style="font-size:1.25rem; font-weight:600; color:var(--text-primary); margin-bottom:0.4rem;">
                Awaiting Machine Telemetry Stream
            </h2>
            <p style="color:var(--text-muted); font-size:0.875rem; max-width:540px; margin:0 auto 1.25rem auto;">
                The ingestion engine is subscribed to MQTT topic <span class="mono" style="color:var(--text-primary);">factory/machine1/sensors</span>.
                Use the simulation toolbar above or ensure the simulator is transmitting.
            </p>
            <div style="background-color:var(--bg-secondary); border:1px solid var(--border-normal); border-radius:4px; padding:0.55rem 1.15rem; font-size:0.825rem;">
                <code class="mono" style="color:var(--status-normal); font-weight:600;">python3 ai4i_machine_simulator.py</code>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Alarm Banner (if severity HIGH or CRITICAL)
        if severity in ["HIGH", "CRITICAL"]:
            alarm_border = "var(--status-critical)" if severity == "CRITICAL" else "var(--status-high)"
            alarm_bg = "rgba(182, 83, 83, 0.15)" if severity == "CRITICAL" else "rgba(200, 117, 61, 0.12)"
            st.markdown(f"""
            <div style="background-color:{alarm_bg}; border:1px solid {alarm_border}; border-left:6px solid {alarm_border}; border-radius:4px; padding:0.85rem 1.25rem; margin-bottom:1.15rem; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <span style="font-size:1.25rem;">⚠️</span>
                    <div>
                        <strong style="color:{alarm_border}; font-size:0.95rem; letter-spacing:0.04em;">ACTIVE SCADA ALARM: {severity} SEVERITY FAULT DETECTED</strong>
                        <div style="font-size:0.85rem; color:var(--text-primary); margin-top:0.15rem;">
                            ML Failure probability ({failure_prob_pct}) has breached the 40.0% cutoff threshold. Inspect conditions immediately.
                        </div>
                    </div>
                </div>
                <span class="mono" style="font-size:0.8rem; color:var(--text-secondary);">{latest_data.get('timestamp')}</span>
            </div>
            """, unsafe_allow_html=True)

        # Machine Status Overview Card (MachineStatusCard.jsx)
        indicator_color = "var(--status-normal)"
        badge_cls = "badge-normal"
        if severity == "MEDIUM":
            indicator_color = "var(--status-medium)"
            badge_cls = "badge-medium"
        elif severity == "HIGH":
            indicator_color = "var(--status-high)"
            badge_cls = "badge-high"
        elif severity == "CRITICAL":
            indicator_color = "var(--status-critical)"
            badge_cls = "badge-critical"

        type_map = {'L': 'Low Quality Variant (L)', 'M': 'Medium Quality Variant (M)', 'H': 'High Quality Variant (H)'}
        type_desc = type_map.get(sensors.get("type", "L"), f"Variant {sensors.get('type')}")

        st.markdown(f"""
        <div class="card-panel" style="border-left:5px solid {indicator_color}; padding:1.25rem 1.65rem; margin-bottom:1.25rem;">
            <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1.5rem;">
                <div style="display:flex; align-items:center; gap:1.25rem;">
                    <div style="padding:0.75rem; border-radius:4px; background-color:var(--bg-elevated); border:1px solid var(--border-normal); font-size:1.5rem;">
                        {'✅' if status_label == 'NORMAL' else '⚠️'}
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:0.65rem; margin-bottom:0.3rem;">
                            <span style="font-size:0.85rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em; font-weight:600;">
                                {st.session_state.active_machine} OPERATIONAL STATE
                            </span>
                            <span style="font-size:0.82rem; background-color:var(--bg-elevated); border:1px solid var(--border-normal); padding:0.15rem 0.55rem; border-radius:3px; color:var(--text-secondary);">
                                {type_desc}
                            </span>
                        </div>
                        <div style="display:flex; align-items:center; gap:0.85rem;">
                            <h2 style="font-size:1.75rem; font-weight:700; letter-spacing:-0.01em; margin:0; color:{'var(--status-normal)' if status_label == 'NORMAL' else indicator_color};">
                                {status_label}
                            </h2>
                            <span class="badge-status {badge_cls}" style="font-size:0.85rem; padding:0.3rem 0.75rem;">
                                {severity} SEVERITY
                            </span>
                        </div>
                    </div>
                </div>

                <div style="display:flex; align-items:center; gap:2.5rem; flex-wrap:wrap;">
                    <div>
                        <div style="font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.2rem;">
                            Failure Risk Probability
                        </div>
                        <div class="mono" style="font-size:1.75rem; font-weight:700; color:{'var(--status-normal)' if status_label == 'NORMAL' else indicator_color};">
                            {failure_prob_pct}
                        </div>
                    </div>
                    <div style="border-left:1px solid var(--border-normal); padding-left:1.75rem;">
                        <div style="font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.2rem;">
                            Last Evaluated
                        </div>
                        <div class="mono" style="font-size:1.05rem; color:var(--text-secondary);">
                            {latest_data.get('timestamp', '--')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 5 Sensor Metric Cards (SensorMonitoring.jsx)
        chronological_history = list(reversed(history_records))
        air_hist = [h.get("sensors", {}).get("air_temperature") for h in chronological_history]
        proc_hist = [h.get("sensors", {}).get("process_temperature") for h in chronological_history]
        speed_hist = [h.get("sensors", {}).get("rotational_speed") for h in chronological_history]
        torque_hist = [h.get("sensors", {}).get("torque") for h in chronological_history]
        wear_hist = [h.get("sensors", {}).get("tool_wear") for h in chronological_history]

        sensor_configs = [
            {
                "label": "AIR TEMPERATURE",
                "val": sensors.get("air_temperature", 0.0),
                "unit": "K",
                "min": 290, "max": 310,
                "limit": "Limit: < 301.0 K",
                "eval": evals.get("air_temperature", {}),
                "hist": air_hist
            },
            {
                "label": "PROCESS TEMPERATURE",
                "val": sensors.get("process_temperature", 0.0),
                "unit": "K",
                "min": 300, "max": 320,
                "limit": "Limit: < 312.0 K",
                "eval": evals.get("process_temperature", {}),
                "hist": proc_hist
            },
            {
                "label": "ROTATIONAL SPEED",
                "val": sensors.get("rotational_speed", 0),
                "unit": "RPM",
                "min": 1000, "max": 2000,
                "limit": "Band: 1300 - 1650 RPM",
                "eval": evals.get("rotational_speed", {}),
                "hist": speed_hist
            },
            {
                "label": "SHAFT TORQUE",
                "val": sensors.get("torque", 0.0),
                "unit": "Nm",
                "min": 20, "max": 80,
                "limit": "Limit: < 55.0 Nm",
                "eval": evals.get("torque", {}),
                "hist": torque_hist
            },
            {
                "label": "TOOL DEGRADATION",
                "val": sensors.get("tool_wear", 0),
                "unit": "min",
                "min": 0, "max": 250,
                "limit": "Limit: < 100 min",
                "eval": evals.get("tool_wear", {}),
                "hist": wear_hist
            }
        ]

        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.65rem;">
            <span style="font-size:0.95rem; font-weight:600; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.05em;">
                LIVE SENSOR TELEMETRY
            </span>
            <span style="font-size:0.82rem; color:var(--text-muted);">
                Operating Thresholds: diagnosis.py
            </span>
        </div>
        """, unsafe_allow_html=True)

        sc_cols = st.columns(5)
        for i, s in enumerate(sensor_configs):
            is_n = s["eval"].get("is_normal", True)
            s_label = s["eval"].get("status_label", "NORMAL")
            badge_c = "badge-normal"
            sc_color = "var(--status-normal)"
            if s_label in ["ELEVATED", "INCREASING", "LOW"]:
                badge_c = "badge-medium"
                sc_color = "var(--status-medium)"
            elif s_label == "HIGH":
                badge_c = "badge-high"
                sc_color = "var(--status-high)"
            elif s_label == "CRITICAL":
                badge_c = "badge-critical"
                sc_color = "var(--status-critical)"

            num_str = f"{s['val']:.1f}" if isinstance(s['val'], float) else str(s['val'])
            range_bar_markup = render_range_bar_html(s['val'], s['min'], s['max'], s['unit'], is_n, sc_color)
            spark_markup = render_sparkline_svg(s['hist'], color="#5B7C99" if is_n else sc_color)

            with sc_cols[i]:
                st.markdown(f"""
                <div class="card-panel" style="padding:1.25rem 1.15rem; min-height:185px; display:flex; flex-direction:column; justify-content:space-between;">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.45rem;">
                        <span style="font-size:0.80rem; color:var(--text-secondary); font-weight:600; letter-spacing:0.03em;">
                            {s['label']}
                        </span>
                        <span class="badge-status {badge_c}" style="font-size:0.75rem; padding:0.2rem 0.55rem;">
                            {s_label}
                        </span>
                    </div>

                    <div style="display:flex; align-items:baseline; gap:0.45rem; margin:0.35rem 0;">
                        <span class="mono" style="font-size:2.2rem; font-weight:700; color:var(--text-primary); line-height:1;">
                            {num_str}
                        </span>
                        <span style="font-size:0.92rem; color:var(--text-muted); font-weight:500;">
                            {s['unit']}
                        </span>
                    </div>

                    <div>
                        <div style="font-size:0.78rem; color:{'var(--text-muted)' if is_n else sc_color}; font-weight:500; margin-bottom:0.15rem;">
                            {s['limit']}
                        </div>
                        {range_bar_markup}
                    </div>

                    <div style="display:flex; align-items:center; justify-content:space-between; border-top:1px solid var(--border-normal); padding-top:0.5rem; margin-top:0.6rem;">
                        <span style="font-size:0.75rem; color:var(--text-muted);">Trend</span>
                        {spark_markup}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.25rem;'></div>", unsafe_allow_html=True)

        # 2-Column Diagnostic & Decision Panel (FailureRiskGauge + DiagnosisPanel on Left | RecommendedAction on Right)
        col_diag_left, col_diag_right = st.columns([1, 1.4])

        with col_diag_left:
            # SVG Radial Gauge
            gauge_html = render_failure_risk_gauge_svg(
                probability=failure_prob,
                threshold=0.40,
                status=status_label
            )
            st.markdown(gauge_html, unsafe_allow_html=True)

            st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)

            # Diagnosis Contributing Conditions Panel (DiagnosisPanel.jsx)
            is_all_clear = not issues or len(issues) == 0 or (len(issues) == 1 and "No major abnormal" in issues[0])
            issues_content = ""
            if is_all_clear:
                issues_content = """
                <div style="display:flex; align-items:center; gap:0.65rem; padding:0.85rem 1rem; border-radius:4px; background-color:rgba(111,163,111,0.12); border:1px solid var(--status-normal); color:var(--status-normal); font-size:0.88rem;">
                    <span>✓</span>
                    <span>No major abnormal sensor condition detected</span>
                </div>
                """
            else:
                for iss in issues:
                    issues_content += f"""
                    <div style="display:flex; align-items:flex-start; gap:0.65rem; padding:0.65rem 0.85rem; border-radius:4px; background-color:var(--bg-elevated); border:1px solid var(--border-normal); font-size:0.88rem; color:var(--text-primary); margin-bottom:0.45rem;">
                        <span style="color:var(--status-medium); flex-shrink:0;">⚠️</span>
                        <span>{iss}</span>
                    </div>
                    """

            st.markdown(f"""
            <div class="card-panel" style="padding:1.25rem 1.45rem;">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem; border-bottom:1px solid var(--border-normal); padding-bottom:0.55rem;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="font-size:0.92rem; font-weight:600; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.04em;">
                            Machine Diagnosis
                        </span>
                    </div>
                    <span style="font-size:0.78rem; color:var(--text-muted);">Rule Engine Active</span>
                </div>
                <div style="font-size:0.82rem; color:var(--text-muted); margin-bottom:0.65rem;">
                    Possible Contributing Conditions:
                </div>
                {issues_content}
            </div>
            """, unsafe_allow_html=True)

        with col_diag_right:
            # Recommended Action Panel (RecommendedAction.jsx)
            action_title = "Standard Operating Procedure"
            action_border = "var(--border-normal)"
            action_color = "var(--status-normal)"
            action_icon = "✓"
            if severity == "CRITICAL":
                action_title = "Immediate Inspection Required"
                action_border = "var(--status-critical)"
                action_color = "var(--status-critical)"
                action_icon = "🛑"
            elif severity == "HIGH":
                action_title = "High Priority Maintenance Scheduled"
                action_border = "var(--status-high)"
                action_color = "var(--status-high)"
                action_icon = "⚠️"
            elif severity == "MEDIUM":
                action_title = "Preventive Maintenance Recommended"
                action_border = "var(--status-medium)"
                action_color = "var(--status-medium)"
                action_icon = "🔧"

            st.markdown(f"""
            <div class="card-panel" style="border-left:5px solid {action_color}; display:flex; align-items:flex-start; gap:1.25rem; padding:1.35rem 1.65rem;">
                <div style="padding:0.65rem; border-radius:4px; background-color:var(--bg-elevated); border:1px solid var(--border-normal); display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:1.5rem;">
                    {action_icon}
                </div>
                <div style="flex:1;">
                    <div style="display:flex; align-items:center; gap:0.65rem; margin-bottom:0.35rem;">
                        <span style="font-size:0.85rem; text-transform:uppercase; font-weight:600; letter-spacing:0.04em; color:var(--text-secondary);">
                            Recommended Action
                        </span>
                        <span style="font-size:0.8rem; color:{action_color}; font-weight:600; background-color:var(--bg-elevated); border:1px solid var(--border-normal); padding:0.15rem 0.5rem; border-radius:3px;">
                            {action_title}
                        </span>
                    </div>
                    <p style="font-size:1.15rem; font-weight:600; color:var(--text-primary); margin:0.35rem 0; line-height:1.45;">
                        {recommendation}
                    </p>
                    <p style="font-size:0.85rem; color:var(--text-muted); margin:0.2rem 0 0 0;">
                        Correlated with FAISS RAG engineering manual and domain diagnosis rules.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)

            # Quick Action Links to 3D Digital Twin & RAG Maintenance Manual
            st.markdown(f"""
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.25rem;">
                <div class="card-panel" style="display:flex; flex-direction:column; justify-content:space-between; min-height:120px;">
                    <div>
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <span style="font-size:1.1rem;">📐</span>
                            <strong style="color:var(--text-primary); font-size:1.0rem;">3D Digital Twin</strong>
                        </div>
                        <p style="font-size:0.82rem; color:var(--text-muted); margin:0.25rem 0 0 0;">
                            Inspect asset assembly CAD schematic & kinematics
                        </p>
                    </div>
                    <div style="font-size:0.85rem; color:var(--accent); font-weight:600; margin-top:0.5rem;">
                        Select '3D Digital Twin' tab above →
                    </div>
                </div>

                <div class="card-panel" style="display:flex; flex-direction:column; justify-content:space-between; min-height:120px;">
                    <div>
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <span style="font-size:1.1rem;">📖</span>
                            <strong style="color:var(--text-primary); font-size:1.0rem;">RAG Maintenance Manual</strong>
                        </div>
                        <p style="font-size:0.82rem; color:var(--text-muted); margin:0.25rem 0 0 0;">
                            {len(rag_items)} contextual troubleshooting guides active
                        </p>
                    </div>
                    <div style="font-size:0.85rem; color:var(--status-normal); font-weight:600; margin-top:0.5rem;">
                        Select 'Diagnostics & RAG' tab above →
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# TAB 2: 3D DIGITAL TWIN (DigitalTwinPage.jsx)
# ==============================================================================
with tab_twin:
    if is_waiting:
        st.info("Standing by for telemetry stream to initialize CAD kinematics...")
    else:
        st.markdown("""
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem; margin-bottom:1rem;">
            <div>
                <h3 style="font-size:1.2rem; font-weight:600; color:var(--text-primary); margin:0;">
                    Asset Subsystem Schematic
                </h3>
                <p style="font-size:0.85rem; color:var(--text-muted); margin:0.2rem 0 0 0;">
                    Technical Assembly Layout • Spindle Drive (Machine 1)
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Subsystem Filter Buttons
        f1, f2, f3, f4, _ = st.columns([1, 1, 1, 1, 2])
        with f1:
            if st.button("Complete Asset", use_container_width=True):
                st.session_state.schematic_part = "all"
        with f2:
            if st.button("Drive Motor", use_container_width=True):
                st.session_state.schematic_part = "motor"
        with f3:
            if st.button("Thermal Sleeve", use_container_width=True):
                st.session_state.schematic_part = "thermal"
        with f4:
            if st.button("Tool Head", use_container_width=True):
                st.session_state.schematic_part = "tool"

        # SVG Schematic Canvas
        schematic_svg = render_machine_schematic_svg(sensors, evals, selected_part=st.session_state.schematic_part)
        st.markdown(schematic_svg, unsafe_allow_html=True)

        st.markdown("<div style='height:1.25rem;'></div>", unsafe_allow_html=True)

        # CAD Kinematics & Physical Spec Grid
        k_col1, k_col2 = st.columns(2)
        delta_t = sensors.get("process_temperature", 0.0) - sensors.get("air_temperature", 0.0)
        rpm = sensors.get("rotational_speed", 0)
        torque = sensors.get("torque", 0.0)
        shaft_power = (torque * (rpm * 2 * math.pi / 60)) / 1000.0 if rpm and torque else 0.0
        load_margin = max(0.0, 55.0 - torque)

        with k_col1:
            st.markdown(f"""
            <div class="card-panel">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.75rem;">
                    <span style="font-size:1.0rem;">🔥</span>
                    <h4 style="font-size:0.88rem; font-weight:600; text-transform:uppercase; color:var(--text-primary); margin:0;">
                        Operating Thermodynamics
                    </h4>
                </div>
                <div style="display:flex; flex-direction:column; gap:0.5rem; font-size:0.82rem;">
                    <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                        <span style="color:var(--text-muted);">Thermal Differential (ΔT)</span>
                        <strong class="mono" style="color:var(--text-primary);">{delta_t:.2f} K</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding:0.35rem 0;">
                        <span style="color:var(--text-muted);">Heat Dissipation Status</span>
                        <span class="badge-status {'badge-high' if delta_t > 12.0 else 'badge-normal'}">
                            {'CONSTRAINED' if delta_t > 12.0 else 'NOMINAL'}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with k_col2:
            st.markdown(f"""
            <div class="card-panel">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.75rem;">
                    <span style="font-size:1.0rem;">⚙️</span>
                    <h4 style="font-size:0.88rem; font-weight:600; text-transform:uppercase; color:var(--text-primary); margin:0;">
                        Mechanical Power & Torque
                    </h4>
                </div>
                <div style="display:flex; flex-direction:column; gap:0.5rem; font-size:0.82rem;">
                    <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                        <span style="color:var(--text-muted);">Estimated Shaft Power (P = τ × ω)</span>
                        <strong class="mono" style="color:var(--text-primary);">{shaft_power:.2f} kW</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding:0.35rem 0;">
                        <span style="color:var(--text-muted);">Torsional Load Margin</span>
                        <strong class="mono" style="color:{'var(--status-critical)' if torque > 55 else 'var(--text-primary)'};">
                            {load_margin:.1f} Nm to limit
                        </strong>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# TAB 3: DIAGNOSTICS & RAG MANUAL (DiagnosticsPage.jsx & RAGKnowledgePanel.jsx)
# ==============================================================================
with tab_diagnostics:
    st.markdown(f"""
    <div class="card-panel" style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.75rem; margin-bottom:1.25rem;">
        <div>
            <h2 style="font-size:1.15rem; font-weight:600; color:var(--text-primary); margin:0; display:flex; align-items:center; gap:0.5rem;">
                🩺 Machine Diagnostics & RAG Knowledge Manual
            </h2>
            <p style="font-size:0.78rem; color:var(--text-muted); margin:0.15rem 0 0 0;">
                Multi-tier heuristic evaluation correlated with dense FAISS vector maintenance database
            </p>
        </div>
        <div style="display:flex; gap:0.65rem; align-items:center;">
            <span class="badge-status {badge_cls}">
                {severity} SEVERITY
            </span>
            <span class="mono" style="font-size:0.82rem; color:var(--text-secondary); background-color:var(--bg-elevated); border:1px solid var(--border-normal); padding:0.2rem 0.55rem; border-radius:3px;">
                Risk: {failure_prob_pct}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if rag_items and len(rag_items) > 0:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <div style="font-size:0.95rem; font-weight:600; color:var(--text-primary); text-transform:uppercase; letter-spacing:0.04em;">
                Contextually Retrieved Maintenance Protocols ({len(rag_items)} Matched)
            </div>
            <div style="font-size:0.8rem; color:var(--text-muted); background:var(--bg-elevated); padding:0.2rem 0.55rem; border-radius:3px; border:1px solid var(--border-normal);">
                Embedding: all-MiniLM-L6-v2 (384-dim)
            </div>
        </div>
        """, unsafe_allow_html=True)

        for idx, item in enumerate(rag_items):
            topic = item.get("topic", f"Topic {idx+1}")
            cond = item.get("condition", "N/A")
            causes = item.get("possible_causes", [])
            actions = item.get("recommended_actions", [])
            steps = item.get("inspection_steps", [])

            causes_html = "".join([f"<li style='margin-bottom:0.35rem;'>{c}</li>" for c in causes])
            actions_html = "".join([f"<li style='margin-bottom:0.35rem;'>{a}</li>" for a in actions])
            steps_html = "".join([f"""
                <div style="display:flex; align-items:flex-start; gap:0.75rem; font-size:0.88rem; color:var(--text-secondary); margin-bottom:0.45rem;">
                    <span class="mono" style="background-color:var(--bg-panel); border:1px solid var(--border-normal); color:var(--text-primary); padding:0.15rem 0.5rem; border-radius:3px; font-size:0.78rem; font-weight:600; flex-shrink:0;">
                        {s_idx + 1}
                    </span>
                    <span style="line-height:1.5;">{s.replace(f'{s_idx+1}.', '').strip()}</span>
                </div>
            """ for s_idx, s in enumerate(steps)])

            st.markdown(f"""
            <div class="card-panel" style="margin-bottom:1.25rem; padding:1.35rem;">
                <div style="background-color:var(--bg-elevated); padding:0.65rem 1rem; border-radius:4px; border:1px solid var(--border-normal); display:flex; align-items:center; gap:0.65rem; margin-bottom:1rem;">
                    <span style="color:var(--status-high);">🛡️</span>
                    <span style="font-size:0.95rem; font-weight:700; color:var(--text-primary); letter-spacing:0.02em;">
                        TOPIC: {topic}
                    </span>
                </div>

                <div style="background-color:var(--bg-elevated); border-left:4px solid var(--accent); padding:0.85rem 1.15rem; border-radius:0 4px 4px 0; margin-bottom:1rem;">
                    <h4 style="font-size:0.82rem; font-weight:700; text-transform:uppercase; color:var(--accent); margin-bottom:0.35rem; letter-spacing:0.04em;">
                        Condition
                    </h4>
                    <p style="font-size:0.92rem; color:var(--text-primary); line-height:1.5; margin:0;">
                        {cond}
                    </p>
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;">
                    <div style="background-color:var(--bg-elevated); border:1px solid var(--border-normal); border-radius:4px; padding:1rem 1.15rem;">
                        <div style="color:var(--status-medium); font-size:0.85rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.65rem;">
                            ❓ Possible Root Causes
                        </div>
                        <ul style="margin:0; padding-left:1.25rem; font-size:0.88rem; color:var(--text-secondary); line-height:1.5;">
                            {causes_html}
                        </ul>
                    </div>

                    <div style="background-color:var(--bg-elevated); border:1px solid var(--border-normal); border-radius:4px; padding:1rem 1.15rem;">
                        <div style="color:var(--status-normal); font-size:0.85rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.65rem;">
                            🔧 Recommended Corrective Actions
                        </div>
                        <ul style="margin:0; padding-left:1.25rem; font-size:0.88rem; color:var(--text-secondary); line-height:1.5;">
                            {actions_html}
                        </ul>
                    </div>
                </div>

                <div style="background-color:var(--bg-elevated); border:1px solid var(--border-normal); border-radius:4px; padding:1rem 1.15rem;">
                    <div style="color:var(--accent); font-size:0.85rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.65rem;">
                        📋 Standard Operating Inspection Steps
                    </div>
                    {steps_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card-panel" style="padding:2.5rem; text-align:center; color:var(--text-muted);">
            <div style="font-size:1.8rem; margin-bottom:0.5rem;">📖</div>
            <h4 style="color:var(--text-primary); margin-bottom:0.25rem;">No Active Abnormal Condition</h4>
            <p style="font-size:0.85rem; max-width:480px; margin:0 auto;">
                When an anomaly or fault risk is identified, the FAISS vector index retrieves contextual repair instructions automatically.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Semantic Knowledge Base Search Drawer
    st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)
    with st.expander("🔍 Interactive FAISS Semantic Knowledge Base Search", expanded=False):
        search_q = st.text_input("Enter search query (e.g. 'bearing vibration', 'overheating', 'torque overload')", "")
        if search_q:
            results = search_knowledge(BACKEND_URL, search_q)
            if results:
                st.success(f"Found {len(results)} matching knowledge topics from dense vector index:")
                for r in results:
                    st.markdown(f"**Topic:** {r.get('topic')}")
                    st.markdown(f"*Condition:* {r.get('condition')}")
                    st.markdown("---")
            else:
                st.warning("No matching maintenance topics found.")

# ==============================================================================
# TAB 4: HISTORY & SENSOR TRENDS (SensorTrendsChart.jsx & TelemetryHistoryTable.jsx)
# ==============================================================================
with tab_history:
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.85rem;">
        <div>
            <h3 style="font-size:1.15rem; font-weight:600; color:var(--text-primary); margin:0;">
                Historical Sensor Trends & Telemetry
            </h3>
            <p style="font-size:0.82rem; color:var(--text-muted); margin:0.15rem 0 0 0;">
                Persistent historical records stored in PostgreSQL 16 database
            </p>
        </div>
        <div style="display:flex; align-items:center; gap:0.65rem;">
            <span class="mono" style="font-size:0.78rem; background:var(--bg-secondary); border:1px solid var(--border-normal); padding:0.25rem 0.65rem; border-radius:3px; color:var(--accent);">
                Storage: {db_stats.get('storage_engine', 'PostgreSQL 16') if db_stats else 'PostgreSQL 16'} ({db_stats.get('total_persisted_records', 0) if db_stats else 0} records)
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metric Selection Buttons
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        if st.button("Failure Risk (%)", use_container_width=True):
            st.session_state.trends_metric = "probability"
    with m_col2:
        if st.button("Temperatures (K)", use_container_width=True):
            st.session_state.trends_metric = "temperatures"
    with m_col3:
        if st.button("Rotational Speed (RPM)", use_container_width=True):
            st.session_state.trends_metric = "speed"
    with m_col4:
        if st.button("Torque (Nm)", use_container_width=True):
            st.session_state.trends_metric = "torque"
    with m_col5:
        if st.button("Tool Wear (min)", use_container_width=True):
            st.session_state.trends_metric = "wear"

    if history_records and len(history_records) >= 2:
        chrono_data = list(reversed(history_records))
        timestamps = [h.get("timestamp", "")[-8:] for h in chrono_data]

        fig = go.Figure()

        if st.session_state.trends_metric == "probability":
            probs = [(h.get("diagnosis", {}).get("failure_probability", 0.0) or 0.0) * 100 for h in chrono_data]
            fig.add_trace(go.Scatter(x=timestamps, y=probs, mode="lines+markers", name="Failure Risk %", line=dict(color="#B65353", width=2.5)))
            fig.add_hline(y=40, line_dash="dash", line_color="#C39A4A", annotation_text="Cutoff Limit (40%)", annotation_font_color="#C39A4A")

        elif st.session_state.trends_metric == "temperatures":
            proc_vals = [h.get("sensors", {}).get("process_temperature", 0.0) for h in chrono_data]
            air_vals = [h.get("sensors", {}).get("air_temperature", 0.0) for h in chrono_data]
            fig.add_trace(go.Scatter(x=timestamps, y=proc_vals, mode="lines+markers", name="Process Temp (K)", line=dict(color="#C8753D", width=2.5)))
            fig.add_trace(go.Scatter(x=timestamps, y=air_vals, mode="lines+markers", name="Air Temp (K)", line=dict(color="#5B7C99", width=2.5)))
            fig.add_hline(y=301, line_dash="dash", line_color="#C39A4A", annotation_text="Air Limit (301 K)")

        elif st.session_state.trends_metric == "speed":
            speeds = [h.get("sensors", {}).get("rotational_speed", 0) for h in chrono_data]
            fig.add_trace(go.Scatter(x=timestamps, y=speeds, mode="lines+markers", name="Rotational Speed (RPM)", line=dict(color="#6FA36F", width=2.5)))
            fig.add_hline(y=1300, line_dash="dash", line_color="#C39A4A", annotation_text="Lower Bound (1300 RPM)")

        elif st.session_state.trends_metric == "torque":
            torques = [h.get("sensors", {}).get("torque", 0.0) for h in chrono_data]
            fig.add_trace(go.Scatter(x=timestamps, y=torques, mode="lines+markers", name="Shaft Torque (Nm)", line=dict(color="#C39A4A", width=2.5)))
            fig.add_hline(y=55, line_dash="dash", line_color="#B65353", annotation_text="Upper Limit (55 Nm)")

        elif st.session_state.trends_metric == "wear":
            wears = [h.get("sensors", {}).get("tool_wear", 0) for h in chrono_data]
            fig.add_trace(go.Scatter(x=timestamps, y=wears, mode="lines+markers", name="Tool Wear (min)", line=dict(color="#A7ADB1", width=2.5)))
            fig.add_hline(y=100, line_dash="dash", line_color="#B65353", annotation_text="Wear Limit (100 min)")

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#181E29",
            plot_bgcolor="#181E29",
            margin=dict(l=40, r=40, t=30, b=40),
            height=250,
            font=dict(family="JetBrains Mono", size=11, color="#A7ADB1"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Accumulating live telemetry buffer for trend analysis...")

    st.markdown("<div style='height:1.25rem;'></div>", unsafe_allow_html=True)

    # Persistent PostgreSQL Telemetry History Table
    st.markdown("""
    <div style="font-size:0.95rem; font-weight:600; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.65rem;">
        Persistent Database Records (PostgreSQL 16)
    </div>
    """, unsafe_allow_html=True)

    # Filter Controls Bar
    fil_col1, fil_col2, fil_col3 = st.columns([1, 1, 2])
    with fil_col1:
        tbl_sev = st.selectbox("Severity Filter", ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"], index=0)
    with fil_col2:
        tbl_limit = st.selectbox("Display Limit", [25, 50, 100, 200], index=1)
    with fil_col3:
        tbl_search = st.text_input("Filter records by timestamp or condition", placeholder="Search records...")

    # Fetch with filters
    tbl_data = fetch_history(BACKEND_URL, st.session_state.active_machine, limit=tbl_limit, severity=tbl_sev)

    if tbl_data:
        rows = []
        for r in tbl_data:
            s = r.get("sensors", {})
            d = r.get("diagnosis", {})
            ts = r.get("timestamp", "")
            issues_txt = ", ".join(d.get("issues", []))

            if tbl_search and (tbl_search.lower() not in ts.lower() and tbl_search.lower() not in issues_txt.lower()):
                continue

            rows.append({
                "Timestamp": ts,
                "Machine": r.get("machine_id", "Machine 1"),
                "Type": s.get("type", "L"),
                "Air (K)": f"{s.get('air_temperature', 0.0):.1f}",
                "Proc (K)": f"{s.get('process_temperature', 0.0):.1f}",
                "Speed (RPM)": str(s.get("rotational_speed", 0)),
                "Torque (Nm)": f"{s.get('torque', 0.0):.1f}",
                "Wear (min)": str(s.get("tool_wear", 0)),
                "Failure Risk": d.get("failure_probability_pct", "0.00%"),
                "Status": d.get("status", "NORMAL"),
                "Severity": d.get("severity", "LOW")
            })

        df_display = pd.DataFrame(rows)
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=360)
    else:
        st.info("No records matching the filter criteria.")

# ==============================================================================
# TAB 5: SYSTEM ARCHITECTURE (SystemStatusPage.jsx)
# ==============================================================================
with tab_system:
    st.markdown("""
    <div class="card-panel" style="margin-bottom:1.25rem;">
        <h2 style="font-size:1.15rem; font-weight:600; margin:0; display:flex; align-items:center; gap:0.5rem; color:var(--text-primary);">
            🖥️ System Health & Diagnostic Architecture
        </h2>
        <p style="font-size:0.80rem; color:var(--text-muted); margin:0.25rem 0 0 0;">
            Broker telemetry status, ML model parameters, rule-engine thresholds, FAISS vector store, and persistent database telemetry
        </p>
    </div>
    """, unsafe_allow_html=True)

    arch_c1, arch_c2 = st.columns(2)

    with arch_c1:
        # Node 1: MQTT Ingestion
        st.markdown(f"""
        <div class="card-panel" style="margin-bottom:1.25rem;">
            <div style="font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:0.04em; color:var(--text-primary); border-bottom:1px solid var(--border-normal); padding-bottom:0.6rem; margin-bottom:0.75rem;">
                📡 IoT Telemetry Ingestion (MQTT)
            </div>
            <div style="display:flex; flex-direction:column; gap:0.65rem; font-size:0.82rem;">
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">MQTT Broker Endpoint</span>
                    <span class="mono" style="color:var(--text-primary);">127.0.0.1:1883</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Subscribed Topic</span>
                    <span class="mono" style="color:var(--text-primary);">factory/machine1/sensors</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Broker Status</span>
                    <span class="badge-status {'badge-normal' if mqtt_connected else 'badge-critical'}">
                        {'CONNECTED' if mqtt_connected else 'DISCONNECTED'}
                    </span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0;">
                    <span style="color:var(--text-muted);">Backend REST Status</span>
                    <span class="badge-status {'badge-normal' if backend_connected else 'badge-critical'}">
                        {'ACTIVE' if backend_connected else 'OFFLINE'}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Node 2: ML Model
        st.markdown("""
        <div class="card-panel" style="margin-bottom:1.25rem;">
            <div style="font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:0.04em; color:var(--text-primary); border-bottom:1px solid var(--border-normal); padding-bottom:0.6rem; margin-bottom:0.75rem;">
                🧠 Predictive ML Pipeline
            </div>
            <div style="display:flex; flex-direction:column; gap:0.65rem; font-size:0.82rem;">
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Classifier Architecture</span>
                    <span style="color:var(--text-primary); font-weight:500;">Gradient Boosting (n=150, d=3)</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Decision Cutoff Threshold</span>
                    <span class="mono" style="color:var(--status-medium); font-weight:600;">0.40 (40.0%)</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Training Dataset Origin</span>
                    <span style="color:var(--text-primary);">UCI AI4I 2020 Predictive Maint.</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0;">
                    <span style="color:var(--text-muted);">Model Artifact</span>
                    <span class="mono" style="color:var(--accent);">models/fault_model.pkl</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with arch_c2:
        # Node 3: PostgreSQL Database
        total_recs = db_stats.get("total_persisted_records", sys_status.get("database_records", 0)) if db_stats else 0
        storage_eng = db_stats.get("storage_engine", "PostgreSQL 16") if db_stats else "PostgreSQL 16"
        st.markdown(f"""
        <div class="card-panel" style="margin-bottom:1.25rem;">
            <div style="font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:0.04em; color:var(--text-primary); border-bottom:1px solid var(--border-normal); padding-bottom:0.6rem; margin-bottom:0.75rem;">
                🗄️ Persistent Relational Storage
            </div>
            <div style="display:flex; flex-direction:column; gap:0.65rem; font-size:0.82rem;">
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Storage Engine</span>
                    <span style="color:var(--text-primary); font-weight:500;">{storage_eng}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Total Persisted Records</span>
                    <span class="mono" style="color:var(--accent); font-weight:600;">{total_recs}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Target Asset</span>
                    <span class="mono" style="color:var(--text-primary);">{st.session_state.active_machine}</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0;">
                    <span style="color:var(--text-muted);">Infrastructure</span>
                    <span style="color:var(--status-normal); font-weight:500;">Docker PostgreSQL 16</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Node 4: FAISS Vector Architecture
        st.markdown("""
        <div class="card-panel" style="margin-bottom:1.25rem;">
            <div style="font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:0.04em; color:var(--text-primary); border-bottom:1px solid var(--border-normal); padding-bottom:0.6rem; margin-bottom:0.75rem;">
                📚 RAG Knowledge Architecture
            </div>
            <div style="display:flex; flex-direction:column; gap:0.65rem; font-size:0.82rem;">
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Vector Index Type</span>
                    <span style="color:var(--text-primary); font-weight:500;">FAISS IndexFlatL2</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Dense Embedding Model</span>
                    <span class="mono" style="color:var(--accent);">all-MiniLM-L6-v2 (384-dim)</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border-normal);">
                    <span style="color:var(--text-muted);">Vector Store File</span>
                    <span class="mono" style="color:var(--text-primary);">rag/maintenance.index</span>
                </div>
                <div style="display:flex; justify-content:space-between; padding:0.35rem 0;">
                    <span style="color:var(--text-muted);">Knowledge Manual</span>
                    <span class="mono" style="color:var(--text-secondary);">knowledge_base/maintenance_knowledge.txt</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# Industrial Console Footer (Matching React App.jsx footer)
# ==============================================================================
st.markdown("""
<div style="border-top:1px solid var(--border-normal); background-color:var(--bg-secondary); padding:1.1rem 1.5rem; font-size:0.82rem; color:var(--text-muted); display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.85rem; margin-top:2.5rem; border-radius:4px;">
    <div style="display:flex; align-items:center; gap:0.85rem;">
        <span style="font-weight:600; color:var(--text-primary);">P_311 Industrial Fault Diagnosis System</span>
        <span>•</span>
        <span class="mono">Topic: factory/machine1/sensors</span>
        <span>•</span>
        <span class="mono">FAISS Vector Index (384-dim)</span>
    </div>
    <div>
        <span>Stratified Gradient Boosting Classifier • Threshold: 0.40</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# Background Auto-Refresh Loop
# ==============================================================================
if not st.session_state.is_paused:
    time.sleep(2)
    st.rerun()
