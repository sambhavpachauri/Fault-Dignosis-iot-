import paho.mqtt.client as mqtt
import json
import sqlite3
from datetime import datetime

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "factory/machine1/sensors"


# Create database
connection = sqlite3.connect("machine_data.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    temperature REAL,
    vibration REAL,
    current REAL,
    rpm INTEGER,
    status TEXT,
    faults TEXT
)
""")

connection.commit()


def check_fault(data):
    faults = []

    if data["temperature"] > 80:
        faults.append("High Temperature")

    if data["vibration"] > 3.5:
        faults.append("High Vibration")

    if data["current"] > 10:
        faults.append("High Current")

    if data["rpm"] < 1400 or data["rpm"] > 1500:
        faults.append("Abnormal RPM")

    return faults


def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to MQTT broker")
    client.subscribe(TOPIC)
    print(f"Subscribed to: {TOPIC}")


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    faults = check_fault(data)

    if faults:
        status = "FAULT"
        fault_text = ", ".join(faults)
    else:
        status = "NORMAL"
        fault_text = "None"

    # Save data to database
    cursor.execute("""
    INSERT INTO sensor_readings
    (timestamp, temperature, vibration, current, rpm, status, faults)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data["temperature"],
        data["vibration"],
        data["current"],
        data["rpm"],
        status,
        fault_text
    ))

    connection.commit()

    # Display data
    print("\n📡 New sensor reading")
    print(f"Temperature : {data['temperature']} °C")
    print(f"Vibration   : {data['vibration']} mm/s")
    print(f"Current     : {data['current']} A")
    print(f"RPM         : {data['rpm']}")

    if faults:
        print("⚠️ MACHINE FAULT DETECTED!")
        for fault in faults:
            print(f"   → {fault}")
    else:
        print("✅ Machine Status: NORMAL")

    print("💾 Data saved to database")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)

client.loop_forever()
