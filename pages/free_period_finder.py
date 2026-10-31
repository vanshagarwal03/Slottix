import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Free Period Finder", page_icon="slottix_icon.png", layout="wide")

hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebarCollapsedControl"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# ── Auth guard ───────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("login.py")

# ── Header row ───────────────────────────────────────────────────────────────
col_title, col_logout = st.columns([9, 1])
with col_title:
    st.title("🔍 Free Period Finder")
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

days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
all_days = [d for d in days_order if d in df["Day"].unique()]
all_lectures = sorted(df["Lecture"].unique().tolist())
all_slots = [(d, lec) for d in all_days for lec in all_lectures]

# ── Search controls ──────────────────────────────────────────────────────────
search_type = st.radio("Find free slots for:", ["Teacher", "Class / Group"], horizontal=True)

busy_slots: set = set()
label = ""

if search_type == "Teacher":
    teachers = sorted(df["Teacher"].dropna().unique())
    selected = st.selectbox("Select Teacher", teachers)
    mask = df["Teacher"] == selected
    busy_slots = set(zip(df[mask]["Day"], df[mask]["Lecture"]))
    label = f"Teacher: {selected}"
else:
    classes = sorted(df["Class"].dropna().unique())
    selected_class = st.selectbox("Select Class", classes)
    groups = sorted(df[df["Class"] == selected_class]["Group"].dropna().unique())
    selected_group = st.selectbox("Select Group", groups)
    mask = (df["Class"] == selected_class) & (df["Group"] == selected_group)
    busy_slots = set(zip(df[mask]["Day"], df[mask]["Lecture"]))
    label = f"Class {selected_class} – Group {selected_group}"

# ── Build free slot grid ─────────────────────────────────────────────────────
free_slots = [(d, lec) for (d, lec) in all_slots if (d, lec) not in busy_slots]
busy_count = len(busy_slots)
free_count = len(free_slots)

col1, col2, col3 = st.columns(3)
col1.metric("Total Slots", len(all_slots))
col2.metric("Busy Slots", busy_count)
col3.metric("Free Slots", free_count)

if free_slots:
    st.success(f"✅ {free_count} free slot(s) for **{label}**")
    free_df = pd.DataFrame(free_slots, columns=["Day", "Lecture"])
    free_df["Day"] = pd.Categorical(free_df["Day"], categories=all_days, ordered=True)
    free_df["Status"] = "✅ Free"
    pivot = free_df.pivot_table(
        index="Day", columns="Lecture", values="Status", aggfunc="first"
    )
    # Fill busy slots with marker
    all_pivot = pd.DataFrame(
        index=pd.CategoricalIndex(all_days, categories=all_days, ordered=True),
        columns=all_lectures
    )
    for d, lec in all_slots:
        all_pivot.at[d, lec] = "✅ Free" if (d, lec) not in busy_slots else "🔴 Busy"

    st.dataframe(all_pivot, use_container_width=True)
else:
    st.warning(f"⚠️ No free slots found for **{label}**.")

st.divider()
if st.button("⬅️ Back to Home"):
    st.switch_page("pages/admin_landing_page.py")
