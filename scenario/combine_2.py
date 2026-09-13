import numpy as np
import pandas as pd
import random

def generate_EV_profiles(
    df_raw,
    profile_files,
    N,
    weekday,            # 0=Mon ... 6=Sun
    season              # "Winter" / "Summer" / "Monsoon" / "Autumn"
):
    # -------------------------------------------------
    # 1. PREPROCESS RAW DATA
    # -------------------------------------------------
    df = df_raw.copy()

    df['Start'] = pd.to_datetime(df['Start'])
    df['ChargeDuration_time'] = pd.to_timedelta(df['Charge.Duration'], unit='m')
    df['ChargingEnd'] = (df['Start'] + df['ChargeDuration_time']).dt.floor('s')

    df['StartHour'] = df['Start'].dt.hour + df['Start'].dt.minute / 60
    df['Month'] = df['Start'].dt.month
    df['Weekday'] = df['Start'].dt.weekday

    def get_season(m):
        if m in [12, 1, 2]: return "Winter"
        if m in [3, 4, 5]:  return "Summer"
        if m in [6, 7, 8, 9]: return "Monsoon"
        return "Autumn"

    df['Season'] = df['Month'].apply(get_season)

    # -------------------------------------------------
    # 2. WEEKDAY START-TIME PDF
    # -------------------------------------------------
    weekday_start_pdf = {}
    bin_width = 1.0

    for wd in range(7):
        sub = df[df['Weekday'] == wd]

        if sub.empty:
            weekday_start_pdf[wd] = np.zeros(24)
            continue

        counts = np.zeros(24)
        for h in range(24):
            counts[h] = np.sum(
                (sub['StartHour'] >= h) & (sub['StartHour'] < h + 1)
            )

        weekday_start_pdf[wd] = counts / (counts.sum() * bin_width)

    # -------------------------------------------------
    # 3. SEASON START-TIME PDF
    # -------------------------------------------------
    season_names = ["Winter", "Summer", "Monsoon", "Autumn"]
    season_start_pdf = {}

    for s in season_names:
        sub = df[df['Season'] == s]

        if sub.empty:
            season_start_pdf[s] = np.zeros(24)
            continue

        counts = np.zeros(24)
        for h in range(24):
            counts[h] = np.sum(
                (sub['StartHour'] >= h) & (sub['StartHour'] < h + 1)
            )

        season_start_pdf[s] = counts / (counts.sum() * bin_width)
    # print(weekday_start_pdf)
    # print(season_start_pdf)
    # -------------------------------------------------
    # 4. GENERATE + AGGREGATE N EV PROFILES
    # -------------------------------------------------
    P_total = np.zeros(1440)
    Q_total = np.zeros(1440)

    start_points = []
    end_points = []
    selected_profiles = []

    for _ in range(N):

        # ---- Randomly select EV profile file
        chosen_file = random.choice(profile_files)
        df_ev = pd.read_csv(chosen_file)

        time_ev = df_ev["time"].values
        P_ev = df_ev["P"].values
        Q_ev = df_ev["Q"].values

        time_ev_min = time_ev / 60
        T_ev_min = time_ev_min[-1]

        t_min = np.arange(0, T_ev_min, 1)

        P_1min = np.interp(t_min, time_ev_min, P_ev)
        Q_1min = np.interp(t_min, time_ev_min, Q_ev)

        session_length = len(P_1min)

        # ---- Joint season × weekday probability
        curve_season = season_start_pdf[season]
        curve_weekday = weekday_start_pdf[weekday]

        joint_curve = curve_season * curve_weekday
        if joint_curve.sum() == 0:
            joint_curve = curve_weekday

        prob_start = joint_curve / joint_curve.sum()

        start_hour = np.random.choice(np.arange(24), p=prob_start)
        start_min = np.random.uniform(0, 60)
        s_idx = int(start_hour * 60 + start_min)

        # ---- Insert into daily profile (wrap-around)
        e_idx = s_idx + session_length

        if e_idx <= 1440:
            P_total[s_idx:e_idx] += P_1min
            Q_total[s_idx:e_idx] += Q_1min
        else:
            overflow = e_idx - 1440
            P_total[s_idx:] += P_1min[:session_length - overflow]
            Q_total[s_idx:] += Q_1min[:session_length - overflow]
            P_total[:overflow] += P_1min[session_length - overflow:]
            Q_total[:overflow] += Q_1min[session_length - overflow:]
            e_idx = 1440

        start_points.append(s_idx)
        end_points.append(e_idx)
        selected_profiles.append(chosen_file)

    # -------------------------------------------------
    # 5. RETURN EVERYTHING
    # -------------------------------------------------
    return (
        weekday_start_pdf,
        season_start_pdf,
        P_total,
        Q_total,
        start_points,
        end_points,
        selected_profiles
    )
