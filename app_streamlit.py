import streamlit as st
import requests
import psutil
import time

st.title("Mobile Price Predictor")
st.write("Send 5 numeric features to the local API at http://127.0.0.1:5000/predict")

# System status panel
st.markdown("---")
st.header("System Status")
col1, col2 = st.columns(2)

# Refresh control
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0

with col2:
    if st.button("Refresh system stats"):
        st.session_state.last_refresh = time.time()

# Read system stats
bat = psutil.sensors_battery()
mem = psutil.virtual_memory()

with col1:
    if bat is None:
        st.info("Battery: not available")
    else:
        st.metric("Battery", f"{bat.percent}%")
        st.progress(int(bat.percent))

    st.metric("RAM usage", f"{mem.percent}%")
    st.write(f"Used: {mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB")
    st.progress(int(mem.percent))

st.markdown("---")

# Main predictor UI
cols = st.columns(4)
features = []
for i in range(20):
    value = cols[i % 4].number_input(f"F{i+1}", value=float(i+1))
    features.append(value)

if st.button("Predict"):
    try:
        r = requests.post("http://127.0.0.1:5000/predict", json={"features": features}, timeout=5)
        st.write(f"Status code: {r.status_code}")
        try:
            data = r.json()
            pr = data.get('price_range')
            labels = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Very High'}
            label = labels.get(pr, 'Unknown')
            # Simple, prominent display
            st.markdown(f"<div style='background:#0b8457;padding:12px;border-radius:6px'><h2 style='color:white;margin:0'>Price range: {pr} — {label}</h2></div>", unsafe_allow_html=True)
        except Exception:
            st.text("Response text:")
            st.text(r.text)
        r.raise_for_status()
    except Exception as e:
        st.error(f"Request failed: {e}")
        try:
            with open('predictions.log', 'r', encoding='utf-8') as fh:
                lines = fh.readlines()
                st.markdown("**Last prediction logs:**")
                st.code(''.join(lines[-5:]))
        except Exception:
            st.info("No prediction log available or failed to read it")

# Quick test button to send a sample request and show the response
if st.button("Test API (sample)"):
    sample = list(range(1, 21))
    try:
        r = requests.post("http://127.0.0.1:5000/predict", json={"features": sample}, timeout=5)
        st.write("Sent sample features:", sample)
        st.write(f"Status code: {r.status_code}")
        try:
            data = r.json()
            pr = data.get('price_range')
            labels = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Very High'}
            label = labels.get(pr, 'Unknown')
            st.markdown(f"<div style='background:#0b8457;padding:12px;border-radius:6px'><h2 style='color:white;margin:0'>Price range: {pr} — {label}</h2></div>", unsafe_allow_html=True)
        except Exception:
            st.text(r.text)
    except Exception as e:
        st.error(f"Test request failed: {e}")
