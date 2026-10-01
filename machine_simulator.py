import paho.mqtt.client as mqtt
import json
import random
import time

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "factory/machine1/sensors"

client = mqtt.Client()
client.connect(BROKER, PORT)

print("Machine Simulator Started...")
print("Sending sensor data...\n")

while True:

    # 80% chance of normal condition
    if random.random() < 0.8:

        sensor_data = {
            "temperature": round(random.uniform(65, 75), 2),
            "vibration": round(random.uniform(1.5, 3.0), 2),
            "current": round(random.uniform(7, 10), 2),
            "rpm": random.randint(1400, 1500)
        }

    # 20% chance of faulty condition
    else:

        sensor_data = {
            "temperature": round(random.uniform(82, 95), 2),
            "vibration": round(random.uniform(4.0, 6.0), 2),
            "current": round(random.uniform(11, 14), 2),
            "rpm": random.randint(1250, 1380)
        }

    message = json.dumps(sensor_data)

    client.publish(TOPIC, message)

    print(sensor_data)

    time.sleep(2)
