import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Teacher Lecture Summary", page_icon="slottix_icon.png", layout="wide")

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

# ── Header ───────────────────────────────────────────────────────────────────
col_title, col_logout = st.columns([9, 1])
with col_title:
    st.title("📚 Teacher Lecture Summary")
with col_logout:
    if st.button("🚪 Logout", key="logout"):
        st.session_state.clear()
        st.switch_page("login.py")

st.caption("See how many lectures a teacher delivers each week and across the full semester, broken down by class and section.")

TIMETABLE_PATH = "data/Master_Timetable.xlsx"

if not os.path.exists(TIMETABLE_PATH):
    st.error("❌ Master Timetable not found. Please generate it first.")
    if st.button("⬅️ Back to Home"):
        back = "pages/admin_landing_page.py" if st.session_state.get("is_admin") else "pages/user_landing_page.py"
        st.switch_page(back)
    st.stop()

df = pd.read_excel(TIMETABLE_PATH)

# ── Controls ──────────────────────────────────────────────────────────────────
all_teachers = sorted(df["Teacher"].dropna().unique())

ctrl_col1, ctrl_col2 = st.columns([3, 1])
with ctrl_col1:
    selected_teacher = st.selectbox("👤 Select Teacher", all_teachers)
with ctrl_col2:
    num_weeks = st.number_input(
        "📆 Weeks in Semester",
        min_value=1, max_value=52, value=16, step=1,
        help="Used to calculate total semester lectures (weekly count × weeks)."
    )

st.divider()

# ── Filter to selected teacher ────────────────────────────────────────────────
tdf = df[df["Teacher"] == selected_teacher].copy()

if tdf.empty:
    st.warning(f"⚠️ No lectures found for **{selected_teacher}** in the timetable.")
    st.stop()

# ── Weekly lecture count per Class / Group / Subject ─────────────────────────
summary = (
    tdf.groupby(["Class", "Group", "Subject"])
    .size()
    .reset_index(name="Lectures / Week")
    .sort_values(["Class", "Group", "Subject"])
    .reset_index(drop=True)
)
summary["Total (Semester)"] = summary["Lectures / Week"] * num_weeks

# ── Top-level metrics ─────────────────────────────────────────────────────────
total_weekly     = int(summary["Lectures / Week"].sum())
total_semester   = int(summary["Total (Semester)"].sum())
unique_classes   = summary["Class"].nunique()
unique_sections  = summary[["Class", "Group"]].drop_duplicates().shape[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Unique Classes",   unique_classes)
m2.metric("Unique Sections",  unique_sections)
m3.metric("Lectures / Week",  total_weekly)
m4.metric(f"Total (× {num_weeks} wks)", total_semester)

st.subheader(f"📋 Breakdown for {selected_teacher}")
st.dataframe(summary, use_container_width=True, hide_index=True)

# ── Per-class totals (collapsible) ────────────────────────────────────────────
with st.expander("📊 Per-Class Weekly Totals (bar chart)", expanded=True):
    per_class = (
        summary.groupby("Class")["Lectures / Week"]
        .sum()
        .reset_index()
        .sort_values("Lectures / Week", ascending=False)
    )
    st.bar_chart(per_class.set_index("Class")["Lectures / Week"])

# ── Per-section pivot ─────────────────────────────────────────────────────────
with st.expander("🗂️ Per-Section Pivot (Classes as columns, Sections as rows)"):
    pivot_weekly = summary.pivot_table(
        index="Group", columns="Class",
        values="Lectures / Week", aggfunc="sum", fill_value=0
    )
    pivot_semester = pivot_weekly * num_weeks

    tab_w, tab_s = st.tabs(["Weekly", f"Semester (× {num_weeks} weeks)"])
    with tab_w:
        st.dataframe(pivot_weekly, use_container_width=True)
    with tab_s:
        st.dataframe(pivot_semester, use_container_width=True)

# ── Day-wise schedule ─────────────────────────────────────────────────────────
with st.expander("📅 Weekly Schedule (Day × Lecture slot)", expanded=True):
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    tdf["Slot Info"] = (
        tdf["Class"].astype(str) + "-" + tdf["Group"].astype(str)
        + " | " + tdf["Subject"].astype(str)
    )

    schedule_pivot = tdf.pivot_table(
        index="Day", columns="Lecture",
        values="Slot Info",
        aggfunc=lambda x: "\n".join(sorted(set(x)))
    )

    available_days = [d for d in days_order if d in schedule_pivot.index]
    schedule_pivot = schedule_pivot.reindex(available_days)

    st.caption("Each cell shows: Class-Section | Subject")
    st.dataframe(schedule_pivot, use_container_width=True)

st.divider()
back_page = "pages/admin_landing_page.py" if st.session_state.get("is_admin") else "pages/user_landing_page.py"
if st.button("⬅️ Back to Home"):
    st.switch_page(back_page)
