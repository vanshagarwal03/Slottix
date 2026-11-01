import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# Page configuration
st.set_page_config(page_title="About Slottix", page_icon="slottix_icon.png", layout="wide")

hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebarCollapsedControl"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Dark mode styling
dark_css = """
<style>
    .stApp { background-color: #1e1e2e !important; color: #cdd6f4 !important; }
    h1, h2, h3, h4, h5, h6, p, label, div, span { color: #cdd6f4 !important; }
    .card-box {
        background-color: #262738;
        border: 1px solid #45475a;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .card-box:hover {
        border-color: #89b4fa;
        transform: translateY(-2px);
    }
    .badge-pill {
        background-color: #313244;
        color: #89b4fa !important;
        border: 1px solid #89b4fa;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }
    .stButton > button {
        background-color: #313244 !important;
        color: #cdd6f4 !important;
        border: 1px solid #585b70 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        background-color: #45475a !important;
        border-color: #89b4fa !important;
        color: #ffffff !important;
    }
    [data-testid="stImage"] img {
        filter: drop-shadow(0 0 25px rgba(0, 168, 255, 0.25));
        transition: transform 0.3s ease;
    }
    [data-testid="stImage"] img:hover {
        transform: scale(1.02);
    }
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# ── Top Back Button Bar ───────────────────────────────────────────────────────
col_empty, col_back = st.columns([8, 2])
with col_back:
    if st.button("⬅️ Back to Home", use_container_width=True):
        if st.session_state.get("logged_in"):
            if st.session_state.get("is_admin"):
                st.switch_page("pages/admin_landing_page.py")
            else:
                st.switch_page("pages/user_landing_page.py")
        else:
            st.switch_page("login.py")

# ── Header with 3D Glowing Logo ──────────────────────────────────────────────
col_l1, col_l2, col_l3 = st.columns([1.5, 2.5, 1.5])
with col_l2:
    try:
        st.image("slottix_3d_logo_blended.png", use_container_width=True)
    except Exception:
        try:
            st.image("slottix_3d_logo.jpg", use_container_width=True)
        except Exception:
            st.image("slottix_logo.png", use_container_width=True)

st.divider()

# ── Section 1: About the Product ──────────────────────────────────────────────
st.markdown("<span class='badge-pill'>ABOUT THE PRODUCT</span>", unsafe_allow_html=True)
st.markdown("### Intelligent Academic Scheduling Platform")
st.write(
    "**Slottix** is an intelligent, AI-powered academic scheduling platform designed to eliminate "
    "timetable clashes and streamline daily teacher proxy management for educational institutions. "
    "By combining advanced mathematical constraint optimization with an intuitive web interface, Slottix transforms "
    "the weeks of tedious manual scheduling into an accurate, conflict-free, 30-second automated process."
)

st.write("")
col_f1, col_f2, col_f3 = st.columns(3, gap="medium")
with col_f1:
    st.markdown("""
    <div class="card-box">
        <h4 style="margin-top:0;">⚡ 100% Conflict-Free Scheduling</h4>
        <p style="font-size:0.92rem; color:#bac2de !important;">
            Powered by Google OR-Tools constraint satisfaction algorithms. Simultaneously evaluates faculty availability, 
            student sections, and room capacities to guarantee zero double-bookings.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown("""
    <div class="card-box">
        <h4 style="margin-top:0;">🤖 1-Click Smart Substitution</h4>
        <p style="font-size:0.92rem; color:#bac2de !important;">
            Instantly detects affected lectures when a faculty member takes leave, matches available teachers by subject expertise, 
            balances daily workload, and assigns proxies with zero disruption.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown("""
    <div class="card-box">
        <h4 style="margin-top:0;">📊 Workload & Lab Analytics</h4>
        <p style="font-size:0.92rem; color:#bac2de !important;">
            Transparent workload dashboards to prevent teacher burnout and color-coded heatmaps to maximize computer lab, 
            auditorium, and seminar hall utilization.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Section 2: Our Services & Solutions ───────────────────────────────────────
st.markdown("<span class='badge-pill'>OUR SERVICES & SOLUTIONS</span>", unsafe_allow_html=True)
st.markdown("### What We Offer to Institutions")

col_s1, col_s2 = st.columns(2, gap="medium")
with col_s1:
    st.markdown("""
    <div class="card-box">
        <h4 style="margin-top:0;">🗓️ Automated Master Timetable Scheduling</h4>
        <p style="font-size:0.95rem; color:#bac2de !important;">
            Complete clash-free master schedule generation for multiple classes, sections (A, B, C, D), 
            and laboratories in under 2 minutes.
        </p>
    </div>
    <div class="card-box">
        <h4 style="margin-top:0;">🎁 14-Day Free Institutional Pilot</h4>
        <p style="font-size:0.95rem; color:#bac2de !important;">
            Experience Slottix with zero financial risk. Share your department's subject-faculty list, 
            and we will configure and generate your upcoming semester timetable for free.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_s2:
    st.markdown("""
    <div class="card-box">
        <h4 style="margin-top:0;">🔄 Dynamic Faculty Substitution</h4>
        <p style="font-size:0.95rem; color:#bac2de !important;">
            Real-time daily proxy management system that prevents empty classrooms and maintains 
            smooth academic continuity.
        </p>
    </div>
    <div class="card-box">
        <h4 style="margin-top:0;">👥 Academic Coordinator Guidance</h4>
        <p style="font-size:0.95rem; color:#bac2de !important;">
            Hands-on walkthrough and assistance to help your timetable coordinators import data, 
            manage section batches, and operate the platform effortlessly.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Section 3: Core Team ───────────────────────────────────────────────────────
st.markdown("<span class='badge-pill'>THE TEAM</span>", unsafe_allow_html=True)
st.markdown("### Core Leadership")

col_t1, col_t2, col_t3 = st.columns(3, gap="medium")
with col_t1:
    st.markdown("""
    <div class="card-box" style="text-align: center;">
        <h3 style="margin-bottom: 4px;">👤 Vansh Agrawal</h3>
        <p style="color: #89b4fa !important; font-weight: 600; font-size: 0.95rem; margin-top: 0;">Team Leader & Product Lead</p>
    </div>
    """, unsafe_allow_html=True)

with col_t2:
    st.markdown("""
    <div class="card-box" style="text-align: center;">
        <h3 style="margin-bottom: 4px;">👤 Ankit Kumar</h3>
        <p style="color: #89b4fa !important; font-weight: 600; font-size: 0.95rem; margin-top: 0;">Marketing & Creative Lead</p>
    </div>
    """, unsafe_allow_html=True)

with col_t3:
    st.markdown("""
    <div class="card-box" style="text-align: center;">
        <h3 style="margin-bottom: 4px;">👤 Salman Rajput</h3>
        <p style="color: #89b4fa !important; font-weight: 600; font-size: 0.95rem; margin-top: 0;">Testing & Quality Assurance</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Section 4: Contact & Demo Inquiries ───────────────────────────────────────
st.markdown("<span class='badge-pill'>GET IN TOUCH</span>", unsafe_allow_html=True)
st.markdown("### Contact & Demo Inquiries")
st.write("For institutional inquiries, live software walkthroughs, or activating your **14-Day Free Pilot**, reach out directly:")

col_c1, col_c2 = st.columns([1, 1.3], gap="large")

with col_c1:
    st.markdown("""
    <div class="card-box">
        <h4 style="margin-top:0;">📞 Direct Call / WhatsApp</h4>
        <p style="font-size:1.15rem; font-weight:700; color:#89b4fa !important; margin: 8px 0;">+91 7310976931</p>
        <p style="font-size:0.88rem; color:#a6adc8 !important;">Available Monday to Saturday for demo requests, faculty discussions, and support.</p>
    </div>
    <div class="card-box">
        <h4 style="margin-top:0;">✉️ Official Email</h4>
        <p style="font-size:1.1rem; font-weight:700; color:#89b4fa !important; margin: 8px 0;">agarwalvansh061@gmail.com</p>
        <p style="font-size:0.88rem; color:#a6adc8 !important;">Write to us with your department details for a customized demo schedule.</p>
    </div>
    """, unsafe_allow_html=True)

with col_c2:
    st.markdown("""
    <div class="card-box">
        <h4 style="margin-top:0; margin-bottom: 15px;">📝 Request a 15-Minute Live Demo</h4>
    """, unsafe_allow_html=True)

    with st.form("demo_request_form", clear_on_submit=True):
        req_name = st.text_input("Your Name *", placeholder="e.g. Dr. Sharma / Coordinator")
        req_inst = st.text_input("Institution / College Name *", placeholder="e.g. ABC College of Engineering")
        
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            req_phone = st.text_input("Phone / WhatsApp *", placeholder="+91 9876543210")
        with col_sub2:
            req_email = st.text_input("Official Email *", placeholder="coordinator@college.edu")
            
        req_notes = st.text_area("Message / Specific Requirements", placeholder="Mention department name, number of sections, or preferred demo timings...")
        
        submit_btn = st.form_submit_button("🚀 Submit Demo Request", use_container_width=True)
        if submit_btn:
            if not req_name or not req_inst or not req_phone:
                st.error("⚠️ Please fill in all required fields (Name, Institution, Phone).")
            else:
                req_path = Path("data") / "demo_requests.csv"
                req_data = {
                    "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Name": [req_name],
                    "Institution": [req_inst],
                    "Phone": [req_phone],
                    "Email": [req_email],
                    "Message": [req_notes]
                }
                new_df = pd.DataFrame(req_data)
                if req_path.exists():
                    new_df.to_csv(req_path, mode="a", header=False, index=False)
                else:
                    new_df.to_csv(req_path, mode="w", header=True, index=False)
                st.success("✅ Thank you! Your demo request has been received. Team Slottix will connect with you shortly.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
