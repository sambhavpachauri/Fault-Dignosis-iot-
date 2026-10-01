from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SensorReading(BaseModel):
    type: str = Field(..., description="Machine type variant (L, M, H)")
    air_temperature: float = Field(..., description="Air temperature in Kelvin")
    process_temperature: float = Field(..., description="Process temperature in Kelvin")
    rotational_speed: int = Field(..., description="Rotational speed in RPM")
    torque: float = Field(..., description="Torque in Nm")
    tool_wear: int = Field(..., description="Tool wear in minutes")


class SensorThresholdEvaluation(BaseModel):
    name: str
    value: float
    unit: str
    normal_range: str
    is_normal: bool
    status_label: str  # "NORMAL", "HIGH", "LOW", "INCREASING"


class StructuredRAGTopic(BaseModel):
    topic: str
    condition: str
    possible_causes: List[str]
    inspection_steps: List[str]
    recommended_actions: List[str]
    raw_text: Optional[str] = None


class DiagnosticResult(BaseModel):
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    status: str    # "NORMAL", "FAULT RISK"
    failure_probability: float
    failure_probability_pct: str
    threshold: float
    issues: List[str]
    recommendation: str
    sensor_evaluations: Dict[str, SensorThresholdEvaluation]
    rag_knowledge: List[StructuredRAGTopic]


class TelemetryRecord(BaseModel):
    id: int
    timestamp: str
    machine_id: str
    sensors: SensorReading
    diagnosis: DiagnosticResult


class SystemStatus(BaseModel):
    mqtt_connected: bool
    backend_connected: bool
    last_data_received: Optional[str]
    active_machine: str
    total_readings_received: int
    buffer_count: int
    database_records: Optional[int] = 0
