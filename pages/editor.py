import streamlit as st
import pandas as pd

st.set_page_config(page_title="Editor", page_icon="slottix_icon.png", layout="wide")

# Hide sidebar completely
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebarCollapsedControl"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Load timetable from Excel
df = pd.read_excel("data/Master_Timetable.xlsx")

# Select Class
classes = df['Class'].unique()
selected_class = st.selectbox("Select Class", classes)

# Filter dataframe for selected class
df_class = df[df['Class'] == selected_class]

# Sort days if they are weekdays
week_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
days = sorted(df_class['Day'].unique(), key=lambda x: week_order.index(x))
groups = sorted(df_class['Group'].unique())

st.title(f"Timetable for {selected_class}")

# Determine max number of lectures overall
max_lectures = df_class['Lecture'].max()

# Build full grid data including Teacher
grid_data = []
for day in days:
    day_df = df_class[df_class['Day'] == day]
    first_row_for_day = True
    for group in groups:
        group_df = day_df[day_df['Group'] == group].sort_values('Lecture')
        row = []
        # Add day name only for the first row of that day
        if first_row_for_day:
            row.append(day)
            first_row_for_day = False
        else:
            row.append("")  # empty cell for subsequent rows
        row.append(group)  # Group column
        for lecture_num in range(1, max_lectures + 1):
            lecture_info = group_df[group_df['Lecture'] == lecture_num]
            if not lecture_info.empty:
                subject = lecture_info['Subject'].values[0]
                teacher = lecture_info['Teacher'].values[0] if 'Teacher' in lecture_info.columns else ""
                row.append(f"{subject} ({teacher})")
            else:
                row.append("—")  # Empty slot
        grid_data.append(row)

# Create column names
columns = ["Day", "Group"] + [f"Lecture {i}" for i in range(1, max_lectures + 1)]

# Display full timetable as one table
st.table(pd.DataFrame(grid_data, columns=columns))
