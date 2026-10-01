# P_311: Knowledge-Driven IoT Fault Diagnosis System

A professional, real-time industrial IoT monitoring & predictive maintenance SCADA workstation built on the **UCI AI4I 2020 Predictive Maintenance Dataset**.

---

## 🏗️ Architecture & Component Interconnections

```
   ┌──────────────────────────────────────────────┐
   │         IoT Telemetry Simulator              │
   │      (ai4i_machine_simulator.py)             │
   └──────────────────────┬───────────────────────┘
                          │ MQTT Publish (Topic: factory/machine1/sensors)
                          ▼
   ┌──────────────────────────────────────────────┐
   │             Mosquitto Broker                 │
   │               (Port 1883)                    │
   └──────────────────────┬───────────────────────┘
                          │ MQTT Subscribe
                          ▼
   ┌──────────────────────────────────────────────┐
   │             FastAPI Backend                  │
   │            (backend/main.py)                 │
   │                                              │
   │  ┌────────────────────────────────────────┐  │
   │  │ ML Classifier (models/fault_model.pkl) │  │ ──► Failure Probability (Threshold: 0.40)
   │  └────────────────────────────────────────┘  │
   │  ┌────────────────────────────────────────┐  │
   │  │ Rule Engine (diagnosis.py)             │  │ ──► Sensor Range Evaluations & Severity
   │  └────────────────────────────────────────┘  │
   │  ┌────────────────────────────────────────┐  │
   │  │ RAG Vector Engine (rag_service.py)     │  │ ──► FAISS Dense Retrieval (all-MiniLM-L6-v2)
   │  └────────────────────────────────────────┘  │
   └──────────────┬───────────────────────────────┘
                  │ WebSocket: /ws/telemetry
                  │ REST APIs: /api/latest, /api/history, /api/simulate
                  ▼
   ┌──────────────────────────────────────────────┐
   │            React SCADA Frontend              │
   │          (http://127.0.0.1:5173)             │
   │                                              │
   │  • Live Sensor Instrumentation Cards         │
   │  • Failure Risk Dial & Critical Threshold    │
   │  • 3D CAD Schematic / Digital Twin           │
   │  • Diagnostic Evaluation & Alarm Banners     │
   │  • FAISS RAG SOP Repair Procedures           │
   │  • Historical Telemetry & SCADA Event Logs   │
   └──────────────────────────────────────────────┘
```

---

## ⚡ Quickstart (One-Command Startup)

We provide an automated master script that verifies dependencies, starts MQTT, backend, frontend, and IoT simulator together:

```bash
# 1. Start all services
./start_all.sh

# 2. Open the dashboard in your browser
http://127.0.0.1:5173

# 3. Stop all services anytime
Press Ctrl+C or run ./stop_all.sh
```

---

## 🛠️ Step-by-Step Manual Run Instructions

If you prefer running each component in separate terminals:

### Terminal 1: MQTT Broker
Ensure Mosquitto is active on port 1883:
```bash
# On macOS:
brew services start mosquitto
# Or run directly:
mosquitto
```

### Terminal 2: FastAPI Backend
```bash
source venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
* **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **WebSocket Endpoint**: `ws://127.0.0.1:8000/ws/telemetry`

### Terminal 3: Vite SCADA Frontend
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
* **Frontend URL**: [http://127.0.0.1:5173](http://127.0.0.1:5173)

### Terminal 4: IoT Machine Simulator
```bash
source venv/bin/activate
python ai4i_machine_simulator.py
```
* Streams synthetic sensor packets (`air_temperature`, `process_temperature`, `rotational_speed`, `torque`, `tool_wear`) every 2 seconds to `factory/machine1/sensors`.

---

## 🧪 Simulation & Fault Testing

You can inject instant operational scenarios either via the **Simulation Controls** drawer in the dashboard (bottom-right button) or via curl:

```bash
# 1. Inject Critical Fault (High Heat & Overstrain)
curl -X POST "http://127.0.0.1:8000/api/simulate?scenario=CRITICAL"

# 2. Inject High Torque Load
curl -X POST "http://127.0.0.1:8000/api/simulate?scenario=HIGH"

# 3. Inject Overheating Warning
curl -X POST "http://127.0.0.1:8000/api/simulate?scenario=WARNING"

# 4. Restore Normal Operation
curl -X POST "http://127.0.0.1:8000/api/simulate?scenario=NORMAL"
```

---

## 📊 Core Files Reference

| Path | Purpose |
| :--- | :--- |
| [`start_all.sh`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/start_all.sh) | Master startup script that connects and launches all modules |
| [`stop_all.sh`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/stop_all.sh) | Cleanly shuts down all active background processes |
| [`backend/main.py`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/backend/main.py) | FastAPI application managing WebSockets, ring buffers, and REST endpoints |
| [`backend/mqtt_handler.py`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/backend/mqtt_handler.py) | MQTT broker subscriber and real-time dispatcher |
| [`backend/services/ml_service.py`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/backend/services/ml_service.py) | ML inference service wrapping `models/fault_model.pkl` |
| [`backend/services/diagnosis_service.py`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/backend/services/diagnosis_service.py) | Evaluates physical threshold boundaries using `diagnosis.py` |
| [`backend/services/rag_service.py`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/backend/services/rag_service.py) | FAISS dense vector retrieval over maintenance repair knowledge |
| [`diagnosis.py`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/diagnosis.py) | Rule-based engine computing machine state and recommendations |
| [`train_ai4i.py`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/train_ai4i.py) | Stratified Gradient Boosting classifier trainer |
| [`create_vector_db.py`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/create_vector_db.py) | Builds FAISS 384-dimensional vector database from SOP documentation |
| [`ai4i_machine_simulator.py`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/ai4i_machine_simulator.py) | Continuous IoT telemetry publisher |
| [`frontend/`](file:///Users/sambhavpachauri/p311-iot-fault-diagnosis/frontend) | React + Vite SCADA/HMI workstation interface |
