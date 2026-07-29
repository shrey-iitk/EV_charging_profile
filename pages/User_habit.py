import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import os
from scenario.combine_2 import generate_EV_profiles

def get_year_range(csv_path):
    try:
        df_tmp = pd.read_csv(csv_path, parse_dates=[0])  # first column is datetime
        years = df_tmp.iloc[:, 0].dt.year
        return int(years.min()), int(years.max())
    except Exception:
        return None, None


# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="EV Charging User Habit", layout="wide")
st.title("EV Charging User Habit")

# --------------------------------------------------
# Sidebar inputs
# --------------------------------------------------
st.sidebar.header("Context Inputs")

weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

weekday_str = st.sidebar.selectbox("Weekday", weekday_names, index=0)
weekday = weekday_names.index(weekday_str)

season = st.sidebar.selectbox(
    "Season",
    ["Winter", "Summer", "Monsoon", "Autumn"],
    index=1
)

N = st.sidebar.number_input(
    "N (Number of EVs / simulations)",
    min_value=1,
    max_value=1000,
    value=10,
    step=1
)

data_folder = "user_profiles"

available_datasets = [
    f for f in os.listdir(data_folder)
    if f.endswith(".csv")
]

dataset_info = {}

for file in available_datasets:
    path = os.path.join(data_folder, file)
    y_start, y_end = get_year_range(path)

    if y_start:
        dataset_info[file] = f"{file} ({y_start}–{y_end})"
    else:
        dataset_info[file] = f"{file} (Year Unknown)"

# --------------------------------------------------
# SOC Profile Selection
# --------------------------------------------------
# st.sidebar.header("SOC Profile Files")

profile_folder = "data"   # adjust if needed

available_profiles = sorted([
    f for f in os.listdir(profile_folder)
    if f.startswith("prediction_SOC") and f.endswith(".csv")
])

selected_profiles = st.sidebar.multiselect(
    "Select SOC profile to use",
    options=available_profiles,
    default=available_profiles[:3]   # pick first few by default
)


selected_label = st.sidebar.selectbox(
    "Select User Profile Dataset",
    options=list(dataset_info.values())
)

# Reverse lookup to get filename
selected_dataset = [k for k, v in dataset_info.items() if v == selected_label][0]


run_button = st.sidebar.button("Run Prediction")

# --------------------------------------------------
# RUN MODEL AND STORE RESULTS
# --------------------------------------------------
if run_button:
    with st.spinner("Generating EV charging profiles..."):

        df_path = os.path.join(data_folder, selected_dataset)
        df_raw = pd.read_csv(df_path)

        profile_files = [
        os.path.join(profile_folder, f)
        for f in selected_profiles
        ]

        if len(profile_files) == 0:
            st.error("Please select at least one SOC profile file.")
            st.stop()



        results = generate_EV_profiles(
            df_raw=df_raw,
            profile_files=profile_files,
            N=N,
            weekday=weekday,
            season=season
        )

        st.sidebar.info(f"Selected dataset rows: {len(df_raw)}")

        (weekday_start_pdf, season_start_pdf,
         P_total, Q_total,
         start_points, end_points,
         selected_profiles) = results
        

        # Store in session
        st.session_state.update({
            "run_done": True,
            "weekday_start_pdf": weekday_start_pdf,
            "season_start_pdf": season_start_pdf,
            "P_total": P_total,
            "Q_total": Q_total,
            "start_points": start_points,
            "end_points": end_points,
            "weekday": weekday,
            "season": season,
            "selected_profiles":selected_profiles,
            "N": N,
            "selected_dataset": selected_dataset
        })

# --------------------------------------------------
# DISPLAY RESULTS IF AVAILABLE
# --------------------------------------------------
if "run_done" in st.session_state and st.session_state["run_done"]:

    weekday = st.session_state["weekday"]
    season = st.session_state["season"]
    N = st.session_state["N"]
    P_total = st.session_state["P_total"]
    Q_total = st.session_state["Q_total"]
    start_points = st.session_state["start_points"]
    end_points = st.session_state["end_points"]
    weekday_start_pdf = st.session_state["weekday_start_pdf"]
    season_start_pdf = st.session_state["season_start_pdf"]
    selected_profiles = st.session_state["selected_profiles"]
    selected_dataset = st.session_state["selected_dataset"]

    st.caption(
    f"Last run: {weekday_names[weekday]} | {season} | N = {N} EVs | Dataset: {st.session_state['selected_dataset']}"
    )


    # --------------------------------------------------
    # DATAFRAME FOR LOAD
    # --------------------------------------------------
    df_load = pd.DataFrame({
        "Minute": np.arange(len(P_total)),
        "P_total_W": P_total,
        "Q_total_VAR": Q_total
    })

    # --------------------------------------------------
    # ACTIVE POWER PLOT
    # --------------------------------------------------
    st.subheader("🔌 Aggregated Active Power")

    fig_p = px.line(df_load, x="Minute", y="P_total_W",
                    labels={"Minute": "Minute of Day", "P_total_W": "Power (W)"})
    fig_p.update_traces(line=dict(width=4))

    safe_start = np.clip(start_points, 0, len(df_load) - 1)
    safe_end   = np.clip(end_points,   0, len(df_load) - 1)


    fig_p.add_scatter(x=start_points,
                      y=[df_load.loc[int(s), "P_total_W"] for s in safe_start],
                      mode="markers", marker=dict(size=9, color="green"),
                      name="Start Time")

    fig_p.add_scatter(x=end_points,
                      y=[df_load.loc[int(e), "P_total_W"] for e in safe_end],
                      mode="markers", marker=dict(size=9, color="red"),
                      name="End Time")

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

    st.plotly_chart(fig_p, use_container_width=True)

    # --------------------------------------------------
    # REACTIVE POWER PLOT
    # --------------------------------------------------
    st.subheader("⚡ Aggregated Reactive Power")

    fig_q = px.line(df_load, x="Minute", y="Q_total_VAR",
                    labels={"Minute": "Minute of Day", "Q_total_VAR": "Reactive Power (VAR)"})
    fig_q.update_traces(line=dict(width=4))

    fig_q.add_scatter(x=start_points,
                      y=[df_load.loc[int(s), "Q_total_VAR"] for s in safe_start],
                      mode="markers", marker=dict(size=9, color="green"),
                      name="Start Time")

    fig_q.add_scatter(x=end_points,
                      y=[df_load.loc[int(e), "Q_total_VAR"] for e in safe_end],
                      mode="markers", marker=dict(size=9, color="red"),
                      name="End Time")

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

    st.plotly_chart(fig_q, use_container_width=True)

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

    ##Tab Section
    dataset_label = st.session_state["selected_dataset"].replace(".csv", "")
    st.markdown("---")
    st.header("⬇️ Download Data")

    tab1, tab2, tab3, tab4= st.tabs(["🔌 Load Profile", "📅 Weekday PDF", "🌦️ Season PDF", "🚗 Selected EV Profiles"])

    # ---------------- TAB 1 ----------------
    with tab1:
        # st.subheader("Aggregated Load Profile Data")

        df_download_load = pd.DataFrame({
            "Minute": np.arange(len(P_total)),
            "Active_Power_W": P_total,
            "Reactive_Power_VAR": Q_total
        })

        csv_load = df_download_load.to_csv(index=False)

        st.download_button(
            label="Download Load Profile CSV",
            data=csv_load,
            file_name=f"EV_Load_Profile_{dataset_label}_{weekday_names[weekday]}_{season}_N{N}.csv",
            mime="text/csv"
        )

    # ---------------- TAB 2 ----------------
    with tab2:
        # st.subheader("Weekday Charging Start Probability")

        hours = np.arange(24)
        df_weekday_pdf_download = pd.DataFrame([
            {"Weekday": weekday_names[wd], "Hour": hr, "Probability": weekday_start_pdf[wd][hr]}
            for wd in range(7) for hr in hours
        ])


        csv_weekday = df_weekday_pdf_download.to_csv(index=False)

        st.download_button(
            label="Download Weekday PDF CSV",
            data=csv_weekday,
            file_name=f"Weekday_Charging_Start_PDF_{dataset_label}.csv",
            mime="text/csv"
        )

    # ---------------- TAB 3 ----------------
    with tab3:
        # st.subheader("Seasonal Charging Start Probability")

        df_season_pdf_download = pd.DataFrame([
            {"Season": s, "Hour": hr, "Probability": season_start_pdf[s][hr]}
            for s in season_start_pdf.keys() for hr in hours
        ])


        csv_season = df_season_pdf_download.to_csv(index=False)

        st.download_button(
            label="Download Season PDF CSV",
            data=csv_season,
            file_name=f"Season_Charging_Start_PDF_{dataset_label}.csv",
            mime="text/csv"
        )

    with tab4:
        # st.subheader("Selected Charging Profiles per EV")

        selected_profiles = st.session_state["selected_profiles"]

        df_selected = pd.DataFrame({
            "EV_ID": np.arange(1, len(selected_profiles) + 1),
            "Profile_File": selected_profiles
        })

        csv_profiles = df_selected.to_csv(index=False)

        st.download_button(
            label="Download Selected Profiles CSV",
            data=csv_profiles,
            file_name=f"Selected_EV_Profiles_{dataset_label}.csv",
            mime="text/csv"
        )


    st.success("Prediction completed successfully ✅")

else:
    st.info("Run prediction to see plots")