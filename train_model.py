import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# Load our improved dataset
data = pd.read_csv("training_data.csv")

print("Dataset loaded successfully!")
print(f"Total records: {len(data)}")

# Input features
X = data[[
    "temperature",
    "vibration",
    "current",
    "rpm"
]]

# Target
y = data["fault_type"]

# Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"\nTraining records: {len(X_train)}")
print(f"Testing records: {len(X_test)}")

# Create the model
model = DecisionTreeClassifier(
    random_state=42,
    max_depth=6
)

# Train
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, predictions)

print("\n==============================")
print("MODEL EVALUATION")
print("==============================")

print(f"\nAccuracy: {accuracy * 100:.2f}%")

# Detailed evaluation
print("\nClassification Report:")
print(classification_report(y_test, predictions))

# Confusion matrix
print("Confusion Matrix:")
print(confusion_matrix(y_test, predictions))
