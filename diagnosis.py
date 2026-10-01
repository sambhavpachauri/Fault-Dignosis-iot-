def diagnose_machine(data, failure_probability):
    """
    Analyze machine sensor values and determine
    severity + possible contributing conditions.
    """

    issues = []

    # --------------------------------------------------
    # 1. Check temperature
    # --------------------------------------------------

    if data["air_temperature"] >= 301:
        issues.append("Elevated air temperature")

    if data["process_temperature"] >= 312:
        issues.append("High process temperature")

    # --------------------------------------------------
    # 2. Check rotational speed
    # --------------------------------------------------

    if data["rotational_speed"] < 1300:
        issues.append("Low rotational speed")

    elif data["rotational_speed"] > 1650:
        issues.append("High rotational speed")

    # --------------------------------------------------
    # 3. Check torque
    # --------------------------------------------------

    if data["torque"] >= 55:
        issues.append("High torque")

    # --------------------------------------------------
    # 4. Check tool wear
    # --------------------------------------------------

    if data["tool_wear"] >= 150:
        issues.append("High tool wear")

    elif data["tool_wear"] >= 100:
        issues.append("Increasing tool wear")

    # --------------------------------------------------
    # 5. Determine severity
    # --------------------------------------------------

    if failure_probability >= 0.75:
        severity = "CRITICAL"

    elif failure_probability >= 0.40:
        severity = "HIGH"

    elif failure_probability >= 0.20:
        severity = "MEDIUM"

    else:
        severity = "LOW"

    # --------------------------------------------------
    # 6. If no sensor issue was found
    # --------------------------------------------------

    if not issues:
        issues.append("No major abnormal sensor condition detected")

    # --------------------------------------------------
    # 7. Generate recommended action
    # --------------------------------------------------

    if severity == "CRITICAL":
        recommendation = (
            "Stop or isolate the machine and perform immediate inspection."
        )

    elif severity == "HIGH":
        recommendation = (
            "Schedule immediate maintenance inspection and check "
            "the identified sensor conditions."
        )

    elif severity == "MEDIUM":
        recommendation = (
            "Continue monitoring the machine and schedule preventive maintenance."
        )

    else:
        recommendation = (
            "Machine appears stable. Continue normal monitoring."
        )

    return {
        "severity": severity,
        "issues": issues,
        "recommendation": recommendation
    }
