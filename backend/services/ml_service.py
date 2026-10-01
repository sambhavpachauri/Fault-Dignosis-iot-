import os
from pathlib import Path
import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "fault_model.pkl"


class MLService:
    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        self.model_data = joblib.load(model_path)
        self.model = self.model_data["model"]
        self.features = self.model_data["features"]
        self.threshold = float(self.model_data["threshold"])
        print(f"MLService initialized: threshold={self.threshold}, features={self.features}")

    def predict(self, sensor_data: dict) -> tuple[float, str]:
        """
        Runs inference on sensor reading dictionary.
        Returns:
            failure_probability (float): Between 0.0 and 1.0
            status (str): "FAULT RISK" if prob >= threshold else "NORMAL"
        """
        input_data = pd.DataFrame([{
            "Air temperature [K]": float(sensor_data["air_temperature"]),
            "Process temperature [K]": float(sensor_data["process_temperature"]),
            "Rotational speed [rpm]": int(sensor_data["rotational_speed"]),
            "Torque [Nm]": float(sensor_data["torque"]),
            "Tool wear [min]": int(sensor_data["tool_wear"]),
            "Type_H": 1 if sensor_data.get("type") == "H" else 0,
            "Type_L": 1 if sensor_data.get("type") == "L" else 0,
            "Type_M": 1 if sensor_data.get("type") == "M" else 0
        }])

        input_data = input_data[self.features]
        proba = float(self.model.predict_proba(input_data)[0][1])
        status = "FAULT RISK" if proba >= self.threshold else "NORMAL"
        return proba, status


ml_service = MLService()
