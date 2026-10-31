import streamlit as st

st.set_page_config(page_title="Slottix - Admin", page_icon="slottix_icon.png", layout="wide")

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

# ── Dark mode toggle (CSS injection) ─────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

if st.session_state["dark_mode"]:
    st.markdown("""
    <style>
        .stApp { background-color: #1e1e2e !important; color: #cdd6f4 !important; }
        h1, h2, h3, h4, h5, h6, p, label, div {
            color: #cdd6f4 !important;
        }
        .stButton > button {
            background-color: #313244 !important;
            color: #cdd6f4 !important;
            border: 1px solid #585b70 !important;
        }
        hr { border-color: #45475a !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: #ffffff !important; color: #1a1a1a !important; }
        h1, h2, h3, h4, h5, h6, p, label, div {
            color: #1a1a1a !important;
        }
        .stButton > button {
            background-color: #f0f2f6 !important;
            color: #1a1a1a !important;
            border: 1px solid #d0d7de !important;
        }
        hr { border-color: #e0e0e0 !important; }
    </style>
    """, unsafe_allow_html=True)

# ── Top bar: title · username · dark-mode toggle · logout ────────────────────
col_title, col_spacer, col_theme, col_logout = st.columns([5, 3, 1, 1], vertical_alignment="center")
with col_title:
    c_logo, c_txt = st.columns([0.18, 0.82], vertical_alignment="center")
    with c_logo:
        st.image("slottix_icon.png", width=58)
    with c_txt:
        st.markdown("<h1 style='margin:0; line-height:1.1;'>Slottix</h1><small style='opacity:0.8;'>Smart Scheduling. Zero Clashes.</small>", unsafe_allow_html=True)
with col_spacer:
    username = st.session_state.get("username", "Admin")
    st.markdown(f"<br><span style='font-size:1rem;'>👤 {username}</span>", unsafe_allow_html=True)
with col_theme:
    theme_label = "☀️ Light" if st.session_state["dark_mode"] else "🌙 Dark"
    if st.button(theme_label, key="theme_toggle"):
        st.session_state["dark_mode"] = not st.session_state["dark_mode"]
        st.rerun()
with col_logout:
    if st.button("🚪 Logout", key="logout"):
        st.session_state.clear()
        st.switch_page("login.py")

st.divider()

# ── Features section ──────────────────────────────────────────────────────────
st.header("🚀 Features")

# Row 1 ── Core tools
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.subheader("🗄️ Database Manager")
    st.write("Manage subjects, teachers, and classes. Centralized data storage.")
    if st.button("Open", key="btn_db"):
        st.switch_page("pages/database_manager.py")

with col2:
    st.subheader("🗂️ Master Timetable Generator")
    st.write("Generate and export the full timetable with conflict-aware scheduling.")
    if st.button("Open", key="btn_master"):
        st.switch_page("pages/master_generator.py")

with col3:
    st.subheader("📅 Timetable Viewer")
    st.write("View the timetable by class, teacher, or day with group filtering.")
    if st.button("Open", key="btn_viewer"):
        st.switch_page("pages/Timetable_Viewer.py")

st.write("")

# Row 2 ── Analytics & validation
col4, col5, col6 = st.columns(3, gap="large")

with col4:
    st.subheader("📊 Teacher Workload")
    st.write("Bar chart and day-wise breakdown of lectures assigned per teacher.")
    if st.button("Open", key="btn_workload"):
        st.switch_page("pages/teacher_workload.py")

with col5:
    st.subheader("⚠️ Conflict Detector")
    st.write("Scan for teacher double-bookings, class clashes, and room over-use.")
    if st.button("Open", key="btn_conflict"):
        st.switch_page("pages/conflict_detector.py")

with col6:
    st.subheader("🔍 Free Period Finder")
    st.write("Look up all free slots for any teacher or class group.")
    if st.button("Open", key="btn_free"):
        st.switch_page("pages/free_period_finder.py")

st.write("")

# Row 3 ── Room, account, day tools
col7, col8, col9 = st.columns(3, gap="large")

with col7:
    st.subheader("🏫 Room Utilization")
    st.write("Colour-coded heatmap of special room usage across all slots.")
    if st.button("Open", key="btn_room"):
        st.switch_page("pages/room_utilization.py")

with col8:
    st.subheader("📆 Day-wise Generator")
    st.write("Handle absent teachers and generate updated day-wise timetables.")
    if st.button("Open", key="btn_daywise"):
        st.switch_page("pages/daywise_timetable_generator.py")

with col9:
    st.subheader("🔒 Change Password")
    st.write("Update your login password securely from within the app.")
    if st.button("Open", key="btn_pwd"):
        st.switch_page("pages/change_password.py")

st.write("")

# Row 4 ── Teacher self-service
col10, col11, col12 = st.columns(3, gap="large")

with col10:
    st.subheader("📚 Teacher Lecture Summary")
    st.write(
        "Weekly and semester-total lecture counts per teacher, "
        "broken down by class and section."
    )
    if st.button("Open", key="btn_teacher_summary"):
        st.switch_page("pages/teacher_lecture_summary.py")

st.divider()
