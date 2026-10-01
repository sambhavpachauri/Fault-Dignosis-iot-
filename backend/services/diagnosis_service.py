import sys
from pathlib import Path
from backend.schemas.models import SensorThresholdEvaluation

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import existing diagnosis module without altering it
from diagnosis import diagnose_machine


def evaluate_sensor_thresholds(sensor_data: dict) -> dict[str, SensorThresholdEvaluation]:
    """
    Evaluates each sensor against the EXACT thresholds defined in diagnosis.py.
    Air temperature: >= 301 K is elevated
    Process temperature: >= 312 K is high
    Rotational speed: < 1300 is low, > 1650 is high
    Torque: >= 55 Nm is high
    Tool wear: >= 150 min is high, >= 100 min is increasing
    """
    air_temp = float(sensor_data["air_temperature"])
    proc_temp = float(sensor_data["process_temperature"])
    rot_speed = int(sensor_data["rotational_speed"])
    torque = float(sensor_data["torque"])
    tool_wear = int(sensor_data["tool_wear"])

    evaluations = {}

    # 1. Air Temperature
    air_is_normal = air_temp < 301.0
    evaluations["air_temperature"] = SensorThresholdEvaluation(
        name="Air Temperature",
        value=air_temp,
        unit="K",
        normal_range="< 301.0 K",
        is_normal=air_is_normal,
        status_label="ELEVATED" if not air_is_normal else "NORMAL"
    )

    # 2. Process Temperature
    proc_is_normal = proc_temp < 312.0
    evaluations["process_temperature"] = SensorThresholdEvaluation(
        name="Process Temperature",
        value=proc_temp,
        unit="K",
        normal_range="< 312.0 K",
        is_normal=proc_is_normal,
        status_label="HIGH" if not proc_is_normal else "NORMAL"
    )

    # 3. Rotational Speed
    speed_is_normal = 1300 <= rot_speed <= 1650
    if rot_speed < 1300:
        speed_label = "LOW"
    elif rot_speed > 1650:
        speed_label = "HIGH"
    else:
        speed_label = "NORMAL"

    evaluations["rotational_speed"] = SensorThresholdEvaluation(
        name="Rotational Speed",
        value=float(rot_speed),
        unit="RPM",
        normal_range="1300 - 1650 RPM",
        is_normal=speed_is_normal,
        status_label=speed_label
    )

    # 4. Torque
    torque_is_normal = torque < 55.0
    evaluations["torque"] = SensorThresholdEvaluation(
        name="Torque",
        value=torque,
        unit="Nm",
        normal_range="< 55.0 Nm",
        is_normal=torque_is_normal,
        status_label="HIGH" if not torque_is_normal else "NORMAL"
    )

    # 5. Tool Wear
    wear_is_normal = tool_wear < 100
    if tool_wear >= 150:
        wear_label = "HIGH"
    elif tool_wear >= 100:
        wear_label = "INCREASING"
    else:
        wear_label = "NORMAL"

    evaluations["tool_wear"] = SensorThresholdEvaluation(
        name="Tool Wear",
        value=float(tool_wear),
        unit="min",
        normal_range="< 100 min",
        is_normal=wear_is_normal,
        status_label=wear_label
    )

    return evaluations


def run_diagnosis(sensor_data: dict, failure_probability: float) -> dict:
    """
    Executes the existing diagnosis logic and supplements it with granular threshold evaluations.
    """
    raw_diag = diagnose_machine(sensor_data, failure_probability)
    sensor_evals = evaluate_sensor_thresholds(sensor_data)

    return {
        "severity": raw_diag["severity"],
        "issues": raw_diag["issues"],
        "recommendation": raw_diag["recommendation"],
        "sensor_evaluations": sensor_evals
    }
