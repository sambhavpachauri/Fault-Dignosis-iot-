import random
import pandas as pd

data = []

# -----------------------------
# 1. NORMAL MACHINE CONDITIONS
# -----------------------------
for _ in range(500):
    temperature = random.uniform(65, 78)
    vibration = random.uniform(1.5, 3.2)
    current = random.uniform(7, 10)
    rpm = random.uniform(1400, 1500)

    data.append([
        temperature,
        vibration,
        current,
        rpm,
        "NORMAL"
    ])


# -----------------------------
# 2. OVERHEATING
# -----------------------------
for _ in range(150):
    temperature = random.uniform(80, 95)
    vibration = random.uniform(2.0, 3.5)
    current = random.uniform(7, 10.5)
    rpm = random.uniform(1380, 1500)

    data.append([
        temperature,
        vibration,
        current,
        rpm,
        "OVERHEATING"
    ])


# -----------------------------
# 3. BEARING / VIBRATION FAULT
# -----------------------------
for _ in range(150):
    temperature = random.uniform(72, 85)
    vibration = random.uniform(3.5, 6.0)
    current = random.uniform(7, 11)
    rpm = random.uniform(1350, 1480)

    data.append([
        temperature,
        vibration,
        current,
        rpm,
        "VIBRATION_FAULT"
    ])


# -----------------------------
# 4. OVERCURRENT
# -----------------------------
for _ in range(100):
    temperature = random.uniform(72, 85)
    vibration = random.uniform(2.0, 3.5)
    current = random.uniform(10.5, 14)
    rpm = random.uniform(1300, 1480)

    data.append([
        temperature,
        vibration,
        current,
        rpm,
        "OVERCURRENT"
    ])


# -----------------------------
# 5. RPM / MOTOR FAULT
# -----------------------------
for _ in range(100):
    temperature = random.uniform(70, 85)
    vibration = random.uniform(2.0, 4.5)
    current = random.uniform(8, 12)
    rpm = random.uniform(1200, 1390)

    data.append([
        temperature,
        vibration,
        current,
        rpm,
        "RPM_FAULT"
    ])


# -----------------------------
# 6. MULTIPLE / SEVERE FAULT
# -----------------------------
for _ in range(100):
    temperature = random.uniform(85, 100)
    vibration = random.uniform(4.0, 7.0)
    current = random.uniform(11, 15)
    rpm = random.uniform(1150, 1350)

    data.append([
        temperature,
        vibration,
        current,
        rpm,
        "CRITICAL_FAULT"
    ])


# Create DataFrame
df = pd.DataFrame(
    data,
    columns=[
        "temperature",
        "vibration",
        "current",
        "rpm",
        "fault_type"
    ]
)

# Shuffle the dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save dataset
df.to_csv("training_data.csv", index=False)

print("Training dataset created successfully!")
print(f"Total records: {len(df)}")
print("\nFault distribution:")
print(df["fault_type"].value_counts())
