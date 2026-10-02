#!/bin/bash
# ==============================================================================
# P_311 Industrial IoT Fault Diagnosis System — Stop Script
# ==============================================================================

echo "🛑 Stopping all running P_311 processes..."

# Stop Python simulator
pkill -f "ai4i_machine_simulator.py" 2>/dev/null && echo "  ✓ Stopped machine simulator"

# Stop Uvicorn backend
pkill -f "backend.main:app" 2>/dev/null && echo "  ✓ Stopped FastAPI backend"

# Stop Vite frontend dev server
pkill -f "vite --host 127.0.0.1 --port 5173" 2>/dev/null && echo "  ✓ Stopped Vite frontend"

# Check remaining port bindings
echo ""
echo "Checking ports:"
lsof -i :8000 > /dev/null 2>&1 && echo "  Port 8000 (FastAPI): occupied" || echo "  Port 8000 (FastAPI): free"
lsof -i :5173 > /dev/null 2>&1 && echo "  Port 5173 (React): occupied" || echo "  Port 5173 (React): free"
lsof -i :5432 > /dev/null 2>&1 && echo "  Port 5432 (PostgreSQL): active" || echo "  Port 5432 (PostgreSQL): stopped"

echo ""
echo "✅ Done."
