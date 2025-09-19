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

st.set_page_config(page_title="Bedrock Monitor", layout="wide")
st.markdown("# 🧠 Bedrock Call Monitor")
logs = load_logs()

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"### Total Calls: **{len(logs)}**")
    if logs:
        st.markdown("## Call Details")
        for i, log in enumerate(logs[::-1], 1):
            st.markdown(f"#### Call #{len(logs)-i+1}")
            st.write(f"**User:** {log.get('user', 'N/A')}")
            st.write(f"**Timestamp:** {log.get('timestamp', 'N/A')}")
            st.write(f"**Cost:** ${float(log.get('cost', 0)):.2f}")
            with st.expander("Request & Response", expanded=False):
                st.write("**Request:**")
                st.code(str(log.get('request', '')), language='text')
                st.write("**Response:**")
                st.json(log.get('response', {}))
    else:
        st.info("No Bedrock calls logged yet.")

with col2:
    total_cost = sum(float(log.get("cost", 0)) for log in logs)
    st.markdown(f"### 💸 Total Cost")
    st.metric(label="Total Cost", value=f"${total_cost:.2f}")
