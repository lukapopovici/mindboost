import streamlit as st
import json
import os
from datetime import datetime

LOG_FILE = "bedrock_calls.json"

def load_logs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_log(entry):
    logs = load_logs()
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def log_bedrock_call(user, request, response, cost):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "request": request,
        "response": response,
        "cost": cost
    }
    save_log(entry)

st.title("Bedrock Call Monitor")
logs = load_logs()

st.write(f"Total calls: {len(logs)}")
if logs:
    st.write("## Call Details")
    for log in logs:
        st.json(log)
    total_cost = sum(float(log.get("cost", 0)) for log in logs)
    st.write(f"### Total Cost: ${total_cost:.2f}")
else:
    st.write("No Bedrock calls logged yet.")
