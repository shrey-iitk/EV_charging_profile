# EV Grid Impact Intelligence Engine

An interactive **Streamlit-based platform for EV charging, battery SOC modelling, user-behaviour simulation, and distribution-grid impact analysis**.

**Live App:** https://ev-charging-dt.streamlit.app/

## Overview

The platform connects EV-level modelling with fleet and grid-level analysis:

```text
User Behaviour Data
        ↓
Charging Behaviour
        ↓
SOC Reconstruction (PINN)
        ↓
EV Power Prediction (LSTM)
        ↓
EV Fleet Aggregation
        ↓
EV Load Profile
        ↓
Distribution-Grid Impact
```

It is designed for EV penetration studies, charging-demand analysis, and scenario-based assessment of network loading and voltage performance.

## Main Features

### 🔋 EV Battery / SOC Model
- Physics-guided neural network (PINN) for SOC reconstruction.
- Generates SOC trajectories between selected initial and final SOC values.
- Uses the saved PyTorch model `pinn_soc_model.pkl`.

### ⚡ P–Q Prediction
- Uses the reconstructed SOC trajectory as input to an LSTM model.
- Predicts:
  - Active power (**P**)
  - Reactive power (**Q**)
- Uses the saved Keras model `LSTM_model_text_7_new.h5`.

### 👤 EV User Behaviour
The **EV Charging User Habit** module:
- Selects historical/user-profile datasets.
- Determines dataset year ranges.
- Generates charging-start probability distributions by:
  - Weekday
  - Season
- Supports fleet simulation for a user-selected number of EVs.

### 📊 EV Load Simulation
For a selected weekday, season, EV count, and SOC profiles, the application generates:
- Aggregate active-power profile.
- Aggregate reactive-power profile.
- Charging start/end points.
- Selected EV-profile information.

Results can be downloaded as CSV files.

### 🏫 Grid Impact Analysis
Generated EV demand can be incorporated into distribution-network studies to examine:
- Aggregate demand growth.
- Voltage behaviour.
- Line loading.
- Substation loading/capacity margin.
- Effects of increasing EV penetration.

## Application Workflow

1. Select EV/user-behaviour data.
2. Generate charging-behaviour probability distributions.
3. Generate or select SOC trajectories.
4. Predict EV active and reactive power.
5. Aggregate individual EV charging profiles.
6. Evaluate the resulting EV load.
7. Assess distribution-grid impact under different scenarios.

## Technology Stack

| Component | Technology |
|---|---|
| Web application | Streamlit |
| Data processing | Python, NumPy, Pandas |
| Visualization | Plotly |
| SOC reconstruction | PyTorch |
| P/Q prediction | TensorFlow / Keras |
| Numerical methods | SciPy |
| Deployment | Streamlit Community Cloud |

## Project Structure

```text
ev_charging_profile/
├── pages/
│   ├── EV_model.py
│   ├── User_habit_2.py
│   └── <other pages>
├── ev_model/
│   ├── P_Q_SOC_predictor_1.py
│   ├── pinn_soc_model.pkl
│   └── LSTM_model_text_7_new.h5
├── scenario/
│   └── combine_2.py
├── user_profiles/
│   └── *.csv
├── data/
│   └── prediction_SOC*.csv
├── requirements.txt
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

Typical dependencies:

```text
streamlit
numpy
pandas
plotly
tensorflow
torch
scipy
```

## Run Locally

```bash
streamlit run pages/EV_model.py
```

## Outputs

The platform can produce:
- SOC trajectories.
- EV P and Q profiles.
- Weekday and seasonal charging-start probability plots.
- Individual and aggregated EV charging profiles.
- EV load-profile CSV files.
- Selected-profile CSV files.
- Grid-impact scenario results.

## Applications

- EV penetration studies.
- Distribution-network planning.
- Campus-grid analysis.
- EV charging-demand modelling.
- User-behaviour analysis.
- Battery SOC reconstruction.
- EV active/reactive power prediction.
- Scenario-based grid-impact assessment.

## Project Objective

The primary objective is to provide a unified environment in which:

**EV behaviour → SOC → charging power → aggregate EV demand → grid impact**

can be analysed interactively and consistently.

## Live Demo

**EV Grid Impact Intelligence Engine**  
https://ev-charging-dt.streamlit.app/

## Authors

Shrey Verma

PhD Researcher, Power Systems & EV Grid Intelligence
IIT Kanpur
>Specialized in physics-informed AI for cyber-physical energy systems.

## License

Add the project's applicable license here.
