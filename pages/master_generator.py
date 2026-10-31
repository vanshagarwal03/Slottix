import os
import io
import random
import re
from collections import defaultdict, Counter

import pandas as pd
import streamlit as st
from io import BytesIO

# Import OR-Tools solver with friendly error message if missing
try:
    from ortools.linear_solver import pywraplp
except Exception as e:
    pywraplp = None

# Streamlit page setup
st.set_page_config(page_title="Timetable Input", page_icon="slottix_icon.png", layout="wide")

# Hide sidebar
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# ======================
# Cached data loaders
# ======================
@st.cache_data
def load_faculty():
    df = pd.read_excel("data/faculty.xlsx")
    names = df["name"].dropna().astype(str).tolist()
    return [re.sub(r'\s+', ' ', n.strip()) for n in names if n.strip()]

@st.cache_data
def load_classes():
    df = pd.read_excel("data/classes.xlsx")
    return df, df["class"].dropna().unique().tolist()

@st.cache_data
def load_rooms():
    df = pd.read_excel("data/Special_Classrooms.xlsx")
    rooms = dict(zip(df["Room Type"], df["Count"]))
    return rooms

# ======================
# Load resources
# ======================
try:
    faculty_list = load_faculty()
except Exception as e:
    st.error(f"Error loading faculty file: {e}")
    faculty_list = []

try:
    class_df, classes = load_classes()
except Exception as e:
    st.error(f"Error loading class/subject file: {e}")
    classes, class_df = [], pd.DataFrame()

# ======================
# Session state
# ======================
if "subjects" not in st.session_state:
    st.session_state["subjects"] = []

if "rooms" not in st.session_state:
    st.session_state["rooms"] = {}

if "unplaced_lectures" not in st.session_state:
    st.session_state["unplaced_lectures"] = []

# Merge rooms from file
try:
    loaded_rooms = load_rooms()
    for rtype, count in loaded_rooms.items():
        if rtype not in st.session_state["rooms"]:
            st.session_state["rooms"][rtype] = int(count)
except Exception as e:
    st.warning(f"⚠️ Could not load Special_Classrooms.xlsx: {e}")

# ======================
# Helper functions
# ======================
def add_subject_to_session(new_entry):
    """Add a subject only if Class+Subject combination is not already added."""
    existing_keys = {(e["Class"], e["Subject"]) for e in st.session_state["subjects"]}
    key = (new_entry["Class"], new_entry["Subject"])
    if key not in existing_keys:
        st.session_state["subjects"].append(new_entry)
        st.session_state.pop("preview_schedule", None)
        st.session_state.pop("generated_pivot", None)
        return True
    return False

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def validate_schedule(df: pd.DataFrame, required_cols: list) -> bool:
    if not all(col in df.columns for col in required_cols):
        st.error(f"Schedule must contain columns: {required_cols}")
        return False
    return True

# ======================
# Main UI
# ======================
col_h1, col_h2 = st.columns([0.08, 0.92], vertical_alignment="center")
with col_h1:
    st.image("slottix_icon.png", width=55)
with col_h2:
    st.title("Master Timetable Generator")

# ── Persistent unplaced-lectures notification ─────────────────────────────────
if st.session_state.get("unplaced_lectures"):
    unplaced = st.session_state["unplaced_lectures"]
    with st.expander(
        f"⚠️ {len(unplaced)} lecture(s) could not be fully placed in the last generation — click to view",
        expanded=False,
    ):
        for item in unplaced:
            st.warning(item)
        if st.button("Clear Notifications", key="clear_unplaced"):
            st.session_state["unplaced_lectures"] = []
            st.rerun()

num_sections = st.number_input("Number of Sections (Batches)", min_value=1, value=1)
num_lectures_per_day = st.number_input("Maximum Lectures per Day", min_value=1, value=6)
st.session_state["num_lectures_per_day"] = num_lectures_per_day
st.session_state["num_sections"] = num_sections

st.write("---")
st.subheader("Add Subject Entry")

# ======================
# Single row input for subjects
# ======================
c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 1, 2, 2, 1])

with c1:
    selected_class = st.selectbox(
        "Class", 
        options=["Select"] + list(classes), 
        key="class_input"
    )

with c2:
    available_subjects = []
    if selected_class != "Select":
        available_subjects = class_df[class_df["class"] == selected_class]["subject"].dropna().unique().tolist()
    selected_subject = st.selectbox(
        "Subject",
        options=["Select"] + available_subjects,
        key="subject_input",
        disabled=(selected_class == "Select")
    )

with c3:
    classes_per_week = st.number_input("Per Week", min_value=1, value=1, key="cpw_input")

with c4:
    selected_faculties = st.multiselect("Faculties", options=faculty_list, key="faculty_input")

with c5:
    room_options = ["None"] + list(st.session_state.get("rooms", {}).keys())
    selected_room = st.selectbox("Special Room Required", options=room_options, key="room_input")

with c6:
    if st.button("➕ Add"):
        if selected_class == "Select" or selected_subject == "Select" or not selected_faculties:
            st.warning("⚠️ Please select a class, subject, and at least one faculty.")
        else:
            new_entry = {
                "Class": selected_class,
                "Subject": selected_subject,
                "Classes/Week": int(classes_per_week),
                "Faculties": selected_faculties,
                "Room": None if selected_room == "None" else selected_room
            }
            if add_subject_to_session(new_entry):
                st.success("✅ Entry added!")
            else:
                st.warning("⚠️ This class-subject is already added!")

st.write("---")

# ======================
# Upload schedule from Excel (auto)
# ======================
st.subheader("Upload Schedule from Excel")
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df_schedule = pd.read_excel(uploaded_file)
        required_cols = ["Class", "Subject", "Classes/Week", "Faculties", "Room"]

        if validate_schedule(df_schedule, required_cols):
            added_count = 0
            for _, row in df_schedule.iterrows():
                faculties_list = (
                    row["Faculties"].split(",") if isinstance(row["Faculties"], str) else list(row["Faculties"])
                )
                new_entry = {
                    "Class": row["Class"],
                    "Subject": row["Subject"],
                    "Classes/Week": int(row["Classes/Week"]),
                    "Faculties": faculties_list,
                    "Room": None if pd.isna(row["Room"]) or row["Room"] == "None" else row["Room"]
                }
                if add_subject_to_session(new_entry):
                    added_count += 1
            st.success(f"✅ Schedule uploaded! {added_count} new entries added.")
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")

st.write("---")

# ======================
# Show current subjects with remove buttons
# ======================
if st.session_state["subjects"]:
    st.subheader("Current Entries")
    for idx, entry in enumerate(list(st.session_state["subjects"])):
        c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 1, 2, 2, 1])
        c1.write(entry["Class"])
        c2.write(entry["Subject"])
        c3.write(entry["Classes/Week"])
        c4.write(", ".join(entry["Faculties"]))
        c5.write(entry["Room"] if entry["Room"] else "-")
        if c6.button("❌", key=f"remove_{idx}"):
            st.session_state["subjects"].pop(idx)
            st.session_state.pop("preview_schedule", None)
            st.session_state.pop("generated_pivot", None)
            st.rerun()
else:
    st.info("No subjects added yet.")

# ======================
# Core Generation Functions
# ======================
def generate_schedule_data(subjects, num_sections):
    """
    Optimizes teacher allocation for each (Class, Group, Subject) combination
    using OR-Tools SCIP solver to balance workload among selected teachers.
    """
    if not subjects:
        return None, "Please add at least one subject before generating a schedule."
    if pywraplp is None:
        return None, "OR-Tools not installed. Run `pip install ortools`."

    assignments = []
    teacher_loads = {}
    group_labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    groups = min(int(num_sections), len(group_labels))

    # Prepare assignments
    for entry in subjects:
        cls = entry["Class"]
        subj = entry["Subject"]
        freq = int(entry["Classes/Week"])
        faculties = entry["Faculties"]
        room = entry["Room"]

        for g in range(groups):
            assignments.append({
                "class": cls,
                "group": group_labels[g],
                "subject": subj,
                "freq": freq,
                "faculties": faculties,
                "room": room
            })
            for f in faculties:
                teacher_loads[f] = teacher_loads.get(f, 0)

    # OR-Tools solver
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        return None, "OR-Tools SCIP solver not available."

    x = {}
    for i, entry in enumerate(assignments):
        for f in entry["faculties"]:
            x[(i, f)] = solver.IntVar(0, 1, f"x_{i}_{f}")

    for i, entry in enumerate(assignments):
        solver.Add(solver.Sum([x[(i, f)] for f in entry["faculties"]]) == 1)

    total_freq = sum(entry["freq"] for entry in assignments)
    max_load = solver.IntVar(0, total_freq, "max_load")

    for f in teacher_loads:
        terms = []
        for i, entry in enumerate(assignments):
            if f in entry["faculties"]:
                terms.append(x[(i, f)] * entry["freq"])
        if terms:
            solver.Add(solver.Sum(terms) <= max_load)

    solver.Minimize(max_load)
    status = solver.Solve()

    if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
        result = []
        for i, entry in enumerate(assignments):
            for f in entry["faculties"]:
                if x[(i, f)].solution_value() == 1:
                    result.append({
                        "Grade": entry["class"],
                        "Groups": entry["group"],
                        "Subject": entry["subject"],
                        "Frequency": entry["freq"],
                        "Teacher": f,
                        "Room": entry["room"]
                    })

        df_result = pd.DataFrame(result)
        os.makedirs("data", exist_ok=True)
        df_result.to_excel("data/Final_Schedule.xlsx", index=False)
        return df_result, None
    else:
        return None, "Could not find a feasible schedule with the given teacher constraints."


def generate_master_timetable_data(df_sched, num_lectures_per_day):
    """
    Places scheduled lectures into day & time slots (Mon-Fri) without clash.
    """
    required_cols = ["Grade", "Groups", "Subject", "Frequency", "Teacher", "Room"]
    if not validate_schedule(df_sched, required_cols):
        return None, None, "Invalid schedule format."

    df_sched = df_sched.copy()
    df_sched["Frequency"] = pd.to_numeric(df_sched["Frequency"], errors="coerce").fillna(0).astype(int)
    timetable = []
    used_slots_class = set()
    used_slots_teacher = set()
    used_rooms = defaultdict(int)
    class_subjects_per_day = defaultdict(lambda: Counter())
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    if df_sched["Groups"].isnull().all():
        num_sections = st.session_state.get("num_sections", 1)
        group_labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
        groups_to_use = group_labels[:max(1, num_sections)]
        expanded = []
        for _, r in df_sched.iterrows():
            for g in groups_to_use:
                nr = r.copy()
                nr["Groups"] = g
                expanded.append(nr)
        df_sched = pd.DataFrame(expanded)

    df_sched = df_sched.sample(frac=1, random_state=42).reset_index(drop=True)
    max_same_subject_per_day = 1
    all_slots = [(d, lec) for d in days for lec in range(1, num_lectures_per_day + 1)]

    def slot_score(cls, group, subj, teacher, room, d, lec):
        score = 0
        if (teacher, d, lec) in used_slots_teacher: score += 1000
        if (cls, group, d, lec) in used_slots_class: score += 1000
        if class_subjects_per_day[(cls, group, d)][subj] >= max_same_subject_per_day: score += 50
        if pd.notna(room) and str(room).strip() and str(room).lower() not in ["none", "nan"]:
            key = (room, d, lec)
            max_room_count = st.session_state.get("rooms", {}).get(room, 1)
            if used_rooms[key] >= max_room_count: score += 500
        score += lec * 2
        return score

    unplaced = []
    for _, row in df_sched.iterrows():
        cls, group, subj, freq, teacher, room = (
            row["Grade"], row["Groups"], row["Subject"],
            int(row["Frequency"]), row["Teacher"], row["Room"]
        )
        room = room if (pd.notna(room) and str(room).strip() and str(room).lower() not in ["none", "nan"]) else None
        placed = 0

        for _ in range(freq):
            best, best_score = None, 10**9
            for (d, lec) in all_slots:
                s = slot_score(cls, group, subj, teacher, room, d, lec)
                if s < best_score:
                    best, best_score = (d, lec), s
            if not best or best_score >= 1000:
                break

            d, lec = best
            used_slots_class.add((cls, group, d, lec))
            used_slots_teacher.add((teacher, d, lec))
            class_subjects_per_day[(cls, group, d)][subj] += 1

            assigned_room = None
            if room:
                key = (room, d, lec)
                used_rooms[key] += 1
                assigned_room = room

            timetable.append({
                "Day": d, "Lecture": lec, "Class": cls, "Group": group,
                "Subject": subj, "Teacher": teacher, "Room": assigned_room or ""
            })
            placed += 1

        if placed < freq:
            msg = f"⚠️ Could not place all {freq} lectures for {cls}-{group} {subj} ({teacher}). Placed: {placed}/{freq}"
            unplaced.append(msg)

    st.session_state["unplaced_lectures"] = unplaced
    for msg in unplaced:
        st.warning(msg)

    df_timetable = pd.DataFrame(timetable)
    if df_timetable.empty:
        return None, None, "No lectures could be scheduled. Please increase lectures per day or reduce frequency."

    df_timetable["Day"] = pd.Categorical(df_timetable["Day"], categories=days, ordered=True)
    df_timetable.sort_values(["Day", "Lecture", "Class", "Group"], inplace=True)

    os.makedirs("data", exist_ok=True)
    df_timetable.to_excel("data/Master_Timetable.xlsx", index=False)

    df_timetable["Details"] = (
        df_timetable["Subject"].astype(str)
        + " | " + df_timetable["Teacher"].astype(str)
        + " | " + df_timetable["Room"].astype(str)
    )

    pivot = df_timetable.pivot_table(
        index=["Day", "Class", "Group"], columns="Lecture",
        values="Details", aggfunc="first"
    ).reset_index()

    pivot["Day"] = pd.Categorical(pivot["Day"], categories=days, ordered=True)
    pivot.sort_values(["Day", "Class", "Group"], inplace=True)
    pivot.to_excel("data/Pivot_Timetable.xlsx", index=False)

    return df_timetable, pivot, None


# ======================
# Action Buttons
# ======================
col_b1, col_b2 = st.columns([1, 1])

with col_b1:
    btn_sched = st.button("📋 Generate Schedule Only", help="Assign teachers to sections without placing them into time slots")

with col_b2:
    btn_master = st.button("📅 Generate Master Timetable", type="primary", help="Generate full master timetable using Current Entries")

if btn_sched:
    if not st.session_state["subjects"]:
        st.warning("⚠️ Please add at least one subject before generating a schedule.")
    else:
        with st.spinner("Generating teacher assignments..."):
            df_result, err = generate_schedule_data(st.session_state["subjects"], num_sections)
            if err:
                st.error(f"❌ {err}")
            else:
                st.session_state["preview_schedule"] = df_result
                st.success("✅ Optimized teacher schedule generated successfully!")

if st.session_state.get("preview_schedule") is not None:
    st.subheader("📋 Teacher Assignment Schedule")
    st.dataframe(st.session_state["preview_schedule"])

if btn_master:
    st.session_state["unplaced_lectures"] = []
    df_sched = None

    # Priority: if Current Entries exist, ALWAYS generate fresh schedule from them
    if st.session_state["subjects"]:
        with st.spinner("Assigning selected teachers to sections..."):
            df_sched, err = generate_schedule_data(st.session_state["subjects"], num_sections)
            if err:
                st.error(f"❌ Schedule generation failed: {err}")
                st.stop()
            st.session_state["preview_schedule"] = df_sched
    elif os.path.exists("data/Final_Schedule.xlsx"):
        st.info("ℹ️ No entries in 'Current Entries'. Generating timetable from existing saved schedule (data/Final_Schedule.xlsx).")
        try:
            df_sched = pd.read_excel("data/Final_Schedule.xlsx")
        except Exception as e:
            st.error(f"❌ Could not read Final_Schedule.xlsx: {e}")
            st.stop()
    else:
        st.warning("⚠️ Please add at least one subject in 'Current Entries' first.")
        st.stop()

    if df_sched is not None:
        with st.spinner("Placing lectures and building master timetable..."):
            df_tt, pivot, err = generate_master_timetable_data(df_sched, num_lectures_per_day)
            if err:
                st.error(f"❌ {err}")
            else:
                st.session_state["generated_pivot"] = pivot
                st.success("✅ Master Timetable generated successfully with your selected teachers!")

if st.session_state.get("generated_pivot") is not None:
    pivot = st.session_state["generated_pivot"]
    st.subheader("📅 Master Timetable (Pivot View)")
    st.dataframe(pivot)
    excel_bytes = to_excel_bytes(pivot)
    st.download_button(
        label="⬇️ Download Pivot Timetable (Excel)",
        data=excel_bytes,
        file_name="Pivot_Timetable.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
