import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Change Password", page_icon="slottix_icon.png", layout="centered")

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
    st.title("🔒 Change Password")
with col_logout:
    if st.button("🚪 Logout", key="logout"):
        st.session_state.clear()
        st.switch_page("login.py")

current_user = st.session_state.get("username", "")

if not current_user:
    st.error("⚠️ Could not identify the logged-in user. Please log out and log in again.")
    st.stop()

st.write(f"Changing password for: **{current_user}**")
st.divider()

CSV_PATH = Path("data/users.csv")

with st.form("change_password_form", clear_on_submit=True):
    current_password = st.text_input("Current Password", type="password")
    new_password     = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    submitted = st.form_submit_button("Update Password", type="primary")

if submitted:
    if not current_password or not new_password or not confirm_password:
        st.error("⚠️ Please fill in all fields.")
    elif new_password != confirm_password:
        st.error("❌ New passwords do not match.")
    elif len(new_password) < 4:
        st.error("❌ New password must be at least 4 characters long.")
    elif new_password == current_password:
        st.warning("⚠️ New password is the same as the current password.")
    else:
        try:
            # Load CSV with normalisation matching login.py
            try:
                df = pd.read_csv(CSV_PATH, encoding="utf-8", engine="python", on_bad_lines="skip")
            except UnicodeDecodeError:
                df = pd.read_csv(CSV_PATH, encoding="latin1", engine="python", on_bad_lines="skip")

            df.columns = [str(c).strip().lower() for c in df.columns]
            df["username"] = df["username"].astype(str).str.strip().str.lower()
            df["password"] = df["password"].astype(str).str.strip()

            user_mask = (df["username"] == current_user) & (df["password"] == current_password)

            if df[user_mask].empty:
                st.error("❌ Current password is incorrect.")
            else:
                df.loc[user_mask, "password"] = new_password
                df.to_csv(CSV_PATH, index=False)
                st.success("✅ Password updated successfully! Please log in again with the new password.")
        except Exception as e:
            st.error(f"❌ Error updating password: {e}")

st.divider()
back_page = "pages/admin_landing_page.py" if st.session_state.get("is_admin") else "pages/user_landing_page.py"
if st.button("⬅️ Back to Home"):
    st.switch_page(back_page)
