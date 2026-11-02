import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Room Utilization", page_icon="slottix_icon.png", layout="wide")

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
    st.title("🏫 Room Utilization View")
with col_logout:
    if st.button("🚪 Logout", key="logout"):
        st.session_state.clear()
        st.switch_page("login.py")

TIMETABLE_PATH = "data/Master_Timetable.xlsx"
ROOMS_PATH     = "data/Special_Classrooms.xlsx"

if not os.path.exists(TIMETABLE_PATH):
    st.error("❌ Master Timetable not found. Please generate it first.")
    if st.button("⬅️ Back to Home"):
        st.switch_page("pages/admin_landing_page.py")
    st.stop()

df = pd.read_excel(TIMETABLE_PATH)

# Keep only rows where a special room was assigned
df_rooms = df[df["Room"].notna() & (df["Room"].astype(str).str.strip() != "")].copy()

if df_rooms.empty:
    st.info("ℹ️ No special rooms were assigned in the timetable.")
    if st.button("⬅️ Back to Home"):
        st.switch_page("pages/admin_landing_page.py")
    st.stop()

# Load capacities
room_capacities: dict = {}
if os.path.exists(ROOMS_PATH):
    try:
        rooms_df = pd.read_excel(ROOMS_PATH)
        room_capacities = dict(zip(rooms_df["Room Type"], rooms_df["Count"]))
    except Exception:
        pass

days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ── Room filter ───────────────────────────────────────────────────────────────
all_rooms = sorted(df_rooms["Room"].unique())
selected_room = st.selectbox("Filter by Room Type", ["All Rooms"] + all_rooms)

filtered = df_rooms if selected_room == "All Rooms" else df_rooms[df_rooms["Room"] == selected_room]

# ── Summary metrics ───────────────────────────────────────────────────────────
usage_agg = (
    filtered.groupby(["Room", "Day", "Lecture"])
    .size()
    .reset_index(name="Sessions")
)

col1, col2 = st.columns(2)
col1.metric("Total Booked Slots", len(usage_agg))
col2.metric("Unique Rooms Used", filtered["Room"].nunique())

# ── Detailed table ────────────────────────────────────────────────────────────
st.subheader("📋 Room Booking Details")
detail_df = (
    filtered[["Room", "Day", "Lecture", "Class", "Group", "Subject", "Teacher"]]
    .sort_values(["Room", "Day", "Lecture"])
    .reset_index(drop=True)
)
st.dataframe(detail_df, use_container_width=True)

# ── Per-room utilization heatmap ──────────────────────────────────────────────
room_to_show = all_rooms if selected_room == "All Rooms" else [selected_room]

for room in room_to_show:
    st.subheader(f"📊 Utilization: {room}")
    capacity = room_capacities.get(room, 1)
    st.caption(f"Capacity: {capacity} parallel session(s)")

    room_data = usage_agg[usage_agg["Room"] == room]
    if room_data.empty:
        st.write("No bookings.")
        continue

    pivot = room_data.pivot_table(
        index="Day", columns="Lecture", values="Sessions", fill_value=0
    )
    available_days = [d for d in days_order if d in pivot.index]
    pivot = pivot.reindex(available_days)

    # Colour each cell: green = within capacity, red = over capacity
    def colour_cell(val):
        if val == 0:
            return "background-color: #f5f5f5; color: #999"
        elif val <= capacity:
            return "background-color: #c6efce; color: #276221"
        else:
            return "background-color: #ffc7ce; color: #9c0006"

    try:
        st.dataframe(
            pivot.style.map(colour_cell) if hasattr(pivot.style, "map") else pivot.style.applymap(colour_cell),
            use_container_width=True
        )
    except Exception:
        st.dataframe(pivot, use_container_width=True)

st.divider()
if st.button("⬅️ Back to Home"):
    st.switch_page("pages/admin_landing_page.py")
