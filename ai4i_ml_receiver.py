import paho.mqtt.client as mqtt
import json
import joblib
import pandas as pd
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from datetime import datetime

from diagnosis import diagnose_machine


# --------------------------------------------------
# MQTT Configuration
# --------------------------------------------------

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "factory/machine1/sensors"


# --------------------------------------------------
# Load trained ML model
# --------------------------------------------------

model_data = joblib.load("models/fault_model.pkl")

model = model_data["model"]
features = model_data["features"]
threshold = model_data["threshold"]

print("ML model loaded successfully!")
print(f"Failure threshold: {threshold}")
print(f"Expected features: {features}")


# --------------------------------------------------
# Load RAG knowledge base
# --------------------------------------------------

rag_index = faiss.read_index("rag/maintenance.index")

with open("rag/documents.pkl", "rb") as file:
    rag_documents = pickle.load(file)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("RAG knowledge base loaded successfully!")
print(f"Knowledge chunks available: {len(rag_documents)}")


# --------------------------------------------------
# RAG search function
# --------------------------------------------------

def search_maintenance_knowledge(query, k=1):

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )

    distances, indices = rag_index.search(
        query_embedding,
        k=k
    )

    results = []

    for index_number in indices[0]:
        results.append(rag_documents[index_number])

    return results


# --------------------------------------------------
# MQTT connection
# --------------------------------------------------

def on_connect(client, userdata, flags, reason_code, properties):

    if reason_code == 0:
        print("\nConnected to MQTT broker")
        client.subscribe(TOPIC)
        print(f"Subscribed to: {TOPIC}\n")

    else:
        print("MQTT connection failed")


# --------------------------------------------------
# Receive sensor data
# --------------------------------------------------

def on_message(client, userdata, msg):

    try:

        data = json.loads(msg.payload.decode())

        input_data = pd.DataFrame([{
            "Air temperature [K]": data["air_temperature"],
            "Process temperature [K]": data["process_temperature"],
            "Rotational speed [rpm]": data["rotational_speed"],
            "Torque [Nm]": data["torque"],
            "Tool wear [min]": data["tool_wear"],
            "Type_H": 1 if data["type"] == "H" else 0,
            "Type_L": 1 if data["type"] == "L" else 0,
            "Type_M": 1 if data["type"] == "M" else 0
        }])

        input_data = input_data[features]

        # ML prediction
        failure_probability = model.predict_proba(input_data)[0][1]

        # Apply threshold
        if failure_probability >= threshold:
            status = "FAULT RISK"
        else:
            status = "NORMAL"

        # Diagnosis
        diagnosis = diagnose_machine(
            data,
            failure_probability
        )

        # --------------------------------------------------
        # Retrieve maintenance knowledge
        # --------------------------------------------------

        rag_results = []

        for issue in diagnosis["issues"]:

            if issue != "No major abnormal sensor condition detected":

                results = search_maintenance_knowledge(
                    issue,
                    k=1
                )

                rag_results.extend(results)


        # --------------------------------------------------
        # Display result
        # --------------------------------------------------

        print("=" * 55)

        print(
            f"Time                : "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )

        print(f"Machine Type        : {data['type']}")
        print(f"Air Temperature     : {data['air_temperature']} K")
        print(f"Process Temperature : {data['process_temperature']} K")
        print(f"Rotational Speed    : {data['rotational_speed']} RPM")
        print(f"Torque              : {data['torque']} Nm")
        print(f"Tool Wear           : {data['tool_wear']} min")

        print("-" * 55)

        print(
            f"Failure Probability : "
            f"{failure_probability:.2%}"
        )

        print(f"Machine Status      : {status}")
        print(f"Severity            : {diagnosis['severity']}")

        print("\nPossible contributing conditions:")

        for issue in diagnosis["issues"]:
            print(f"  → {issue}")

        print("\nRecommended Action:")
        print(f"  → {diagnosis['recommendation']}")

        # --------------------------------------------------
        # Display RAG knowledge
        # --------------------------------------------------
        if rag_results:
            print("\nRelevant Maintenance Knowledge:")
            for rank, result in enumerate(rag_results, start=1):
                print(f"\n--- Knowledge Result {rank} ---")
                print(result)
        else:
            print("\nRelevant Maintenance Knowledge:")
            print("  → No specific maintenance knowledge retrieved.")

        print("=" * 55)

    except Exception as e:

        print("Error processing sensor data:")
        print(e)


# --------------------------------------------------
# Start MQTT client
# --------------------------------------------------

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)

print("Starting ML-powered IoT receiver...")

client.loop_forever()
