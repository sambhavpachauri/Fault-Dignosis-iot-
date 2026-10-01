import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    balanced_accuracy_score,
    roc_auc_score,
    confusion_matrix
)

# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

df = pd.read_csv("ai4i2020.csv")

# --------------------------------------------------
# 2. Select features
# --------------------------------------------------

features = [
    "Type",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]"
]

target = "Machine failure"

X = df[features]
y = df[target]

# Convert Type into numerical columns
X = pd.get_dummies(X, columns=["Type"], dtype=int)

# --------------------------------------------------
# 3. Train/Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# --------------------------------------------------
# 4. Create Gradient Boosting model
# --------------------------------------------------

model = GradientBoostingClassifier(
    n_estimators=150,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)

# --------------------------------------------------
# 5. Train
# --------------------------------------------------

print("Training Gradient Boosting model...")

model.fit(X_train, y_train)

print("Training complete!")

# --------------------------------------------------
# 6. Predictions
# --------------------------------------------------

probabilities = model.predict_proba(X_test)[:, 1]

# Our selected threshold
THRESHOLD = 0.40

predictions = (probabilities >= THRESHOLD).astype(int)

# --------------------------------------------------
# 7. Evaluation
# --------------------------------------------------

print("\n========== FINAL MODEL ==========")

print(f"Threshold          : {THRESHOLD}")
print(f"Precision          : {precision_score(y_test, predictions):.4f}")
print(f"Recall             : {recall_score(y_test, predictions):.4f}")
print(f"F1 Score           : {f1_score(y_test, predictions):.4f}")
print(
    f"Balanced Accuracy  : "
    f"{balanced_accuracy_score(y_test, predictions):.4f}"
)
print(f"ROC-AUC            : {roc_auc_score(y_test, probabilities):.4f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

# --------------------------------------------------
# 8. Save model
# --------------------------------------------------

os.makedirs("models", exist_ok=True)

model_data = {
    "model": model,
    "features": X.columns.tolist(),
    "threshold": THRESHOLD
}

joblib.dump(model_data, "models/fault_model.pkl")

print("\nModel saved successfully!")
print("Location: models/fault_model.pkl")
