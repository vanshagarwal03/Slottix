import streamlit as st
import pandas as pd
from pathlib import Path

dark_css = """
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stApp { background-color: #1e1e2e !important; color: #cdd6f4 !important; }
        h1, h2, h3, h4, h5, h6, p, label, div { color: #cdd6f4 !important; }
        .stButton > button {
            background-color: #313244 !important;
            color: #cdd6f4 !important;
            border: 1px solid #585b70 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover {
            background-color: #45475a !important;
            border-color: #89b4fa !important;
            color: #ffffff !important;
            box-shadow: 0 0 12px rgba(137, 180, 250, 0.25) !important;
        }
        .stTextInput > div > div > input {
            background-color: #313244 !important;
            color: #cdd6f4 !important;
            border: 1px solid #585b70 !important;
            border-radius: 8px !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #89b4fa !important;
        }
    </style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# Page config
st.set_page_config(page_title="Slottix", page_icon="slottix_icon.png", layout="centered")


# Load user credentials from CSV
@st.cache_data
def load_users():
    """Load and normalize users from data/users.csv.

    Expected columns (case-insensitive): username, password, admin
    """
    csv_path = Path("data") / "users.csv"

    if not csv_path.exists():
        st.error(f"User database not found at: {csv_path.resolve()}")
        # Empty frame with required columns so code below still works
        return pd.DataFrame(columns=["username", "password", "admin"])

    # Try UTF-8 first, fall back to a Windows-friendly encoding.
    # Use the Python engine and skip bad lines so a stray comma doesn't break the app.
    try:
        df = pd.read_csv(
            csv_path,
            encoding="utf-8",
            engine="python",
            on_bad_lines="skip",
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            csv_path,
            encoding="latin1",
            engine="python",
            on_bad_lines="skip",
        )
    except Exception as e:
        st.error(f"Error reading user database: {e}")
        return pd.DataFrame(columns=["username", "password", "admin"])

    # Normalize column names (handle Username, USERNAME, etc.)
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Ensure required columns exist
    for col in ["username", "password", "admin"]:
        if col not in df.columns:
            df[col] = "" if col != "admin" else False

    # Strip whitespace and normalize
    df["username"] = df["username"].astype(str).str.strip().str.lower()
    df["password"] = df["password"].astype(str).str.strip()

    # Normalize admin flag to boolean
    df["admin"] = (
        df["admin"].astype(str).str.strip().str.lower().isin(["1", "true", "yes", "y"])
    )

    return df


users_df = load_users()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True


def login():
    """Check credentials against CSV and update session state."""
    # Read values safely from session_state
    raw_username = str(st.session_state.get("username", ""))
    raw_password = str(st.session_state.get("password", ""))

    # Normalize input to match how we normalized the CSV
    username = raw_username.strip().lower()
    password = raw_password.strip()

    if not username or not password:
        st.error("⚠️ Please enter both username and password")
        return

    # Match user
    user = users_df[
        (users_df["username"] == username) &
        (users_df["password"] == password)
    ]

    if not user.empty:
        st.session_state.logged_in = True
        st.session_state.is_admin = bool(user.iloc[0]["admin"])
        st.session_state.username = username  # store for use in other pages

        # Redirect based on role
        if st.session_state.is_admin:
            st.switch_page("pages/admin_landing_page.py")
        else:
            st.switch_page("pages/user_landing_page.py")
    else:
        st.error("❌ Invalid username or password")


# Show login form only if not logged in
if not st.session_state.logged_in:
    col_l1, col_l2, col_l3 = st.columns([1.2, 1.6, 1.2])
    with col_l2:
        st.image("slottix_logo.png", use_container_width=True)
    st.markdown("<p style='text-align: center; font-size: 1.35rem; font-weight: 600; margin: 5px 0 18px 0; color: #cdd6f4;'>🔑 Sign In</p>", unsafe_allow_html=True)
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password")
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    col_b1, col_b2, col_b3 = st.columns([1.35, 1.0, 1.35])
    with col_b2:
        st.button("Login", on_click=login, use_container_width=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    col_a1, col_a2, col_a3 = st.columns([1.0, 2.0, 1.0])
    with col_a2:
        if st.button("🏢 About Slottix & Services", use_container_width=True, key="btn_login_about"):
            st.switch_page("pages/about_slottix.py")

else:
    # Already logged in → redirect based on role
    if st.session_state.is_admin:
        st.switch_page("pages/admin_landing_page.py")
    else:
        st.switch_page("pages/user_landing_page.py")
