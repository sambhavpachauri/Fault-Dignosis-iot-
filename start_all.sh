#!/bin/bash
# ==============================================================================
# P_311 Industrial IoT Fault Diagnosis System — Master Startup Script
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=================================================================="
echo "  P_311 Industrial IoT Fault Diagnosis System"
echo "  Knowledge-Driven Predictive Maintenance & SCADA Workstation"
echo "=================================================================="
echo ""

# 1. Check Python Virtual Environment
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment 'venv' not found."
    echo "   Please create it: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

PYTHON_BIN="$PROJECT_DIR/venv/bin/python"
UVICORN_BIN="$PROJECT_DIR/venv/bin/uvicorn"

# Load .env if present
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 2. Check Database Engine (PostgreSQL / Docker / SQLite)
echo "🔍 [1/5] Checking Database Engine..."
if command -v docker > /dev/null 2>&1 && docker info > /dev/null 2>&1; then
    if docker compose ps --services --filter "status=running" 2>/dev/null | grep postgres > /dev/null; then
        echo "    ✅ PostgreSQL container is healthy in Docker."
        export DATABASE_URL="${LOCAL_DATABASE_URL:-postgresql+psycopg2://p311_user:p311_secure_pass_2026@127.0.0.1:5432/p311}"
    elif [ -f "docker-compose.yml" ]; then
        echo "    🚀 Launching PostgreSQL via Docker Compose..."
        docker compose up -d postgres
        sleep 2
        export DATABASE_URL="${LOCAL_DATABASE_URL:-postgresql+psycopg2://p311_user:p311_secure_pass_2026@127.0.0.1:5432/p311}"
    fi
elif lsof -i :5432 > /dev/null 2>&1; then
    echo "    ✅ PostgreSQL is running on 127.0.0.1:5432."
    export DATABASE_URL="${LOCAL_DATABASE_URL:-postgresql+psycopg2://p311_user:p311_secure_pass_2026@127.0.0.1:5432/p311}"
else
    echo "    ℹ️ PostgreSQL not active on port 5432. Falling back to persistent SQLite (machine_data.db)."
    export DATABASE_URL="sqlite:///./machine_data.db"
fi

# 3. Check MQTT Broker (Port 1883)
echo "🔍 [2/5] Checking MQTT Broker on 127.0.0.1:1883..."
if lsof -i :1883 > /dev/null 2>&1; then
    echo "    ✅ MQTT broker is running."
else
    echo "    ⚠️ MQTT broker is not running on port 1883."
    if command -v brew > /dev/null 2>&1 && brew services list | grep mosquitto > /dev/null 2>&1; then
        echo "    🚀 Starting Mosquitto via brew services..."
        brew services start mosquitto
        sleep 1
    elif command -v mosquitto > /dev/null 2>&1; then
        echo "    🚀 Launching mosquitto in background..."
        mosquitto -d
        sleep 1
    else
        echo "    ⚠️ Warning: Could not auto-start Mosquitto. Please start your MQTT broker on port 1883."
    fi
fi

# 3. Check ML Model & RAG Vector DB Artifacts
echo "🔍 [3/5] Verifying ML model and RAG vector store..."
if [ ! -f "models/fault_model.pkl" ]; then
    echo "    ⚠️ 'models/fault_model.pkl' not found. Training model..."
    "$PYTHON_BIN" train_ai4i.py
fi

if [ ! -f "rag/maintenance.index" ]; then
    echo "    ⚠️ 'rag/maintenance.index' not found. Building FAISS index..."
    "$PYTHON_BIN" create_vector_db.py
fi
echo "    ✅ Model and vector index verified."

# 5. Cleanup function on Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Shutting down P_311 services..."
    if [ -n "$SIM_PID" ]; then kill "$SIM_PID" 2>/dev/null; fi
    if [ -n "$STREAMLIT_PID" ]; then kill "$STREAMLIT_PID" 2>/dev/null; fi
    if [ -n "$FRONT_PID" ]; then kill "$FRONT_PID" 2>/dev/null; fi
    if [ -n "$BACK_PID" ]; then kill "$BACK_PID" 2>/dev/null; fi
    echo "✅ All services stopped."
    exit 0
}
trap cleanup SIGINT SIGTERM

# 6. Start FastAPI Backend (Port 8000)
echo "🚀 [4/6] Starting FastAPI Backend on port 8000..."
"$UVICORN_BIN" backend.main:app --host 127.0.0.1 --port 8000 > /dev/null 2>&1 &
BACK_PID=$!
sleep 2

# 7. Start Vite React Frontend (Port 5173)
echo "🚀 [5/6] Starting Vite SCADA Frontend on port 5173..."
cd "$PROJECT_DIR/frontend"
npm run dev -- --host 127.0.0.1 --port 5173 > /dev/null 2>&1 &
FRONT_PID=$!
cd "$PROJECT_DIR"
sleep 2

# 8. Start Streamlit App (Port 8501)
echo "🚀 [6/6] Starting Streamlit Application on port 8501..."
"$PROJECT_DIR/venv/bin/streamlit" run streamlit_app.py --server.port 8501 --server.headless true > /dev/null 2>&1 &
STREAMLIT_PID=$!
sleep 2

# 9. Start IoT Machine Telemetry Simulator
echo "📡 Launching IoT Machine Sensor Simulator (Publishing to factory/machine1/sensors)..."
"$PYTHON_BIN" ai4i_machine_simulator.py &
SIM_PID=$!

echo ""
echo "=================================================================="
echo "  ✅ SYSTEM FULLY OPERATIONAL & CONNECTED"
echo "=================================================================="
echo "  🖥️  SCADA Dashboard : http://127.0.0.1:5173"
echo "  📊 Streamlit Portal : http://127.0.0.1:8501"
echo "  🔌 Backend API Docs : http://127.0.0.1:8000/docs"
echo "  🐘 Database Storage : $DATABASE_URL"
echo "  📡 MQTT Stream Topic: factory/machine1/sensors (127.0.0.1:1883)"
echo "  🤖 ML Model Status  : Gradient Boosting (Threshold: 0.40)"
echo "  📚 RAG Vector Store : FAISS Index (all-MiniLM-L6-v2)"
echo "=================================================================="
echo "  Press Ctrl+C to stop all services."
echo ""

# Keep running
wait
