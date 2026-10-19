import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import pytz
from ev_model.P_Q_SOC_predictor_1 import predict_from_soc_range

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="Energy & Cost (TOU)", layout="wide")
st.title("Charging Energy & Cost with Time-of-Use (TOU) Pricing")


def get_local_time():
    try:
        user_tz = st.context.timezone
        return datetime.now(timezone.utc).astimezone(pytz.timezone(user_tz))
    except Exception:
        return datetime.now().astimezone()


# --------------------------------------------------
# Sidebar: SOC input + predictor
# --------------------------------------------------
st.sidebar.header("SOC Input")

soc_start = st.sidebar.number_input(
    "Initial SOC (%)", min_value=10, max_value=100, value=45, step=1
)
soc_end = st.sidebar.number_input(
    "Final SOC (%)", min_value=10, max_value=100, value=89, step=1
)
run_button = st.sidebar.button("Run Prediction")

if run_button:
    if soc_start >= soc_end:
        st.sidebar.error("Initial SOC must be less than Final SOC")
    else:
        with st.spinner("Running SOC prediction..."):
            time, P_pred, Q_pred, SOC_pred = predict_from_soc_range(soc_start, soc_end)

        st.session_state["prediction_df"] = pd.DataFrame(
            {"time": time, "P": P_pred, "Q": Q_pred, "SOC": SOC_pred}
        )
        st.session_state["start_time"] = get_local_time()
        st.session_state["soc_range"] = (soc_start, soc_end)

if "prediction_df" not in st.session_state:
    st.info("Choose the SOC range in the sidebar and click **Run Prediction**.")
    st.stop()

df = st.session_state["prediction_df"]
soc_range = st.session_state["soc_range"]
default_start = st.session_state["start_time"]

# --------------------------------------------------
# TOU defaults / presets
# --------------------------------------------------
PRESETS = {
    "Typical TOU": [4] * 6 + [8] * 10 + [18] * 5 + [8] * 3,   # off-peak / mid / peak / mid
    "Flat (10)": [10] * 24,
    "Night cheap": [2] * 7 + [10] * 11 + [16] * 4 + [6] * 2,
    "Evening peak": [6] * 16 + [20] * 4 + [6] * 4,
}

for h in range(24):
    st.session_state.setdefault(f"tou_{h}", float(PRESETS["Typical TOU"][h]))


def apply_preset():
    values = PRESETS[st.session_state["preset_choice"]]
    for h in range(24):
        st.session_state[f"tou_{h}"] = float(values[h])


def set_all():
    for h in range(24):
        st.session_state[f"tou_{h}"] = float(st.session_state["all_price"])


# --------------------------------------------------
# Sidebar: start time + currency
# --------------------------------------------------
st.sidebar.divider()
st.sidebar.header("Charging Session")
st.sidebar.caption(f"Last run: SOC {soc_range[0]}% → {soc_range[1]}%")

start_t = st.sidebar.time_input(
    "Charging start time (local)",
    value=default_start.time().replace(microsecond=0),
    step=60,
)
start_dt = default_start.replace(
    hour=start_t.hour, minute=start_t.minute, second=start_t.second, microsecond=0
)

currency = st.sidebar.text_input("Currency / price unit", value="₹")

# --------------------------------------------------
# Placeholder for the plot (filled after the sliders are read)
# --------------------------------------------------
plot_area = st.container()

# --------------------------------------------------
# TOU controls: one slider ("knob") per hour
# --------------------------------------------------
st.subheader("🎚️ TOU Price per Hour")

c1, c2, c3 = st.columns([2, 1, 2])
with c1:
    st.selectbox("Preset", list(PRESETS.keys()), key="preset_choice", on_change=apply_preset)
with c2:
    pass
with c3:
    st.number_input(
        f"Set all hours to ({currency}/kWh)", 0.0, 20.0, 10.0, 0.5, key="all_price"
    )
    st.button("Apply to all hours", on_click=set_all)

for row in range(4):
    cols = st.columns(6)
    for i, col in enumerate(cols):
        h = row * 6 + i
        with col:
            st.slider(
                f"{h:02d}:00 – {(h + 1) % 24:02d}:00",
                min_value=0.0,
                max_value=20.0,
                step=0.5,
                key=f"tou_{h}",
            )

prices = np.array([st.session_state[f"tou_{h}"] for h in range(24)])

# --------------------------------------------------
# Energy calculation (trapezoidal integration, split at hour boundaries)
# --------------------------------------------------
t = df["time"].to_numpy(dtype=float)
P = df["P"].to_numpy(dtype=float)   # Watts

offset0 = start_dt.minute * 60 + start_dt.second   # seconds into the start hour
off = t + offset0

energy_by_slot = {}   # absolute hour index (from start hour) -> kWh
for i in range(len(t) - 1):
    a, b = off[i], off[i + 1]
    if b <= a:
        continue
    pa, pb = P[i], P[i + 1]
    cur = a
    while cur < b - 1e-9:
        k = int(np.floor(cur / 3600))
        nxt = min(b, (k + 1) * 3600)
        p1 = pa + (pb - pa) * (cur - a) / (b - a)
        p2 = pa + (pb - pa) * (nxt - a) / (b - a)
        e_kwh = 0.5 * (p1 + p2) * (nxt - cur) / 3600 / 1000
        energy_by_slot[k] = energy_by_slot.get(k, 0.0) + e_kwh
        cur = nxt

slot_hour0 = start_dt.replace(minute=0, second=0, microsecond=0)
rows = []
for k in sorted(energy_by_slot):
    slot_start = slot_hour0 + timedelta(hours=k)
    hod = slot_start.hour
    kwh = energy_by_slot[k]
    price = prices[hod]
    rows.append(
        {
            "Slot": f"{slot_start:%d %b %H:00} – {(slot_start + timedelta(hours=1)):%H:00}",
            "Hour of day": hod,
            "Energy (kWh)": kwh,
            f"Price ({currency}/kWh)": price,
            f"Cost ({currency})": kwh * price,
        }
    )
breakdown = pd.DataFrame(rows)

total_kwh = breakdown["Energy (kWh)"].sum()
total_cost = breakdown[f"Cost ({currency})"].sum()
duration = timedelta(seconds=float(t[-1] - t[0]))
end_dt = start_dt + duration
avg_price = total_cost / total_kwh if total_kwh > 0 else 0.0

# --------------------------------------------------
# Plot: TOU price (bars) + energy used per hour (line)
# --------------------------------------------------
used_hours = set(breakdown["Hour of day"].tolist())
hour_labels = [f"{h:02d}:00" for h in range(24)]
bar_colors = ["darkorange" if h in used_hours else "lightsteelblue" for h in range(24)]

kwh_by_hod = np.zeros(24)
for _, r in breakdown.iterrows():
    kwh_by_hod[int(r["Hour of day"])] += r["Energy (kWh)"]

fig = go.Figure()
fig.add_trace(
    go.Bar(
        x=hour_labels,
        y=prices,
        name=f"TOU price ({currency}/kWh)",
        marker_color=bar_colors,
        yaxis="y1",
    )
)
fig.add_trace(
    go.Scatter(
        x=hour_labels,
        y=np.where(kwh_by_hod > 0, kwh_by_hod, np.nan),
        name="Energy delivered (kWh)",
        mode="lines+markers",
        line=dict(color="royalblue", width=3),
        yaxis="y2",
    )
)
fig.update_layout(
    template="simple_white",
    xaxis=dict(title="Time slot (hour of day)", title_font=dict(size=18), tickfont=dict(size=12)),
    yaxis=dict(title=f"Price ({currency}/kWh)", range=[0, 20], title_font=dict(size=18)),
    yaxis2=dict(
        title="Energy (kWh)",
        overlaying="y",
        side="right",
        rangemode="tozero",
        title_font=dict(size=18, color="royalblue"),
        tickfont=dict(color="royalblue"),
    ),
    legend=dict(orientation="h", y=1.12),
    hovermode="x unified",
    height=420,
)

fig_ps = go.Figure()
fig_ps.add_trace(
    go.Scatter(x=df["time"], y=df["P"] / 1000, name="Active Power (kW)",
               line=dict(color="royalblue", width=4), yaxis="y1")
)
fig_ps.add_trace(
    go.Scatter(x=df["time"], y=df["SOC"], name="SOC (%)",
               line=dict(color="darkorange", width=4, dash="dot"), yaxis="y2")
)
fig_ps.update_layout(
    template="simple_white",
    xaxis=dict(title="Time (s)", title_font=dict(size=18), tickfont=dict(size=14)),
    yaxis=dict(title="Active Power (kW)", title_font=dict(size=18, color="royalblue"),
               tickfont=dict(color="royalblue")),
    yaxis2=dict(title="SOC (%)", title_font=dict(size=18, color="darkorange"),
                tickfont=dict(color="darkorange"), overlaying="y", side="right"),
    legend=dict(orientation="h", y=1.12),
    hovermode="x unified",
    height=380,
)

with plot_area:
    st.subheader("🔌⚡ Predicted Active Power & 🔋 SOC")
    st.plotly_chart(fig_ps, use_container_width=True)
    st.subheader("💲 TOU Price & Energy per Hour")
    st.caption("Orange bars = hours in which the car is charging. Change prices with the knobs below.")
    st.plotly_chart(fig, use_container_width=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("⚡ Total Energy", f"{total_kwh:.2f} kWh")
    m2.metric("💰 Total Cost", f"{currency}{total_cost:.2f}")
    m3.metric("⏱ Charging Time", str(duration).split(".")[0])
    m4.metric("🕒 Start → End", f"{start_dt:%H:%M} → {end_dt:%H:%M}")
    m5.metric("📊 Avg Price", f"{currency}{avg_price:.2f}/kWh")

# --------------------------------------------------
# Breakdown table + download
# --------------------------------------------------
st.divider()
st.subheader("Hourly Breakdown")

hdr = st.columns([2.2, 1.2, 1.4, 1.4, 1.4])
for col, name in zip(
    hdr,
    ["Slot", "Energy (kWh)", f"Price ({currency}/kWh)", f"Cost ({currency})", "Share of cost"],
):
    col.markdown(f"**{name}**")

for _, r in breakdown.iterrows():
    c = st.columns([2.2, 1.2, 1.4, 1.4, 1.4])
    cost_r = r[f"Cost ({currency})"]
    c[0].write(r["Slot"])
    c[1].write(f"{r['Energy (kWh)']:.3f}")
    c[2].write(f"{r[f'Price ({currency}/kWh)']:.2f}")
    c[3].write(f"{cost_r:.2f}")
    c[4].write(f"{(cost_r / total_cost * 100) if total_cost > 0 else 0:.1f}%")

tot = st.columns([2.2, 1.2, 1.4, 1.4, 1.4])
tot[0].markdown("**Total**")
tot[1].markdown(f"**{total_kwh:.3f}**")
tot[2].markdown(f"**{avg_price:.2f}**")
tot[3].markdown(f"**{total_cost:.2f}**")

st.download_button(
    "Download breakdown CSV",
    data=breakdown.to_csv(index=False),
    file_name=f"EV_Cost_Breakdown_{soc_range[0]}_{soc_range[1]}.csv",
    mime="text/csv",
)