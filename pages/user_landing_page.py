import streamlit as st

st.set_page_config(page_title="Slottix - Home", page_icon="slottix_icon.png", layout="wide")

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

# ── Dark mode (shared preference) ───────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

if st.session_state["dark_mode"]:
    st.markdown("""
    <style>
        .stApp { background-color: #1e1e2e !important; color: #cdd6f4 !important; }
        h1, h2, h3, h4, h5, h6, p, label, div { color: #cdd6f4 !important; }
        .stButton > button {
            background-color: #313244 !important;
            color: #cdd6f4 !important;
            border: 1px solid #585b70 !important;
        }
        hr { border-color: #45475a !important; }
    </style>
    """, unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
col_title, col_spacer, col_theme, col_logout = st.columns([5, 3, 1, 1], vertical_alignment="center")
with col_title:
    c_logo, c_txt = st.columns([0.18, 0.82], vertical_alignment="center")
    with c_logo:
        st.image("slottix_icon.png", width=58)
    with c_txt:
        st.markdown("<h1 style='margin:0; line-height:1.1;'>Slottix</h1><small style='opacity:0.8;'>Smart Scheduling. Zero Clashes.</small>", unsafe_allow_html=True)
with col_spacer:
    username = st.session_state.get("username", "User")
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
st.header("🚀 Features")

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.subheader("📅 Timetable Viewer")
    st.write("View the complete timetable for any class, teacher, or day.")
    if st.button("Open", key="btn_viewer"):
        st.switch_page("pages/Timetable_Viewer.py")

with col2:
    st.subheader("📆 Day-wise Generator")
    st.write("Handle absent teachers and view updated day-wise timetables.")
    if st.button("Open", key="btn_daywise"):
        st.switch_page("pages/daywise_timetable_generator.py")

with col3:
    st.subheader("🔒 Change Password")
    st.write("Update your login password securely.")
    if st.button("Open", key="btn_pwd"):
        st.switch_page("pages/change_password.py")

st.write("")

col4, col5, col6 = st.columns(3, gap="large")

with col4:
    st.subheader("📚 My Lecture Summary")
    st.write("View your weekly and semester lecture counts per class and section.")
    if st.button("Open", key="btn_teacher_summary"):
        st.switch_page("pages/teacher_lecture_summary.py")

with col5:
    st.subheader("🏢 About Slottix")
    st.write("Product overview, services, team details, and institutional demo contact.")
    if st.button("Open", key="btn_about"):
        st.switch_page("pages/about_slottix.py")


st.divider()
