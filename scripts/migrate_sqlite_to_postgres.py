#!/usr/bin/env python3
"""
P_311 Industrial IoT - Safe SQLite to PostgreSQL Migration Tool

Reads telemetry records from 'machine_data.db' in READ-ONLY mode and migrates
them to the PostgreSQL database. Does NOT delete or alter 'machine_data.db'.
Idempotent: will not create duplicate records if re-run.
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from sqlalchemy import create_engine, text
from backend.database import Base, TelemetryModel


def migrate(sqlite_path: str, postgres_url: str, batch_size: int = 200):
    print("=" * 70)
    print("  P_311 Telemetry Migration: SQLite -> PostgreSQL")
    print("=" * 70)

    if not os.path.exists(sqlite_path):
        print(f"❌ Error: SQLite database not found at '{sqlite_path}'")
        return False

    print(f"📂 Source SQLite DB : {sqlite_path} (READ-ONLY)")
    print(f"🐘 Target PostgreSQL: {postgres_url.split('@')[-1] if '@' in postgres_url else postgres_url}")
    print()

    # 1. Connect to SQLite in read-only mode
    try:
        sqlite_uri = f"file:{os.path.abspath(sqlite_path)}?mode=ro"
        sqlite_conn = sqlite3.connect(sqlite_uri, uri=True)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cur = sqlite_conn.cursor()

        sqlite_cur.execute("SELECT count(*) FROM telemetry_records")
        total_sqlite = sqlite_cur.fetchone()[0]
        print(f"🔍 Found {total_sqlite} records in SQLite 'telemetry_records' table.")
    except Exception as e:
        print(f"❌ Error reading SQLite database: {e}")
        return False

    if total_sqlite == 0:
        print("ℹ️ No records to migrate. Exiting.")
        sqlite_conn.close()
        return True

    # 2. Connect to PostgreSQL
    try:
        pg_engine = create_engine(postgres_url, pool_pre_ping=True)
        # Ensure tables exist
        Base.metadata.create_all(bind=pg_engine)
        print("✅ PostgreSQL table schema verified / created successfully.")
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        sqlite_conn.close()
        return False

    # 3. Check existing records in PostgreSQL to prevent duplication
    existing_timestamps = set()
    with pg_engine.connect() as conn:
        result = conn.execute(text("SELECT machine_id, timestamp FROM telemetry_records"))
        for row in result:
            existing_timestamps.add((row[0], row[1]))
    print(f"ℹ️ PostgreSQL currently has {len(existing_timestamps)} existing records.")

    # 4. Fetch all SQLite records
    sqlite_cur.execute("""
        SELECT 
            id, machine_id, timestamp, machine_type,
            air_temperature, process_temperature, rotational_speed, torque, tool_wear,
            failure_probability, failure_probability_pct, status, severity, threshold, recommendation,
            issues_json, sensor_evaluations_json, rag_knowledge_json
        FROM telemetry_records
        ORDER BY id ASC
    """)
    sqlite_rows = sqlite_cur.fetchall()

    # 5. Insert records in batches
    insert_sql = text("""
        INSERT INTO telemetry_records (
            id, machine_id, timestamp, machine_type,
            air_temperature, process_temperature, rotational_speed, torque, tool_wear,
            failure_probability, failure_probability_pct, status, severity, threshold, recommendation,
            issues_json, sensor_evaluations_json, rag_knowledge_json
        ) VALUES (
            :id, :machine_id, :timestamp, :machine_type,
            :air_temperature, :process_temperature, :rotational_speed, :torque, :tool_wear,
            :failure_probability, :failure_probability_pct, :status, :severity, :threshold, :recommendation,
            :issues_json, :sensor_evaluations_json, :rag_knowledge_json
        )
    """)

    migrated_count = 0
    skipped_count = 0

    batch = []
    with pg_engine.connect() as conn:
        for row in sqlite_rows:
            key = (row["machine_id"], row["timestamp"])
            if key in existing_timestamps:
                skipped_count += 1
                continue

            record_dict = {
                "id": row["id"],
                "machine_id": row["machine_id"],
                "timestamp": row["timestamp"],
                "machine_type": row["machine_type"],
                "air_temperature": float(row["air_temperature"]),
                "process_temperature": float(row["process_temperature"]),
                "rotational_speed": int(row["rotational_speed"]),
                "torque": float(row["torque"]),
                "tool_wear": int(row["tool_wear"]),
                "failure_probability": float(row["failure_probability"]),
                "failure_probability_pct": str(row["failure_probability_pct"]),
                "status": str(row["status"]),
                "severity": str(row["severity"]),
                "threshold": float(row["threshold"]),
                "recommendation": str(row["recommendation"]),
                "issues_json": str(row["issues_json"] or "[]"),
                "sensor_evaluations_json": str(row["sensor_evaluations_json"] or "{}"),
                "rag_knowledge_json": str(row["rag_knowledge_json"] or "[]"),
            }
            batch.append(record_dict)
            existing_timestamps.add(key)
            migrated_count += 1

            if len(batch) >= batch_size:
                conn.execute(insert_sql, batch)
                conn.commit()
                batch = []
                print(f"  ...migrated {migrated_count} records")

        if batch:
            conn.execute(insert_sql, batch)
            conn.commit()

        # 6. Synchronize sequence so future inserts autoincrement properly
        try:
            conn.execute(text("""
                SELECT setval(
                    pg_get_serial_sequence('telemetry_records', 'id'),
                    COALESCE(MAX(id), 1),
                    MAX(id) IS NOT NULL
                ) FROM telemetry_records;
            """))
            conn.commit()
            print("🔢 Synchronized PostgreSQL autoincrement ID sequence.")
        except Exception as se:
            print(f"⚠️ Sequence sync note: {se}")

    sqlite_conn.close()

    print()
    print("=" * 70)
    print("  ✅ MIGRATION SUMMARY")
    print("=" * 70)
    print(f"  Total records in SQLite : {total_sqlite}")
    print(f"  New records migrated    : {migrated_count}")
    print(f"  Records skipped (dup)   : {skipped_count}")
    print(f"  Final total in Postgres : {len(existing_timestamps)}")
    print(f"  SQLite file preserved   : {sqlite_path} (UNTOUCHED)")
    print("=" * 70)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate P_311 telemetry from SQLite to PostgreSQL")
    parser.add_argument("--sqlite-path", default=os.path.join(PROJECT_ROOT, "machine_data.db"), help="Path to machine_data.db")
    parser.add_argument(
        "--postgres-url",
        default=os.getenv("LOCAL_DATABASE_URL", os.getenv("DATABASE_URL", "postgresql+psycopg2://p311_user:p311_secure_pass_2026@127.0.0.1:5432/p311")),
        help="Target PostgreSQL connection string"
    )
    args = parser.parse_args()

    success = migrate(args.sqlite_path, args.postgres_url)
    sys.exit(0 if success else 1)
