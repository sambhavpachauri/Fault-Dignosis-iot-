import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    Text,
    Index,
    desc,
    event,
    text
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Configurable database URL: defaults to local SQLite, easily swapped to PostgreSQL via env var
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./machine_data.db")

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
    # Enable WAL (Write-Ahead Logging) mode in SQLite for high-concurrency read/write
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
else:
    # Production PostgreSQL connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TelemetryModel(Base):
    __tablename__ = "telemetry_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    machine_id = Column(String(64), nullable=False, default="Machine 1", index=True)
    timestamp = Column(String(32), nullable=False, index=True)
    
    # Machine variant type (L, M, H)
    machine_type = Column(String(8), nullable=False, default="M")
    
    # Raw Sensors
    air_temperature = Column(Float, nullable=False)
    process_temperature = Column(Float, nullable=False)
    rotational_speed = Column(Integer, nullable=False)
    torque = Column(Float, nullable=False)
    tool_wear = Column(Integer, nullable=False)

    # ML & Diagnosis
    failure_probability = Column(Float, nullable=False)
    failure_probability_pct = Column(String(16), nullable=False)
    status = Column(String(32), nullable=False)  # "NORMAL", "FAULT RISK"
    severity = Column(String(32), nullable=False)  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    threshold = Column(Float, nullable=False, default=0.40)
    recommendation = Column(Text, nullable=False)

    # Serialized JSON fields for structured evaluations
    issues_json = Column(Text, nullable=False, default="[]")
    sensor_evaluations_json = Column(Text, nullable=True, default="{}")
    rag_knowledge_json = Column(Text, nullable=True, default="[]")

    # Composite Index for efficient time-series queries per machine
    __table_args__ = (
        Index("ix_machine_timestamp", "machine_id", "timestamp"),
        Index("ix_machine_severity", "machine_id", "severity"),
    )


def sync_id_sequence():
    """Synchronizes PostgreSQL SERIAL sequence with max(id) if records exist."""
    if not is_sqlite:
        with engine.connect() as conn:
            try:
                conn.execute(text("SELECT setval(pg_get_serial_sequence('telemetry_records', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM telemetry_records;"))
                conn.commit()
            except Exception as e:
                # Table might be empty or sequence not yet initialized
                pass


def init_db():
    """Initializes the database schema if tables do not exist."""
    Base.metadata.create_all(bind=engine)
    sync_id_sequence()
    print(f"[Database] Initialized tables successfully on {DATABASE_URL.split('?')[0]}")


def save_telemetry_record(record_data: dict) -> int:
    """
    Persists a real telemetry and diagnostic record into the database.
    Accepts dictionary matching TelemetryRecord Pydantic model.
    """
    sensors = record_data.get("sensors", {})
    diagnosis = record_data.get("diagnosis", {})

    issues = diagnosis.get("issues", [])
    sensor_evals = diagnosis.get("sensor_evaluations", {})
    rag_items = diagnosis.get("rag_knowledge", [])

    db_item = TelemetryModel(
        machine_id=record_data.get("machine_id", "Machine 1"),
        timestamp=record_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        machine_type=str(sensors.get("type", "M")),
        air_temperature=float(sensors.get("air_temperature", 0.0)),
        process_temperature=float(sensors.get("process_temperature", 0.0)),
        rotational_speed=int(sensors.get("rotational_speed", 0)),
        torque=float(sensors.get("torque", 0.0)),
        tool_wear=int(sensors.get("tool_wear", 0)),
        failure_probability=float(diagnosis.get("failure_probability", 0.0)),
        failure_probability_pct=str(diagnosis.get("failure_probability_pct", "0.00%")),
        status=str(diagnosis.get("status", "NORMAL")),
        severity=str(diagnosis.get("severity", "LOW")),
        threshold=float(diagnosis.get("threshold", 0.40)),
        recommendation=str(diagnosis.get("recommendation", "")),
        issues_json=json.dumps(issues),
        sensor_evaluations_json=json.dumps(sensor_evals),
        rag_knowledge_json=json.dumps(rag_items)
    )

    session: Session = SessionLocal()
    try:
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item.id
    except Exception as e:
        session.rollback()
        print(f"[Database] Error saving telemetry record: {e}")
        raise e
    finally:
        session.close()


def row_to_telemetry_dict(row: TelemetryModel) -> dict:
    """Converts a SQLAlchemy TelemetryModel row into the standard TelemetryRecord dict format."""
    try:
        issues = json.loads(row.issues_json) if row.issues_json else []
    except Exception:
        issues = []

    try:
        sensor_evals = json.loads(row.sensor_evaluations_json) if row.sensor_evaluations_json else {}
    except Exception:
        sensor_evals = {}

    try:
        rag_knowledge = json.loads(row.rag_knowledge_json) if row.rag_knowledge_json else []
    except Exception:
        rag_knowledge = []

    return {
        "id": row.id,
        "timestamp": row.timestamp,
        "machine_id": row.machine_id,
        "sensors": {
            "type": row.machine_type,
            "air_temperature": row.air_temperature,
            "process_temperature": row.process_temperature,
            "rotational_speed": row.rotational_speed,
            "torque": row.torque,
            "tool_wear": row.tool_wear
        },
        "diagnosis": {
            "severity": row.severity,
            "status": row.status,
            "failure_probability": row.failure_probability,
            "failure_probability_pct": row.failure_probability_pct,
            "threshold": row.threshold,
            "issues": issues,
            "recommendation": row.recommendation,
            "sensor_evaluations": sensor_evals,
            "rag_knowledge": rag_knowledge
        }
    }


def get_telemetry_history(
    machine_id: Optional[str] = None,
    limit: int = 50,
    severity: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> List[dict]:
    """
    Fetches historical telemetry from the database with filtering options.
    Returns newest first.
    """
    session: Session = SessionLocal()
    try:
        query = session.query(TelemetryModel)

        if machine_id and machine_id.upper() != "ALL":
            query = query.filter(TelemetryModel.machine_id == machine_id)

        if severity and severity.upper() != "ALL":
            query = query.filter(TelemetryModel.severity == severity.upper())

        if start_time:
            query = query.filter(TelemetryModel.timestamp >= start_time)

        if end_time:
            query = query.filter(TelemetryModel.timestamp <= end_time)

        records = query.order_by(desc(TelemetryModel.timestamp), desc(TelemetryModel.id)).limit(limit).all()
        return [row_to_telemetry_dict(r) for r in records]
    finally:
        session.close()


def get_latest_telemetry(machine_id: Optional[str] = "Machine 1") -> Optional[dict]:
    """Fetches the latest single record for a given machine from the database."""
    session: Session = SessionLocal()
    try:
        query = session.query(TelemetryModel)
        if machine_id:
            query = query.filter(TelemetryModel.machine_id == machine_id)
        latest_row = query.order_by(desc(TelemetryModel.timestamp), desc(TelemetryModel.id)).first()
        return row_to_telemetry_dict(latest_row) if latest_row else None
    finally:
        session.close()


def get_available_machines() -> List[str]:
    """Returns a list of all distinct machine IDs in the database."""
    session: Session = SessionLocal()
    try:
        rows = session.query(TelemetryModel.machine_id).distinct().all()
        machines = [r[0] for r in rows if r[0]]
        if not machines:
            return ["Machine 1"]
        if "Machine 1" not in machines:
            machines.insert(0, "Machine 1")
        return machines
    finally:
        session.close()


def get_database_stats() -> Dict[str, Any]:
    """Returns summary statistics of persisted telemetry data."""
    session: Session = SessionLocal()
    try:
        total = session.query(TelemetryModel).count()
        machines = session.query(TelemetryModel.machine_id).distinct().count()
        return {
            "total_persisted_records": total,
            "distinct_machines": machines,
            "storage_engine": "SQLite (WAL)" if is_sqlite else "PostgreSQL"
        }
    finally:
        session.close()
