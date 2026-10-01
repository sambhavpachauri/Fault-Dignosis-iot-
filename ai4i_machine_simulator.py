import paho.mqtt.client as mqtt
import json
import random
import time

# --------------------------------------------------
# MQTT Configuration
# --------------------------------------------------

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "factory/machine1/sensors"

# --------------------------------------------------
# Connect to MQTT broker
# --------------------------------------------------

client = mqtt.Client()
client.connect(BROKER, PORT)

print("AI4I Machine Simulator Started...")
print("Publishing sensor data to MQTT...\n")

# --------------------------------------------------
# Generate machine data
# --------------------------------------------------

while True:

    # 80% normal operation
    if random.random() < 0.80:

        sensor_data = {
            "type": random.choice(["L", "M", "H"]),
            "air_temperature": round(random.uniform(298.0, 300.0), 1),
            "process_temperature": round(random.uniform(308.0, 310.0), 1),
            "rotational_speed": random.randint(1400, 1600),
            "torque": round(random.uniform(35.0, 50.0), 1),
            "tool_wear": random.randint(0, 100)
        }

    # 20% abnormal operation
    else:

        sensor_data = {
            "type": random.choice(["L", "M", "H"]),
            "air_temperature": round(random.uniform(300.0, 303.0), 1),
            "process_temperature": round(random.uniform(311.0, 315.0), 1),
            "rotational_speed": random.randint(1100, 1350),
            "torque": round(random.uniform(50.0, 70.0), 1),
            "tool_wear": random.randint(100, 250)
        }

    # Convert dictionary to JSON
    message = json.dumps(sensor_data)

    # Publish to MQTT
    client.publish(TOPIC, message)

    print("📡 Published:")
    print(sensor_data)
    print()

    time.sleep(2)
