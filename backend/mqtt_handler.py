import json
import os
import asyncio
from datetime import datetime
from collections import deque
from typing import Optional, Set, List
import paho.mqtt.client as mqtt

from backend.schemas.models import (
    SensorReading,
    DiagnosticResult,
    TelemetryRecord,
    SystemStatus
)
from backend.services.ml_service import ml_service
from backend.services.diagnosis_service import run_diagnosis
from backend.services.rag_service import rag_service
from backend.database import (
    save_telemetry_record,
    get_telemetry_history,
    get_latest_telemetry,
    get_database_stats
)

BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC = os.getenv("MQTT_TOPIC", "factory/machine1/sensors")


class MQTTTelemetryHandler:
    def __init__(self, max_history: int = 200):
        self.max_history = max_history
        self.history: deque[TelemetryRecord] = deque(maxlen=max_history)
        self.latest_record: Optional[TelemetryRecord] = None
        self.counter = 0
        self.total_received = 0
        self.last_received_time: Optional[str] = None
        self.is_connected = False
        self.active_machine = "Machine 1"
        
        # Asyncio event loop & websocket client subscribers
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.ws_subscribers: Set[asyncio.Queue] = set()

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.is_connected = True
            print(f"[MQTT] Connected successfully to {BROKER}:{PORT}")
            self.client.subscribe(TOPIC)
            print(f"[MQTT] Subscribed to topic: {TOPIC}")
        else:
            self.is_connected = False
            print(f"[MQTT] Connection failed with code: {reason_code}")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.is_connected = False
        print(f"[MQTT] Disconnected (reason: {reason_code})")

    def on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode()
            data = json.loads(payload_str)

            # 1. ML Failure prediction
            failure_prob, status = ml_service.predict(data)

            # 2. Heuristic & Threshold Diagnosis
            diag_output = run_diagnosis(data, failure_prob)

            # 3. RAG Maintenance Retrieval
            rag_knowledge = []
            seen_topics = set()
            for issue in diag_output["issues"]:
                if issue != "No major abnormal sensor condition detected":
                    matched_topics = rag_service.search(issue, k=1)
                    for item in matched_topics:
                        if item.topic not in seen_topics:
                            seen_topics.add(item.topic)
                            rag_knowledge.append(item)

            # If failure probability is high or critical but no specific sensor bounds triggered, retrieve general risk topic
            if not rag_knowledge and diag_output["severity"] in ["HIGH", "CRITICAL"]:
                matched_topics = rag_service.search("Machine failure risk", k=1)
                for item in matched_topics:
                    if item.topic not in seen_topics:
                        seen_topics.add(item.topic)
                        rag_knowledge.append(item)

            self.counter += 1
            self.total_received += 1
            now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_received_time = now_iso

            diagnostic_result = DiagnosticResult(
                severity=diag_output["severity"],
                status=status,
                failure_probability=round(failure_prob, 4),
                failure_probability_pct=f"{failure_prob * 100:.2f}%",
                threshold=ml_service.threshold,
                issues=diag_output["issues"],
                recommendation=diag_output["recommendation"],
                sensor_evaluations=diag_output["sensor_evaluations"],
                rag_knowledge=rag_knowledge
            )

            sensor_reading = SensorReading(
                type=str(data.get("type", "M")),
                air_temperature=float(data["air_temperature"]),
                process_temperature=float(data["process_temperature"]),
                rotational_speed=int(data["rotational_speed"]),
                torque=float(data["torque"]),
                tool_wear=int(data["tool_wear"])
            )

            record = TelemetryRecord(
                id=self.counter,
                timestamp=now_iso,
                machine_id=self.active_machine,
                sensors=sensor_reading,
                diagnosis=diagnostic_result
            )

            # 4. Save to Persistent Database
            try:
                db_id = save_telemetry_record(record.model_dump())
                record.id = db_id
            except Exception as dbe:
                print(f"[Database] Warning: Failed to persist record: {dbe}")

            self.latest_record = record
            self.history.append(record)

            # 5. Broadcast to WebSocket subscribers
            if self.loop and self.loop.is_running():
                data_dict = record.model_dump()
                for queue in list(self.ws_subscribers):
                    self.loop.call_soon_threadsafe(queue.put_nowait, data_dict)

        except Exception as e:
            print(f"[MQTT] Error handling telemetry message: {e}")

    def start(self):
        try:
            print(f"[MQTT] Attempting connection to {BROKER}:{PORT}...")
            self.client.connect(BROKER, PORT, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT] Warning: Could not connect to broker at startup: {e}")

    def stop(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
            print("[MQTT] Client stopped.")
        except Exception as e:
            print(f"[MQTT] Stop error: {e}")

    def get_status(self) -> SystemStatus:
        db_records_count = 0
        try:
            stats = get_database_stats()
            db_records_count = stats.get("total_persisted_records", 0)
        except Exception:
            pass

        return SystemStatus(
            mqtt_connected=self.is_connected,
            backend_connected=True,
            last_data_received=self.last_received_time,
            active_machine=self.active_machine,
            total_readings_received=self.total_received,
            buffer_count=len(self.history),
            database_records=db_records_count
        )

    def get_latest(self, machine_id: Optional[str] = None) -> Optional[TelemetryRecord]:
        m_id = machine_id if machine_id else self.active_machine
        if self.latest_record and self.latest_record.machine_id == m_id:
            return self.latest_record
        
        # Fall back to database query if in-memory is empty
        try:
            latest_dict = get_latest_telemetry(m_id)
            if latest_dict:
                return TelemetryRecord(**latest_dict)
        except Exception as e:
            print(f"[Database] Error retrieving latest telemetry: {e}")

        return self.latest_record

    def get_history(
        self,
        machine_id: Optional[str] = None,
        limit: int = 50,
        severity: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[TelemetryRecord]:
        """
        Retrieves real historical telemetry from the persistent database.
        Falls back to in-memory buffer if database is empty.
        """
        try:
            m_id = machine_id if machine_id else self.active_machine
            db_records = get_telemetry_history(
                machine_id=m_id,
                limit=limit,
                severity=severity,
                start_time=start_time,
                end_time=end_time
            )
            if db_records:
                return [TelemetryRecord(**r) for r in db_records]
        except Exception as e:
            print(f"[Database] Query failed, falling back to in-memory: {e}")

        # In-memory fallback
        items = list(self.history)
        if severity and severity.upper() != "ALL":
            items = [item for item in items if item.diagnosis.severity.upper() == severity.upper()]
        items.reverse()
        return items[:limit]


mqtt_handler = MQTTTelemetryHandler()
