import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Conflict Detector", page_icon="slottix_icon.png", layout="wide")

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
    st.title("⚠️ Conflict Detector / Validator")
with col_logout:
    if st.button("🚪 Logout", key="logout"):
        st.session_state.clear()
        st.switch_page("login.py")

TIMETABLE_PATH = "data/Master_Timetable.xlsx"
ROOMS_PATH = "data/Special_Classrooms.xlsx"

if not os.path.exists(TIMETABLE_PATH):
    st.error("❌ Master Timetable not found. Please generate it first.")
    if st.button("⬅️ Back to Home"):
        st.switch_page("pages/admin_landing_page.py")
    st.stop()

df = pd.read_excel(TIMETABLE_PATH)

# ── Run scan ─────────────────────────────────────────────────────────────────
if st.button("🔍 Scan for Conflicts", type="primary"):
    conflicts = []

    # 1. Teacher double-booking: same teacher, same day, same lecture slot
    tc = df[df.duplicated(subset=["Teacher", "Day", "Lecture"], keep=False)]
    for _, row in tc.iterrows():
        conflicts.append({
            "Type": "Teacher Double-Booking",
            "Details": (
                f"Teacher: {row['Teacher']}  |  "
                f"Day: {row['Day']}  |  "
                f"Lecture: {row['Lecture']}  |  "
                f"Class: {row['Class']}-{row['Group']}"
            )
        })

    # 2. Class double-booking: same class+group, same day, same lecture slot
    cc = df[df.duplicated(subset=["Class", "Group", "Day", "Lecture"], keep=False)]
    for _, row in cc.iterrows():
        conflicts.append({
            "Type": "Class Double-Booking",
            "Details": (
                f"Class: {row['Class']}-{row['Group']}  |  "
                f"Day: {row['Day']}  |  "
                f"Lecture: {row['Lecture']}  |  "
                f"Subject: {row['Subject']}"
            )
        })

    # 3. Room over-booking
    room_capacities = {}
    if os.path.exists(ROOMS_PATH):
        try:
            rooms_df = pd.read_excel(ROOMS_PATH)
            room_capacities = dict(zip(rooms_df["Room Type"], rooms_df["Count"]))
        except Exception:
            pass

    df_with_room = df[df["Room"].notna() & (df["Room"].astype(str).str.strip() != "")]
    if not df_with_room.empty:
        room_usage = (
            df_with_room.groupby(["Room", "Day", "Lecture"])
            .size()
            .reset_index(name="Used")
        )
        for _, row in room_usage.iterrows():
            capacity = room_capacities.get(row["Room"], 1)
            if row["Used"] > capacity:
                conflicts.append({
                    "Type": "Room Over-Booking",
                    "Details": (
                        f"Room: {row['Room']}  |  "
                        f"Day: {row['Day']}  |  "
                        f"Lecture: {row['Lecture']}  |  "
                        f"Used: {row['Used']}  /  Capacity: {capacity}"
                    )
                })

    # ── Results ───────────────────────────────────────────────────────────────
    if conflicts:
        st.error(f"❌ {len(conflicts)} conflict(s) found!")
        df_conflicts = pd.DataFrame(conflicts)
        # Show counts by type
        type_counts = df_conflicts["Type"].value_counts().reset_index()
        type_counts.columns = ["Conflict Type", "Count"]
        st.dataframe(type_counts, use_container_width=True)
        st.subheader("Detailed Conflict List")
        st.dataframe(df_conflicts, use_container_width=True)
    else:
        st.success("✅ No conflicts found! Timetable is clean.")
else:
    st.info("Click **Scan for Conflicts** to analyse the timetable.")

st.divider()
if st.button("⬅️ Back to Home"):
    st.switch_page("pages/admin_landing_page.py")
