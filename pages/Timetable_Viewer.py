import streamlit as st
import pandas as pd

st.set_page_config(page_title="Slottix - Timetable Viewer", page_icon="slottix_icon.png", layout="wide")

# Hide sidebar
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Load the timetable
@st.cache_data
def load_data():
    df = pd.read_excel('data/Master_Timetable.xlsx')
    return df

df = load_data()

st.title("📅 Timetable Viewer with Tabs and Group Filter")

# Always allow multi-select for groups
all_groups = sorted(df['Group'].dropna().unique())
selected_groups = st.multiselect("Select Group(s)", options=all_groups, default=all_groups)

# Filter by selected groups
df = df[df['Group'].isin(selected_groups)]

# Days order for proper grid
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Helper to create grid-like timetable
def create_timetable(data, value_col):
    timetable = data.pivot_table(
        index="Day",
        columns="Lecture",
        values=value_col,
        aggfunc=lambda x: ' | '.join(str(i) for i in x if pd.notnull(i))
    )
    timetable = timetable.reindex(days_order).dropna(how="all")
    return timetable

def get_room_str(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    return "" if s.lower() in ["", "nan", "none"] else s

def format_class_details(row):
    subj = str(row['Subject']) if pd.notnull(row['Subject']) else ''
    grp = str(row['Group']).strip() if pd.notnull(row['Group']) else ''
    teacher = str(row['Teacher']) if pd.notnull(row['Teacher']) else ''
    room = get_room_str(row.get('Room'))
    
    grp_str = f"[Group {grp}] " if grp and grp.lower() not in ['nan', 'none'] else ""
    room_str = f" (Room: {room})" if room else ""
    return f"{grp_str}{subj}{room_str} - {teacher}"

def format_teacher_details(row):
    cls = str(row['Class']) if pd.notnull(row['Class']) else ''
    subj = str(row['Subject']) if pd.notnull(row['Subject']) else ''
    grp = str(row['Group']).strip() if pd.notnull(row['Group']) else ''
    room = get_room_str(row.get('Room'))
    
    parts = []
    if grp and grp.lower() not in ['nan', 'none']:
        parts.append(f"Group {grp}")
    if room:
        parts.append(f"Room: {room}")
    
    extra = f" ({' | '.join(parts)})" if parts else ""
    base = " - ".join([p for p in [cls, subj] if p])
    return f"{base}{extra}"

def format_day_details(row):
    cls = str(row['Class']) if pd.notnull(row['Class']) else ''
    grp = str(row['Group']).strip() if pd.notnull(row['Group']) else ''
    subj = str(row['Subject']) if pd.notnull(row['Subject']) else ''
    teacher = str(row['Teacher']) if pd.notnull(row['Teacher']) else ''
    room = get_room_str(row.get('Room'))
    
    cls_grp = f"{cls} (Group {grp})" if grp and grp.lower() not in ['nan', 'none'] else cls
    room_str = f" [Room: {room}]" if room else ""
    return f"{cls_grp} - {subj}{room_str} - {teacher}"

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Class-wise", "Teacher-wise", "Day-wise"])

with tab1:
    st.header("📚 View by Class")
    classes = df['Class'].unique()
    selected_class = st.selectbox("Select Class", sorted(classes))
    filtered_df = df[df['Class'] == selected_class].copy()

    # Combine details for display
    filtered_df["Details"] = filtered_df.apply(format_class_details, axis=1)

    st.subheader(f"Timetable for Class: {selected_class} and Groups: {', '.join(selected_groups)}")
    if not filtered_df.empty:
        timetable = create_timetable(filtered_df, "Details")
        st.dataframe(timetable)
    else:
        st.write("No data available for this selection.")

with tab2:
    st.header("👨‍🏫 View by Teacher")
    teachers = df['Teacher'].dropna().unique()
    selected_teacher = st.selectbox("Select Teacher", sorted(teachers))
    filtered_df = df[df['Teacher'] == selected_teacher].copy()

    filtered_df["Details"] = filtered_df.apply(format_teacher_details, axis=1)

    st.subheader(f"Timetable for Teacher: {selected_teacher} and Groups: {', '.join(selected_groups)}")
    if not filtered_df.empty:
        timetable = create_timetable(filtered_df, "Details")
        st.dataframe(timetable)
    else:
        st.write("No data available for this selection.")

with tab3:
    st.header("📆 View by Day")
    days = df['Day'].unique()
    sorted_days = sorted(days, key=lambda d: days_order.index(d))
    selected_day = st.selectbox("Select Day", sorted_days)
    filtered_df = df[df['Day'] == selected_day].copy()

    filtered_df["Details"] = filtered_df.apply(format_day_details, axis=1)

    st.subheader(f"Timetable for Day: {selected_day} and Groups: {', '.join(selected_groups)}")
    if not filtered_df.empty:
        timetable = filtered_df.pivot_table(
            index="Lecture",
            values="Details",
            aggfunc=lambda x: ' | '.join(str(i) for i in x if pd.notnull(i))
        )
        st.dataframe(timetable)
    else:
        st.write("No data available for this selection.")
