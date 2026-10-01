import asyncio
import json
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.schemas.models import (
    TelemetryRecord,
    SystemStatus,
    StructuredRAGTopic
)
from backend.mqtt_handler import mqtt_handler
from backend.services.rag_service import rag_service
from backend.database import (
    init_db,
    get_available_machines,
    get_database_stats
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQL database schema
    init_db()

    # Setup asyncio event loop on MQTT handler for websocket broadcasting
    loop = asyncio.get_running_loop()
    mqtt_handler.set_loop(loop)
    mqtt_handler.start()
    print("[FastAPI] Backend started, Database initialized, and MQTT handler active.")
    yield
    mqtt_handler.stop()
    print("[FastAPI] Backend stopped.")


app = FastAPI(
    title="P_311 IoT Fault Diagnosis API",
    description="Knowledge-Driven IoT Fault Diagnosis & Predictive Maintenance Backend with Database Storage",
    version="1.1.0",
    lifespan=lifespan
)

# Enable CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status", response_model=SystemStatus)
def get_system_status():
    """Returns connectivity, database persistence, and telemetry metrics."""
    return mqtt_handler.get_status()


@app.get("/api/latest")
def get_latest_telemetry(machine_id: Optional[str] = Query(None, description="Optional machine ID filter")):
    """
    Returns the latest real telemetry reading from disk/cache, or a waiting response if none received yet.
    """
    latest = mqtt_handler.get_latest(machine_id=machine_id)
    if latest is None:
        return JSONResponse(
            status_code=200,
            content={
                "waiting": True,
                "message": "Waiting for machine data...",
                "status": mqtt_handler.get_status().model_dump()
            }
        )
    return latest


@app.get("/api/latest/{machine_id}")
def get_latest_by_machine(machine_id: str = Path(..., description="Target machine ID, e.g. 'Machine 1'")):
    """Returns the latest telemetry reading specifically for the specified machine."""
    latest = mqtt_handler.get_latest(machine_id=machine_id)
    if latest is None:
        return JSONResponse(
            status_code=200,
            content={
                "waiting": True,
                "message": f"Waiting for data from {machine_id}...",
                "machine_id": machine_id
            }
        )
    return latest


@app.get("/api/history", response_model=List[TelemetryRecord])
def get_telemetry_history(
    machine_id: Optional[str] = Query(None, description="Filter by machine ID, e.g. 'Machine 1' or 'ALL'"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of historical records to return"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL, or ALL"),
    start_time: Optional[str] = Query(None, description="Start timestamp filter (YYYY-MM-DD HH:MM:SS)"),
    end_time: Optional[str] = Query(None, description="End timestamp filter (YYYY-MM-DD HH:MM:SS)")
):
    """
    Returns persistent historical telemetry stored in the database.
    Supports time-range, machine ID, and severity filtering.
    """
    return mqtt_handler.get_history(
        machine_id=machine_id,
        limit=limit,
        severity=severity,
        start_time=start_time,
        end_time=end_time
    )


@app.get("/api/history/{machine_id}", response_model=List[TelemetryRecord])
def get_history_by_machine(
    machine_id: str = Path(..., description="Machine ID to query, e.g. 'Machine 1'"),
    limit: int = Query(50, ge=1, le=1000),
    severity: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None)
):
    """Returns historical telemetry records specifically for the requested machine ID."""
    return mqtt_handler.get_history(
        machine_id=machine_id,
        limit=limit,
        severity=severity,
        start_time=start_time,
        end_time=end_time
    )


@app.get("/api/machines", response_model=List[str])
def get_machines_list():
    """Returns the list of all distinct machine IDs recorded in the database."""
    return get_available_machines()


@app.get("/api/database/stats")
def get_db_statistics():
    """Returns database persistence statistics and storage engine info."""
    return get_database_stats()


@app.get("/api/knowledge", response_model=List[StructuredRAGTopic])
def get_all_knowledge():
    """Returns all structured knowledge topics from the maintenance knowledge base."""
    return rag_service.get_all_topics()


@app.get("/api/knowledge/search", response_model=List[StructuredRAGTopic])
def search_knowledge(q: str = Query(..., min_length=2)):
    """Performs semantic vector search on maintenance knowledge."""
    return rag_service.search(q, k=3)


@app.post("/api/simulate")
def trigger_simulation(
    scenario: str = Query("NORMAL", description="Scenario: NORMAL, HIGH_TEMP, HIGH_TORQUE, HIGH_WEAR, CRITICAL"),
    machine_id: Optional[str] = Query("Machine 1", description="Target machine ID")
):
    """
    Convenience endpoint for live demonstrations: publishes realistic AI4I telemetry
    directly to the MQTT topic 'factory/machine1/sensors'.
    """
    import random
    from backend.mqtt_handler import TOPIC

    scenarios = {
        "NORMAL": {
            "type": "L",
            "air_temperature": round(298.5 + (0.5 - random.random()), 1),
            "process_temperature": round(308.7 + (0.5 - random.random()), 1),
            "rotational_speed": random.randint(1480, 1560),
            "torque": round(40.0 + random.uniform(0, 5), 1),
            "tool_wear": random.randint(20, 60)
        },
        "HIGH_TEMP": {
            "type": "M",
            "air_temperature": round(302.2 + random.uniform(0, 1.2), 1),
            "process_temperature": round(313.5 + random.uniform(0, 1.5), 1),
            "rotational_speed": random.randint(1400, 1520),
            "torque": round(44.0 + random.uniform(0, 5), 1),
            "tool_wear": random.randint(70, 110)
        },
        "HIGH_TORQUE": {
            "type": "H",
            "air_temperature": round(299.0 + random.uniform(0, 1), 1),
            "process_temperature": round(309.5 + random.uniform(0, 1), 1),
            "rotational_speed": random.randint(1200, 1280),
            "torque": round(62.0 + random.uniform(0, 8), 1),
            "tool_wear": random.randint(80, 120)
        },
        "HIGH_WEAR": {
            "type": "L",
            "air_temperature": round(299.5 + random.uniform(0, 1), 1),
            "process_temperature": round(309.8 + random.uniform(0, 1), 1),
            "rotational_speed": random.randint(1420, 1500),
            "torque": round(48.0 + random.uniform(0, 6), 1),
            "tool_wear": random.randint(165, 210)
        },
        "CRITICAL": {
            "type": "H",
            "air_temperature": round(303.0 + random.uniform(0, 1.5), 1),
            "process_temperature": round(314.5 + random.uniform(0, 1.5), 1),
            "rotational_speed": random.randint(1140, 1240),
            "torque": round(68.0 + random.uniform(0, 9), 1),
            "tool_wear": random.randint(175, 235)
        }
    }
    payload = scenarios.get(scenario.upper(), scenarios["NORMAL"])
    mqtt_handler.client.publish(TOPIC, json.dumps(payload))
    return {"published": True, "scenario": scenario.upper(), "machine_id": machine_id, "payload": payload}


@app.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    """
    Real-time push channel streaming live enriched telemetry directly to frontend clients.
    """
    await websocket.accept()
    queue = asyncio.Queue(maxsize=100)
    mqtt_handler.ws_subscribers.add(queue)

    try:
        # Immediately push the latest reading upon connection so UI isn't blank
        latest = mqtt_handler.get_latest()
        if latest:
            await websocket.send_json({
                "type": "telemetry",
                "data": latest.model_dump()
            })
        else:
            await websocket.send_json({
                "type": "waiting",
                "message": "Connected to telemetry pipeline. Awaiting machine frames..."
            })

        while True:
            # Wait for next live reading from MQTT handler
            data = await queue.get()
            await websocket.send_json({
                "type": "telemetry",
                "data": data
            })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WebSocket] Client error: {e}")
    finally:
        mqtt_handler.ws_subscribers.discard(queue)
