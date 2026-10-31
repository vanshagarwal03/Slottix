import streamlit as st
import pandas as pd
import os
import io
from collections import defaultdict

# =====================
# Streamlit Page Config
# =====================
st.set_page_config(
    page_title="Slottix",
    page_icon="slottix_icon.png",
    layout="wide"
)

# Hide sidebar
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# =====================
# Load Master Timetable
# =====================
timetable_path = "data/Master_Timetable.xlsx"
if not os.path.exists(timetable_path):
    st.error("❌ Master Timetable not found. Please generate it first.")
    st.stop()

df_timetable = pd.read_excel(timetable_path)
df_timetable["Room"] = df_timetable["Room"].fillna("")
df_timetable["Details"] = (
    df_timetable["Subject"].astype(str)
    + " | " + df_timetable["Teacher"].astype(str)
    + " | " + df_timetable["Room"].astype(str)
)

# =====================
# User Inputs
# =====================
days = df_timetable["Day"].unique().tolist()
selected_day = st.selectbox("Select Day", days)

all_teachers = df_timetable["Teacher"].unique().tolist()
absent_teachers = st.multiselect("Select Absent Teacher(s)", all_teachers)

day_df = df_timetable[df_timetable["Day"] == selected_day].copy()

# Always define new_timetable to avoid NameError
new_timetable = day_df.copy()

affected_lectures = day_df[day_df["Teacher"].isin(absent_teachers)]

if affected_lectures.empty:
    st.success("No lectures affected by absent teacher(s).")
else:
    st.warning(f"⚠️ Lectures affected by absent teacher(s) on {selected_day}:")
    st.dataframe(affected_lectures[["Lecture", "Class", "Group", "Subject", "Teacher", "Room"]])

    # =====================
    # Find Replacement Teachers
    # =====================
    # Mapping of subject -> teachers who teach that subject
    subject_teacher_map = defaultdict(set)
    for _, r in df_timetable.iterrows():
        subject_teacher_map[r["Subject"]].add(r["Teacher"])

    # Track initially busy teachers on selected_day
    teacher_busy = defaultdict(set)
    for _, row in day_df.iterrows():
        if row["Teacher"] not in absent_teachers:
            teacher_busy[row["Teacher"]].add(row["Lecture"])

    # Workload count per teacher on selected_day for fair distribution
    teacher_workload = defaultdict(int)
    for _, row in day_df.iterrows():
        if row["Teacher"] not in absent_teachers:
            teacher_workload[row["Teacher"]] += 1

    dynamic_busy = defaultdict(set)
    for t, lecs in teacher_busy.items():
        dynamic_busy[t] = set(lecs)

    dynamic_workload = defaultdict(int, teacher_workload)

    st.subheader("Select Replacement Teachers:")

    # Quick action buttons for convenience
    col_btn1, col_btn2, _ = st.columns([2, 2, 4])
    with col_btn1:
        if st.button("⚡ Auto Replace All", help="Automatically assign available teachers to all affected lectures"):
            for a_idx in affected_lectures.index:
                st.session_state[f"replace_{a_idx}"] = "Automatic replacement"
            st.rerun()
    with col_btn2:
        if st.button("🔄 Reset to No Replacement", help="Reset all replacements to No replacement"):
            for a_idx in affected_lectures.index:
                st.session_state[f"replace_{a_idx}"] = "No replacement"
            st.rerun()

    for idx, row in affected_lectures.iterrows():
        lecture = row["Lecture"]
        cls = row["Class"]
        group = row["Group"]
        subj = row["Subject"]
        room = row["Room"]

        available_teachers = [
            t for t in all_teachers
            if t not in absent_teachers and (lecture not in dynamic_busy[t] or t == st.session_state.get(f"replace_{idx}"))
        ]

        options = ["No replacement", "Automatic replacement"] + available_teachers

        selected_replacement = st.selectbox(
            f"Lecture {lecture} | {cls}-{group} | {subj} | Room: {room}",
            options=options,
            key=f"replace_{idx}"
        )

        if selected_replacement == "Automatic replacement":
            # Priority 1: Free teacher who teaches the same subject
            same_subj = [t for t in available_teachers if t in subject_teacher_map.get(subj, set())]
            candidates = same_subj if same_subj else available_teachers

            if candidates:
                # Priority 2: Teacher with minimum workload on this day
                auto_teacher = min(candidates, key=lambda t: (dynamic_workload[t], t))
                new_timetable.loc[new_timetable.index == idx, "Teacher"] = auto_teacher
                new_timetable.loc[new_timetable.index == idx, "Details"] = f"{subj} | {auto_teacher} | {room}"
                dynamic_busy[auto_teacher].add(lecture)
                dynamic_workload[auto_teacher] += 1
                st.info(f"🤖 **Auto-assigned:** `{auto_teacher}` for Lecture {lecture} ({cls}-{group} - {subj})")
            else:
                st.warning(f"⚠️ No free teacher available for Lecture {lecture} ({cls}-{group} - {subj}).")
        elif selected_replacement != "No replacement":
            new_timetable.loc[new_timetable.index == idx, "Teacher"] = selected_replacement
            new_timetable.loc[new_timetable.index == idx, "Details"] = f"{subj} | {selected_replacement} | {room}"
            dynamic_busy[selected_replacement].add(lecture)
            dynamic_workload[selected_replacement] += 1

# =====================
# Show Updated Timetable in Grid Format
# =====================
st.subheader(f"Updated Timetable (Grid) for {selected_day}:")

# Combine info for each lecture
new_timetable["Info"] = new_timetable["Subject"] + " | " + new_timetable["Teacher"] + " | " + new_timetable["Room"]

# Create Class_Group column
new_timetable["Class_Group"] = new_timetable["Class"].astype(str) + "-" + new_timetable["Group"].astype(str)

# Pivot table
grid_df = new_timetable.pivot_table(
    index="Class_Group",
    columns="Lecture",
    values="Info",
    aggfunc='first'
).fillna("")

# Sort columns numerically if possible
try:
    grid_df = grid_df.reindex(
        sorted(grid_df.columns, key=lambda x: int(str(x).replace('L','')) if str(x).replace('L','').isdigit() else x),
        axis=1
    )
except:
    pass

# Strip whitespace from index
grid_df.index = grid_df.index.str.strip()

# Highlight replaced teachers
def highlight_replacements(val):
    for absent in absent_teachers:
        if absent in str(val):
            return 'background-color: #ffcccc'  # Light red
    return ''

st.dataframe(grid_df.style.applymap(highlight_replacements))

# =====================
# Download Updated Timetable in Pivot Format
# =====================
st.subheader("Download Updated Timetable:")

output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    grid_df.to_excel(writer, sheet_name='Updated_Timetable')
output.seek(0)

st.download_button(
    label="📥 Download Excel",
    data=output,
    file_name=f"Updated_Timetable_{selected_day}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
