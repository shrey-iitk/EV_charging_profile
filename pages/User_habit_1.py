import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import os
from scenario.combine_2 import generate_EV_profiles

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(page_title="EV Charging User Habit", layout="wide")
st.title("EV Charging User Habit")

# --------------------------------------------------
# Session State Initialization
# --------------------------------------------------
default_states = {
    "pdf_done": False,
    "sim_done": False,
    "weekday_start_pdf": None,
    "season_start_pdf": None,
    "P_total": None,
    "Q_total": None,
    "start_points": None,
    "end_points": None,
    "selected_profiles": [],
    "selected_dataset": None,
    "weekday": None,
    "season": None,
    "N": None
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# Helper Function
# --------------------------------------------------
def get_year_range(csv_path):
    try:
        df_tmp = pd.read_csv(csv_path, parse_dates=[0])
        years = df_tmp.iloc[:, 0].dt.year
        return int(years.min()), int(years.max())
    except Exception:
        return None, None

# --------------------------------------------------
# Sidebar — Dataset Selection
# --------------------------------------------------
st.sidebar.header("📁 Data Selection")

# Project root = folder containing "pages"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_folder = os.path.join(BASE_DIR, "user_profiles")
profile_folder = os.path.join(BASE_DIR, "data")

if not os.path.isdir(data_folder):
    st.error(f"user_profiles folder not found: {data_folder}")
    st.stop()

if not os.path.isdir(profile_folder):
    st.error(f"data folder not found: {profile_folder}")
    st.stop()

available_datasets = [
    f for f in os.listdir(data_folder)
    if f.lower().endswith(".csv")
]

dataset_info = {}
for file in available_datasets:
    y_start, y_end = get_year_range(os.path.join(data_folder, file))
    dataset_info[file] = f"{file} ({y_start}–{y_end})" if y_start else f"{file} (Year Unknown)"

selected_label = st.sidebar.selectbox("Select Dataset", dataset_info.values())
selected_dataset = [k for k, v in dataset_info.items() if v == selected_label][0]

pdf_button = st.sidebar.button("📊 Generate Behavior PDFs")

# --------------------------------------------------
# STEP 1 — GENERATE PDFs
# --------------------------------------------------
if pdf_button:
    df_raw = pd.read_csv(os.path.join(data_folder, selected_dataset))

    all_profiles = [
        os.path.join(profile_folder, f)
        for f in os.listdir(profile_folder)
        if f.startswith("prediction_SOC") and f.endswith(".csv")
    ]

    weekday_start_pdf, season_start_pdf, *_ = generate_EV_profiles(
        df_raw=df_raw,
        profile_files=all_profiles,
        N=50,
        weekday=0,
        season="Summer"
    )

    st.session_state.update({
        "pdf_done": True,
        "weekday_start_pdf": weekday_start_pdf,
        "season_start_pdf": season_start_pdf,
        "selected_dataset": selected_dataset
    })


# --------------------------------------------------
# DISPLAY PDFs
# --------------------------------------------------
if st.session_state["pdf_done"]:
    st.caption(
    f"Last run:  Dataset: {st.session_state['selected_dataset']}"
    )
    

    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = np.arange(24)

    weekday_start_pdf = st.session_state["weekday_start_pdf"]
    season_start_pdf = st.session_state["season_start_pdf"]

    df_weekday_pdf = pd.DataFrame([
        {"Weekday": weekday_names[wd], "Hour": hr, "Probability": weekday_start_pdf[wd][hr]}
        for wd in range(7) for hr in hours
    ])

    df_season_pdf = pd.DataFrame([
        {"Season": s, "Hour": hr, "Probability": season_start_pdf[s][hr]}
        for s in season_start_pdf.keys() for hr in hours
    ])

      # --------------------------------------------------
    # WEEKDAY PDF PLOT
    # --------------------------------------------------
    hours = np.arange(24)
    df_weekday_pdf = pd.DataFrame([
        {"Weekday": weekday_names[wd], "Hour": hr, "Probability": weekday_start_pdf[wd][hr]}
        for wd in range(7) for hr in hours
    ])

    st.subheader("⏱️ Charging Start PDF by Weekday")
    fig_wd = px.line(df_weekday_pdf, x="Hour", y="Probability", color="Weekday")
    fig_wd.update_traces(line=dict(width=3))

    fig_wd.update_layout(
    # title_font_size=26,
    # title_font_color="green",
    xaxis_title_font_size=18,
    xaxis_title_font_color="black",
    yaxis_title_font_size=18,
    yaxis_title_font_color="black",
    xaxis_tickfont_size=14,
    xaxis_tickfont_color="black",
    yaxis_tickfont_size=14,
    yaxis_tickfont_color="black", hovermode="x unified")
    st.plotly_chart(fig_wd, use_container_width=True)

    # --------------------------------------------------
    # SEASON PDF PLOT
    # --------------------------------------------------
    df_season_pdf = pd.DataFrame([
        {"Season": s, "Hour": hr, "Probability": season_start_pdf[s][hr]}
        for s in season_start_pdf.keys() for hr in hours
    ])

    st.subheader("🌦️ Charging Start PDF by Season")
    fig_season = px.line(df_season_pdf, x="Hour", y="Probability", color="Season")
    fig_season.update_traces(line=dict(width=3))

    fig_season.update_layout(
    # title_font_size=26,
    # title_font_color="green",
    xaxis_title_font_size=18,
    xaxis_title_font_color="black",
    yaxis_title_font_size=18,
    yaxis_title_font_color="black",
    xaxis_tickfont_size=14,
    xaxis_tickfont_color="black",
    yaxis_tickfont_size=14,
    yaxis_tickfont_color="black", hovermode="x unified")

    st.plotly_chart(fig_season, use_container_width=True)

    st.markdown("---")
# --------------------------------------------------
# STEP 2 — SIMULATION CONTROLS
# --------------------------------------------------
if st.session_state["pdf_done"]:

    st.header("⚡ Step 2: Grid Load Simulation")

    col1, col2, col3, col4 = st.columns(4)
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    with col1:
        weekday_str = st.selectbox("Weekday", weekday_names)
        weekday = weekday_names.index(weekday_str)

    with col2:
        season = st.selectbox("Season", ["Winter", "Summer", "Monsoon", "Autumn"])

    with col3:
        N = st.number_input("Number of EVs (N)", 1, 1000, 10)

    with col4:
        available_profiles = sorted([
            f for f in os.listdir(profile_folder)
            if f.startswith("prediction_SOC") and f.endswith(".csv")
        ])
        selected_profile_files = st.multiselect("SOC Profiles", available_profiles, default=available_profiles[:3])

    simulate_button = st.button("🚀 Run Simulation")


# --------------------------------------------------
# RUN SIMULATION
# --------------------------------------------------
if st.session_state["pdf_done"] and simulate_button:

    df_raw = pd.read_csv(os.path.join(data_folder, st.session_state["selected_dataset"]))
    profile_files = [os.path.join(profile_folder, f) for f in selected_profile_files]

    if not profile_files:
        st.error("Please select at least one SOC profile.")
        st.stop()

    (_, _, P_total, Q_total,
     start_points, end_points,
     used_profiles) = generate_EV_profiles(
        df_raw=df_raw,
        profile_files=profile_files,
        N=N,
        weekday=weekday,
        season=season
    )

    st.session_state.update({
        "sim_done": True,
        "P_total": P_total,
        "Q_total": Q_total,
        "start_points": start_points,
        "end_points": end_points,
        "selected_profiles": used_profiles,
        "weekday": weekday,
        "season": season,
        "N": N
    })

# --------------------------------------------------
# DISPLAY SIMULATION RESULTS
# --------------------------------------------------
if st.session_state["sim_done"]:
    st.caption(
    f"Last run: {weekday_names[weekday]} | {season} | N = {N} EVs | Dataset: {st.session_state['selected_dataset']}"
    )
    

    P_total = st.session_state["P_total"]
    Q_total = st.session_state["Q_total"]
    start_points = np.clip(st.session_state["start_points"], 0, len(P_total)-1)
    end_points = np.clip(st.session_state["end_points"], 0, len(P_total)-1)

    df_load = pd.DataFrame({
        "Minute": np.arange(len(P_total)),
        "Active Power (kW)": P_total,
        "Reactive Power (kVAR)": Q_total
    })

    # --------------------------------------------------
    # ACTIVE POWER PLOT WITH START/END MARKERS
    # --------------------------------------------------
    st.subheader("🔌 Active Power")

    fig_p = px.line(df_load, x="Minute", y="Active Power (kW)",labels={"Minute": "Minute of Day", "Active Power (kW)": "Active Power (W)"})
    fig_p.update_traces(line=dict(width=4, color="royalblue"))

    fig_p.add_scatter(
        x=start_points,
        y=df_load.loc[start_points, "Active Power (kW)"],
        mode="markers",
        name="Start Charging",
        marker=dict(color="green", size=9, symbol="circle")
    )

    fig_p.add_scatter(
        x=end_points,
        y=df_load.loc[end_points, "Active Power (kW)"],
        mode="markers",
        name="End Charging",
        marker=dict(color="red", size=9, symbol="x")
    )
    fig_p.update_layout(title=f"Load on {weekday_names[weekday]} ({season})",
                        hovermode="x unified")

    fig_p.update_layout(
    # title_font_size=26,
    # title_font_color="green",
    xaxis_title_font_size=18,
    xaxis_title_font_color="black",
    yaxis_title_font_size=18,
    yaxis_title_font_color="black",
    xaxis_tickfont_size=14,
    xaxis_tickfont_color="black",
    yaxis_tickfont_size=14,
    yaxis_tickfont_color="black")
    fig_p.update_layout(hovermode="x unified")
    st.plotly_chart(fig_p, use_container_width=True)

    # --------------------------------------------------
    # REACTIVE POWER PLOT WITH START/END MARKERS
    # --------------------------------------------------
    st.subheader("⚡ Reactive Power")

    fig_q = px.line(df_load, x="Minute", y="Reactive Power (kVAR)",labels={"Minute": "Minute of Day", "Reactive Power (kVAR)": "Reactive Power (VAR)"})
    fig_q.update_traces(line=dict(width=4, color="purple"))

    fig_q.add_scatter(
        x=start_points,
        y=df_load.loc[start_points, "Reactive Power (kVAR)"],
        mode="markers",
        name="Start Charging",
        marker=dict(color="green", size=9, symbol="circle")
    )

    fig_q.add_scatter(
        x=end_points,
        y=df_load.loc[end_points, "Reactive Power (kVAR)"],
        mode="markers",
        name="End Charging",
        marker=dict(color="red", size=9, symbol="x")
    )
    fig_q.update_layout(title=f"Reactive Power on {weekday_names[weekday]} ({season})",
                        hovermode="x unified")
    fig_q.update_layout(
    # title_font_size=26,
    # title_font_color="green",
    xaxis_title_font_size=18,
    xaxis_title_font_color="black",
    yaxis_title_font_size=18,
    yaxis_title_font_color="black",
    xaxis_tickfont_size=14,
    xaxis_tickfont_color="black",
    yaxis_tickfont_size=14,
    yaxis_tickfont_color="black")
    fig_q.update_layout(hovermode="x unified")
    st.plotly_chart(fig_q, use_container_width=True)


    # ---------------- DOWNLOAD SECTION ----------------
    st.markdown("---")
    st.header("⬇️ Download Results")

    dataset_label = st.session_state["selected_dataset"].replace(".csv", "")
    weekday_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    tab1, tab2 = st.tabs(["🔌 Load Profile", "🚗 Selected EV Profiles"])

    with tab1:
        st.download_button(
            "Download Load CSV",
            df_load.to_csv(index=False),
            f"EV_Load_Profile_{dataset_label}_{weekday_names[st.session_state['weekday']]}_{st.session_state['season']}_N{st.session_state['N']}.csv",
            "text/csv"
        )

    with tab2:
        df_selected = pd.DataFrame({
            "EV_ID": np.arange(1, len(st.session_state["selected_profiles"]) + 1),
            "Profile_File": st.session_state["selected_profiles"]
        })
        st.download_button("Download Profiles CSV", df_selected.to_csv(index=False),
                           f"Selected_EV_Profiles_{dataset_label}.csv", "text/csv")

    st.success("Simulation completed successfully ✅")
# --------------------------------------------------
# USER GUIDANCE MESSAGES
# --------------------------------------------------
if not st.session_state["pdf_done"]:
    st.info("📊 Generate Behavior PDFs from the sidebar to begin.")

elif st.session_state["pdf_done"] and not st.session_state["sim_done"]:
    st.info("⚡ PDFs ready. Configure simulation parameters and run the Grid Load Simulation.")

# When both done → show nothing


