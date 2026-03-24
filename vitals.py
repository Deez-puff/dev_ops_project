import pandas as pd
from database import save_vitals, get_vitals_by_patient
from datetime import datetime

IDEAL_RANGES = {
    "heart_rate": {
        "min": 60, "max": 100,
        "unit": "bpm",
        "label": "Heart Rate"
    },
    "spo2": {
        "min": 95, "max": 100,
        "unit": "%",
        "label": "Oxygen Level (SpO2)"
    },
    "temperature": {
        "min": 97.0, "max": 99.5,
        "unit": "°F",
        "label": "Body Temperature"
    },
    "bp_systolic": {
        "min": 90, "max": 120,
        "unit": "mmHg",
        "label": "Blood Pressure (Upper Number)"
    },
    "bp_diastolic": {
        "min": 60, "max": 80,
        "unit": "mmHg",
        "label": "Blood Pressure (Lower Number)"
    },
}

def check_vital(name, value):
    r = IDEAL_RANGES[name]
    if value < r["min"]:
        return "LOW", (
            f"⚠️ Your {r['label']} is a bit LOW "
            f"({value} {r['unit']}). "
            f"Normal range is {r['min']}–{r['max']} {r['unit']}."
        )
    elif value > r["max"]:
        return "HIGH", (
            f"⚠️ Your {r['label']} is a bit HIGH "
            f"({value} {r['unit']}). "
            f"Normal range is {r['min']}–{r['max']} {r['unit']}."
        )
    else:
        return "NORMAL", (
            f"✅ Your {r['label']} is NORMAL "
            f"({value} {r['unit']}). Keep it up!"
        )

def needs_doctor(alerts):
    critical = [a for a in alerts if a[0] != "NORMAL"]
    return len(critical) >= 2

def record_vitals(patient_id, heart_rate, spo2, temperature,
                  bp_systolic, bp_diastolic, medicines):
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_vitals(patient_id, date, heart_rate, spo2,
                temperature, bp_systolic, bp_diastolic, medicines)

def get_vitals_df(patient_id):
    rows = get_vitals_by_patient(patient_id)
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=[
        "id", "patient_id", "date", "heart_rate", "spo2",
        "temperature", "bp_systolic", "bp_diastolic", "medicines"
    ])
    df["date"] = pd.to_datetime(df["date"])
    return df

def suggest_medicine_change(medicines, alerts):
    suggestions = []
    if medicines:
        med_list = [m.strip().lower() for m in medicines.split(",") if m.strip()]
    else:
        med_list = []

    for status, msg in alerts:
        if status == "HIGH" and "heart rate" in msg.lower():
            suggestions.append(
                "💊 Your heart rate is high. If you are not already on "
                "a heart rate medication, please consult your doctor."
            )
        if status == "LOW" and "oxygen" in msg.lower():
            suggestions.append(
                "💊 Your oxygen level is low. This can be serious — "
                "please seek medical attention right away."
            )
        if status == "HIGH" and "upper" in msg.lower():
            if "amlodipine" not in med_list and "lisinopril" not in med_list:
                suggestions.append(
                    "💊 Your blood pressure is high. Talk to your doctor "
                    "about whether blood pressure medication is right for you."
                )
        if status == "HIGH" and "temperature" in msg.lower():
            if "paracetamol" not in med_list and "ibuprofen" not in med_list:
                suggestions.append(
                    "💊 Your temperature is high. Paracetamol or Ibuprofen "
                    "may help bring it down — but consult your doctor first."
                )
        if status == "LOW" and "heart rate" in msg.lower():
            suggestions.append(
                "💊 Your heart rate is low. Avoid heavy exercise and "
                "consult your doctor if you feel dizzy or tired."
            )

    if not suggestions:
        suggestions.append(
            "✅ Your current medicines appear to be working well "
            "based on your vital readings. Keep it up!"
        )

    return suggestions