import streamlit as st
import pandas as pd
import os

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="DataBase Manager", page_icon="slottix_icon.png", layout="centered")

# Hide sidebar completely
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebarCollapsedControl"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# -----------------------------
# Folder path
# -----------------------------
folder_path = r"data/"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

st.title("📘 Database Manager")

# Allowed files
allowed_files = {"users.csv", "classes.xlsx", "faculty.xlsx", "Special_Classrooms.xlsx"}

# Get all matching files in the folder
excel_files = [f for f in os.listdir(folder_path) if f in allowed_files]

if not excel_files:
    st.warning("No matching files found in the folder.")
else:
    # -----------------------------
    # File selection
    # -----------------------------
    selected_file = st.selectbox("📂 Select a file", excel_files)
    file_path = os.path.join(folder_path, selected_file)

    # Load file
    try:
        if selected_file.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception:
        # Fallback columns
        if selected_file.lower() == "faculty.xlsx":
            df = pd.DataFrame(columns=["Faculty"])
        elif selected_file.lower() == "classes.xlsx":
            df = pd.DataFrame(columns=["Class", "Subject"])
        elif selected_file.lower() == "users.csv":
            df = pd.DataFrame(columns=["User"])
        elif selected_file.lower() == "special_classrooms.xlsx":
            df = pd.DataFrame(columns=["RoomType", "Count"])
        else:
            df = pd.DataFrame()

    # Determine columns dynamically
    columns = df.columns.tolist()

    # -----------------------------
    # Session state handling
    # -----------------------------
    if "selected_file_state" not in st.session_state or st.session_state.selected_file_state != selected_file:
        st.session_state.selected_file_state = selected_file
        st.session_state.edited_data = df.copy()

    st.subheader("📊 Current Data")
    st.write(f"Total Entries: {len(st.session_state.edited_data)}")
    st.dataframe(st.session_state.edited_data)

    # -----------------------------
    # ➕ Add new entry
    # -----------------------------
    st.subheader("➕ Add New Entry")

    new_row_values = []
    for col in columns:
        if col.lower() == "count":
            val = st.number_input(f"Enter {col}", min_value=1, step=1, key=f"input_{col}")
        else:
            val = st.text_input(f"Enter {col}", key=f"input_{col}")
        new_row_values.append(val)

    if st.button("Add Entry", key="add_entry"):
        if all(v not in [None, ""] for v in new_row_values):
            new_row = pd.DataFrame([new_row_values], columns=columns)
            st.session_state.edited_data = pd.concat(
                [st.session_state.edited_data, new_row], ignore_index=True
            )
            st.success(f"✅ Added new entry (Pending Save)")
        else:
            st.warning("⚠ Please fill all fields.")

    # -----------------------------
    # 🗑 Delete entry
    # -----------------------------
    st.subheader("🗑 Delete Entry")
    if not st.session_state.edited_data.empty:
        row_to_delete = st.number_input(
            f"Enter row number to delete (0 to {len(st.session_state.edited_data)-1})",
            min_value=0,
            max_value=len(st.session_state.edited_data)-1,
            step=1,
            key="delete_row_input"
        )
        if st.button("Delete Row", key="delete_button"):
            st.session_state.edited_data = st.session_state.edited_data.drop(row_to_delete).reset_index(drop=True)
            st.success(f"✅ Deleted row {row_to_delete} (Pending Save)")

    # -----------------------------
    # 💾 Save changes
    # -----------------------------
    st.subheader("💾 Save Changes")
    if not st.session_state.edited_data.empty:
        if st.button("Save Changes", key="save_changes"):
            try:
                if selected_file.endswith(".csv"):
                    st.session_state.edited_data.to_csv(file_path, index=False)
                else:
                    st.session_state.edited_data.to_excel(file_path, index=False)
                st.success(f"✅ All changes saved to {selected_file}")
                st.rerun()  # Refresh view
            except Exception as e:
                st.error(f"⚠ Error saving file: {e}\nMake sure the file is closed in Excel.")
    else:
        st.info("⚠ No data to save.")
