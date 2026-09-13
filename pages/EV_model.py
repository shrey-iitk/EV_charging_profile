
import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ev_model.P_Q_SOC_predictor import predict_from_soc_range

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="EV SOC Prediction",
    layout="wide"
)

st.title("EV Charging Profile Prediction")

# --------------------------------------------------
# Sidebar inputs
# --------------------------------------------------
st.sidebar.header("SOC Input")

soc_start = st.sidebar.number_input(
    "Initial SOC (%)",
    min_value=10,
    max_value=100,
    value=45,
    step=1
)

soc_end = st.sidebar.number_input(
    "Final SOC (%)",
    min_value=10,
    max_value=100,
    value=89,
    step=1
)

run_button = st.sidebar.button("Run Prediction")

# --------------------------------------------------
# Run model (ONLY when button is pressed)
# --------------------------------------------------
if run_button:

    if soc_start >= soc_end:
        st.error("Initial SOC must be less than Final SOC")

    else:
        with st.spinner("Running SOC prediction..."):
            time, P, Q, SOC = predict_from_soc_range(soc_start, soc_end)

        # Create DataFrame
        df = pd.DataFrame({
            "time": time,
            "P": P,
            "Q": Q,
            "SOC": SOC,
        })

        # 🔑 STORE RESULT IN SESSION STATE
        st.session_state["prediction_df"] = df
        st.session_state["start_time"] = datetime.now()
        st.session_state["soc_range"] = (soc_start, soc_end)

# --------------------------------------------------
# Plot results (PERSIST across tabs)
# --------------------------------------------------
if "prediction_df" in st.session_state:

    df = st.session_state["prediction_df"]

    st.caption(
        f"Last run: SOC {st.session_state['soc_range'][0]} → {st.session_state['soc_range'][1]}"
    )

    st.subheader("🔌⚡ Active Power & 🔋 SOC")

    fig_combined = go.Figure()

    # -----------------------------
    # Active Power (Left Y-axis)
    # -----------------------------
    fig_combined.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["P"] / 1000,
            name="Active Power (kW)",
            line=dict(color="royalblue", width=4),
            yaxis="y1"
        )
    )

    # -----------------------------
    # SOC (Right Y-axis)
    # -----------------------------
    fig_combined.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["SOC"],
            name="SOC (%)",
            line=dict(color="darkorange", width=4, dash="dot"),
            yaxis="y2"
        )
    )

    # -----------------------------
    # Layout Styling
    # -----------------------------
    fig_combined.update_layout(
        template="simple_white",
        xaxis=dict(
            title="Time (s)",
            title_font=dict(size=18, color="black"),
            tickfont=dict(size=14,color="black")
        ),
        yaxis=dict(
            title="Active Power (kW)",
            title_font=dict(size=18, color="royalblue"),
            tickfont=dict(size=14, color="royalblue")
        ),
        yaxis2=dict(
            title="SOC (%)",
            title_font=dict(size=18, color="darkorange"),
            tickfont=dict(size=14, color="darkorange"),
            overlaying="y",
            side="right"
        ),
        legend=dict(
            x=0.15,
            y=0.99,
            xanchor="right",
            yanchor="top",
            font=dict(size=14),
            bgcolor="rgba(255,255,255,0.6)"
        ),
        hovermode="x unified"
    )

    st.plotly_chart(fig_combined, use_container_width=True)

    st.subheader("⚡ Reactive Power & 🔋 SOC")

    fig_q_soc = go.Figure()

    # -----------------------------
    # Reactive Power (Left Axis)
    # -----------------------------
    fig_q_soc.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["Q"] / 1000,   # convert to kVAR
            name="Reactive Power (kVAR)",
            line=dict(color="purple", width=4),
            yaxis="y1"
        )
    )

    # -----------------------------
    # SOC (Right Axis)
    # -----------------------------
    fig_q_soc.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["SOC"],
            name="SOC (%)",
            line=dict(color="darkorange", width=4, dash="dot"),
            yaxis="y2"
        )
    )

    # -----------------------------
    # Layout Styling
    # -----------------------------
    fig_q_soc.update_layout(
        template="simple_white",
        xaxis=dict(
            title="Time (s)",
            title_font=dict(size=18,color="black"),
            tickfont=dict(size=14,color="black")
        ),
        yaxis=dict(
            title="Reactive Power (kVAR)",
            title_font=dict(size=18, color="purple"),
            tickfont=dict(size=14, color="purple")
        ),
        yaxis2=dict(
            title="SOC (%)",
            title_font=dict(size=18, color="darkorange"),
            tickfont=dict(size=14, color="darkorange"),
            overlaying="y",
            side="right"
        ),
        legend=dict(
            x=0.15,
            y=0.99,
            xanchor="right",
            yanchor="top",
            font=dict(size=14),
            bgcolor="rgba(255,255,255,0.6)"
        ),
        hovermode="x unified"
    )

    st.plotly_chart(fig_q_soc, use_container_width=True)

    st.divider()
    # ---------------------------------------------
    # Charging time summary
    # ---------------------------------------------
    st.subheader("Summary of Charging Time and SOC")
    start_time = st.session_state["start_time"]

    charging_duration = timedelta(seconds=float(df["time"].iloc[-1]))
    end_time = start_time + charging_duration

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "🔋 Initial SOC",
            f"{st.session_state['soc_range'][0]}%"
        )

    with col2:
        st.metric(
            "🔋 Final SOC",
            f"{st.session_state['soc_range'][1]}%"
        )

    with col3:
        st.metric(
            "🕒 Start Time",
            start_time.strftime("%H:%M:%S")
        )

    with col4:
        st.metric(
            "🕒 End Time",
            end_time.strftime("%H:%M:%S")
        )

    with col5:
        st.metric(
            "⏱ Charging Time",
            str(charging_duration).split(".")[0]
        )

    st.divider()
    # --------------------------------------------------
    # Download results
    # --------------------------------------------------
    st.subheader("⬇️ Download Prediction Data")

    csv_data = df.to_csv(index=False)

    st.download_button(
        label="Download CSV file",
        data=csv_data,
        file_name=f"EV_SOC_Prediction_{st.session_state['soc_range'][0]}_{st.session_state['soc_range'][1]}.csv",
        mime="text/csv"
    )

    st.success("Prediction completed successfully ✅")

else:
    st.info("Run prediction to see plots")

    
