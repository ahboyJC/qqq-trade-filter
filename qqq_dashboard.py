import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# === CONFIG ===
st.set_page_config(page_title="QQQ Trade Filter", layout="centered")
st.title("QQQ Put Spread Auto-Filter")
st.caption("Updates every minute | Next check: 11:00 PM SGT")

# === REAL-TIME DATA ===
sgt = pytz.timezone('Asia/Singapore')
now = datetime.now(sgt)
today_str = now.strftime('%Y-%m-%d')

# Fetch data
qqq = yf.Ticker("QQQ")
vix = yf.Ticker("^VIX")
qqq_hist = qqq.history(period="3mo")
vix_price = vix.history(period="1d")['Close'].iloc[-1]

# 50-day MA
ma50 = qqq_hist['Close'].rolling(50).mean().iloc[-1]
qqq_price = qqq_hist['Close'].iloc[-1]

# US Holiday Check (2025)
holidays_2025 = [
    "2025-01-01", "2025-01-20", "2025-02-17", "2025-04-18",
    "2025-05-26", "2025-06-19", "2025-07-04", "2025-09-01",
    "2025-11-27", "2025-12-25"
]
is_holiday = today_str in holidays_2025

# === 4 FILTERS ===
f1 = qqq_price >= ma50
f2 = vix_price <= 30
f3 = True  # Credit check — you'll input manually or via Tiger API later
f4 = not is_holiday

# === DASHBOARD DISPLAY ===
col1, col2 = st.columns(2)
with col1:
    st.metric("QQQ Price", f"${qqq_price:.2f}", f"{qqq_price - ma50:+.2f}")
    st.metric("50-day MA", f"${ma50:.2f}")
with col2:
    st.metric("VIX", f"{vix_price:.2f}", f"{30 - vix_price:+.1f} from cap")
    st.write(f"**Holiday?** {'YES → SKIP' if is_holiday else 'NO'}")

st.divider()

# === FILTER STATUS ===
filters = [
    ("QQQ ≥ 50-day MA", f1, "✅ PASS" if f1 else "❌ FAIL"),
    ("VIX ≤ 30", f2, "✅ PASS" if f2 else "❌ FAIL"),
    ("Credit ≥ $0.22", f3, "⚠️ MANUAL" if f3 else "❌ FAIL"),
    ("No US Holiday", f4, "✅ PASS" if f4 else "❌ FAIL"),
]

pass_count = sum(1 for _, status, _ in filters if status)
st.write(f"### **{pass_count}/4 FILTERS PASS**")

for label, status, emoji in filters:
    color = "green" if "PASS" in emoji else "red" if "FAIL" in emoji else "orange"
    st.markdown(f"<span style='color:{color}; font-size:20px'>{emoji} {label}</span>", unsafe_allow_html=True)

# === FINAL SIGNAL ===
if pass_count == 4 and now.hour == 23 and now.minute >= 0:
    st.success("**TRADE SIGNAL: GREEN → EXECUTE NOW**")
    st.balloons()
elif now.hour == 23 and now.minute < 30:
    st.info("⏳ Waiting for 11:00 PM SGT window...")
else:
    st.error("**RED → SKIP TODAY**")

# === CREDIT INPUT (Manual for now) ===
st.sidebar.header("Manual Credit Check")
credit = st.sidebar.number_input("Enter $5-wide credit (e.g. 0.27)", 0.00, 1.00, 0.27)
if credit >= 0.24:
    st.sidebar.success(f"Credit OK → Target Profit: ${credit*50:.0f}")
elif credit >= 0.18:
    st.sidebar.warning(f"Low credit → Try $3-wide")
else:
    st.sidebar.error("Credit too low → SKIP")

# Footer
st.caption(f"Last updated: {now.strftime('%H:%M:%S %p SGT')} | @CleanWhistle")
