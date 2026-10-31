import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Teacher Workload", page_icon="slottix_icon.png", layout="wide")

hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebarCollapsedControl"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# ── Auth guard ──────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("login.py")

# ── Header row ───────────────────────────────────────────────────────────────
col_title, col_logout = st.columns([9, 1])
with col_title:
    st.title("📊 Teacher Workload Dashboard")
with col_logout:
    if st.button("🚪 Logout", key="logout"):
        st.session_state.clear()
        st.switch_page("login.py")

TIMETABLE_PATH = "data/Master_Timetable.xlsx"

if not os.path.exists(TIMETABLE_PATH):
    st.error("❌ Master Timetable not found. Please generate it first.")
    if st.button("⬅️ Back to Home"):
        st.switch_page("pages/admin_landing_page.py")
    st.stop()

df = pd.read_excel(TIMETABLE_PATH)

# ── Total lectures per teacher ────────────────────────────────────────────────
teacher_counts = (
    df.groupby("Teacher")
    .size()
    .reset_index(name="Total Lectures")
    .sort_values("Total Lectures", ascending=False)
    .reset_index(drop=True)
)

st.subheader("📋 Summary Table")
avg = teacher_counts["Total Lectures"].mean()
col1, col2, col3 = st.columns(3)
col1.metric("Total Teachers", len(teacher_counts))
col2.metric("Total Lectures Scheduled", int(teacher_counts["Total Lectures"].sum()))
col3.metric("Avg Lectures / Teacher", f"{avg:.1f}")

st.dataframe(teacher_counts, use_container_width=True)

# ── Bar chart ─────────────────────────────────────────────────────────────────
st.subheader("📊 Lectures per Teacher")
st.bar_chart(teacher_counts.set_index("Teacher")["Total Lectures"])

# ── Day-wise breakdown ────────────────────────────────────────────────────────
st.subheader("📅 Day-wise Breakdown per Teacher")
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

day_teacher = df.groupby(["Teacher", "Day"]).size().reset_index(name="Lectures")
pivot = day_teacher.pivot_table(
    index="Teacher", columns="Day", values="Lectures", fill_value=0
)
# Reorder columns by weekday
ordered_cols = [d for d in days_order if d in pivot.columns]
pivot = pivot[ordered_cols]
st.dataframe(pivot, use_container_width=True)

st.divider()
if st.button("⬅️ Back to Home"):
    st.switch_page("pages/admin_landing_page.py")
