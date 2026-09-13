# EV Grid Impact Intelligence Engine

An interactive **Streamlit-based digital engineering platform for electric-vehicle charging analysis, EV load-profile generation, battery/SOC modelling, user-behaviour simulation, and distribution-grid impact assessment**.

The application brings together data-driven EV modelling and power-system analysis in a single web interface. It is intended for research, planning, and scenario-based evaluation of how increasing EV adoption and realistic charging behaviour can influence electrical-network operation.

**Live application:** https://ev-charging-dt.streamlit.app/

---

## 1. Project Overview

The EV Grid Impact Intelligence Engine is designed to answer a practical question:

> **How will EV charging behaviour and increasing EV penetration affect the operation of an electrical distribution network?**

The platform addresses this through a connected workflow:

1. Reconstruct and generate realistic EV battery **State of Charge (SOC)** trajectories.
2. Use SOC trajectories as inputs to an **LSTM-based model** to estimate EV active and reactive charging power.
3. Model charging behaviour using historical/user-profile data.
4. Generate stochastic EV charging profiles for different weekdays, seasons, and fleet sizes.
5. Aggregate individual EV profiles into **campus/grid-level EV load profiles**.
6. Evaluate the resulting network impact using electrical-performance indicators and scenario analysis.
7. Export generated load profiles and selected EV-profile information for further studies.

The architecture therefore connects:

**Battery state estimation → EV power prediction → User behaviour → Fleet aggregation → Grid-impact analysis**

---

## 2. Main Capabilities

### 🔋 Physics-guided SOC modelling

The battery-SOC module reconstructs SOC as a function of time using a saved physics-guided neural-network model.

The implementation:

- Loads a previously trained PINN model from a `.pkl` file.
- Reconstructs the original PyTorch network architecture.
- Restores the training normalization parameters.
- Predicts SOC from time.
- Uses the learned SOC trajectory to identify time locations corresponding to specified initial and final SOC values.
- Generates a continuous SOC trajectory between those states.

This provides a physics-guided representation of EV battery behaviour before the power-prediction stage.

### ⚡ LSTM-based EV power prediction

The reconstructed SOC trajectory is passed to a saved TensorFlow/Keras LSTM model.

The LSTM produces the EV charging-power outputs used by the downstream simulation:

- **Active power, P**
- **Reactive power, Q**

The model therefore links battery state progression to electrical charging demand.

### 👤 EV user-habit modelling

The user-behaviour module uses CSV datasets containing charging-related profiles and generates probabilistic charging behaviour.

The current implementation supports:

- Dataset selection.
- Automatic extraction of dataset year ranges.
- Charging-start probability distributions by **weekday**.
- Charging-start probability distributions by **season**.
- Interactive visualization of these probability distributions.
- Selection of SOC profile files.
- Simulation of multiple EVs.
- Charging-event start/end points.
- Aggregation of individual EV profiles into total active and reactive power.

### 📈 EV load-profile simulation

The simulator can generate an aggregate EV charging profile for a selected scenario using:

- Weekday
- Season
- Number of EVs
- Selected SOC profiles
- User-behaviour distributions

The result is an estimated time-varying EV load profile suitable for grid studies.

### 🏫 Distribution-grid impact assessment

The broader platform is intended to evaluate how EV penetration changes network operating conditions.

The impact-analysis workflow considers quantities such as:

- Aggregate campus demand.
- Bus/substation voltage behaviour.
- Voltage-deviation performance.
- Line loading.
- Substation loading/capacity margin.
- EV penetration scenarios.

This allows the effect of progressively increasing EV adoption to be evaluated rather than treating EV charging as a fixed load.

---

# 3. Application Workflow

The complete analytical workflow can be represented as:

```text
Historical / User-profile Data
          │
          ▼
  Charging Behaviour Model
          │
          ▼
  EV Charging Start/End Behaviour
          │
          ▼
     SOC Reconstruction
       (PINN Model)
          │
          ▼
     SOC Trajectory
          │
          ▼
    LSTM Power Prediction
       ┌──────────────┐
       │ Active Power │
       │      P       │
       ├──────────────┤
       │ Reactive Q   │
       └──────────────┘
          │
          ▼
 Individual EV Profiles
          │
          ▼
   Fleet Aggregation
          │
          ▼
    EV Load Profile
          │
          ▼
 Distribution Network
      Evaluation
          │
          ▼
 Grid Impact Indicators
```

---

# 4. Application Pages / Modules

> **Note:** The public Streamlit endpoint could not be programmatically crawled during documentation because Streamlit redirected the page through its application authentication layer. The page descriptions below therefore use the available application source code and the implemented project modules rather than inventing undocumented functionality.

## 4.1 EV Model

The **EV Model** page is the battery-and-power modelling component of the platform.

### Purpose

Generate an EV electrical-load trajectory from an initial and final SOC condition.

### Main processing stages

**Step 1 — SOC reconstruction**

A previously trained PINN model is loaded from:

```text
pinn_soc_model.pkl
```

The model reconstructs SOC as a continuous function of time.

**Step 2 — SOC range selection**

The user specifies:

- Initial SOC
- Final SOC

The model identifies the corresponding time interval and generates the SOC sequence.

**Step 3 — LSTM prediction**

The generated SOC profile is provided to:

```text
LSTM_model_text_7_new.h5
```

The LSTM model predicts:

- Active power
- Reactive power

### Typical output

The page returns arrays representing:

```text
Time
P
Q
SOC
```

These profiles form the basis of subsequent fleet-level charging simulations.

---

## 4.2 EV Charging User Habit / Behaviour Simulation

The **EV Charging User Habit** page models the probabilistic nature of EV charging.

The current implementation uses:

```text
user_profiles/
data/
scenario/combine_2.py
```

### Dataset selection

The user selects a CSV dataset from the `user_profiles` directory.

For each dataset, the application attempts to identify the available year range and displays it in the dataset selector.

### Behaviour probability analysis

The page generates two main behavioural probability views:

#### Charging Start PDF by Weekday

Charging-start probability is displayed for:

- Monday
- Tuesday
- Wednesday
- Thursday
- Friday
- Saturday
- Sunday

This allows the model to distinguish weekday-dependent charging behaviour.

#### Charging Start PDF by Season

Charging-start probability is displayed for:

- Winter
- Summer
- Monsoon
- Autumn

This introduces seasonal variability into the simulation.

### Fleet simulation

The simulation stage allows the user to specify:

- Weekday
- Season
- Number of EVs
- SOC profile files

The simulation then generates:

- Aggregate active power
- Aggregate reactive power
- Charging-start points
- Charging-end points
- Selected EV-profile information

### Visualization

The results include:

- Active-power load profile.
- Reactive-power load profile.
- Charging-start markers.
- Charging-end markers.

### Downloads

The page provides downloadable CSV files for:

**EV Load Profile**

Contains the simulated time-series load, including:

- Minute
- Active Power
- Reactive Power

**Selected EV Profiles**

Contains the EV/profile selection used in the scenario.

---

## 4.3 Grid Impact / Network Analysis

The grid-analysis functionality uses the generated EV demand as an additional and time-varying electrical load.

The main idea is to compare network operating conditions as EV penetration increases.

The analysis can be used to investigate:

- Increase in aggregate demand.
- Changes in voltage profiles.
- Changes in feeder/line loading.
- Substation capacity utilisation.
- Remaining network operating margin.
- Sensitivity of the system to increasing EV adoption.

The resulting scenario studies help identify operating limits and potential network bottlenecks before large-scale EV deployment.

---

# 5. Scenario-Based Analysis

A key feature of the platform is the ability to study multiple EV-penetration levels.

A scenario can be interpreted as:

```text
Baseline Grid
      +
 EV Charging Load
      │
      ▼
  Power Flow
      │
      ▼
Network Performance
```

By repeating this process for different numbers or penetration levels of EVs, the application can reveal:

- Growth in peak demand.
- Timing of charging peaks.
- Voltage sensitivity.
- Thermal/loading constraints.
- Remaining substation capacity.

This makes the platform suitable for planning studies rather than only single-scenario visualization.

---

# 6. Data Flow

The application uses several classes of data and model artefacts.

## User behaviour data

CSV datasets stored under:

```text
user_profiles/
```

These are used to derive charging-behaviour patterns.

## SOC profile data

SOC-profile CSV files stored under:

```text
data/
```

Files beginning with:

```text
prediction_SOC
```

are used by the charging-profile simulation.

## PINN model

```text
pinn_soc_model.pkl
```

Stores the trained PyTorch network parameters together with normalization and physics-related constants required for inference.

## LSTM model

```text
LSTM_model_text_7_new.h5
```

Stores the trained TensorFlow/Keras sequence model used to estimate P and Q from the SOC trajectory.

---

# 7. Technology Stack

| Component | Technology |
|---|---|
| Application framework | Streamlit |
| Data processing | Pandas, NumPy |
| Interactive visualization | Plotly |
| SOC model | PyTorch |
| Power-prediction model | TensorFlow / Keras |
| Numerical root finding | SciPy |
| Model storage | `.pkl`, `.h5` |
| Deployment | Streamlit Community Cloud |
| Programming language | Python |

Streamlit is used for the interactive web application and deployment workflow, while Plotly provides interactive visual analytics.

---

# 8. Project Structure

A typical repository structure is:

```text
ev_charging_profile/
│
├── pages/
│   ├── EV_model.py
│   ├── User_habit_2.py
│   └── <other application pages>
│
├── ev_model/
│   ├── P_Q_SOC_predictor_1.py
│   ├── pinn_soc_model.pkl
│   └── LSTM_model_text_7_new.h5
│
├── scenario/
│   └── combine_2.py
│
├── user_profiles/
│   └── *.csv
│
├── data/
│   └── prediction_SOC*.csv
│
├── requirements.txt
└── README.md
```

The exact repository layout may vary depending on the deployment branch.

---

# 9. Installation

Create a Python environment and install the required packages:

```bash
pip install -r requirements.txt
```

A typical dependency set for the currently implemented modules is:

```text
streamlit
numpy
pandas
plotly
tensorflow
torch
scipy
```

---

# 10. Run the Application Locally

From the project root:

```bash
streamlit run pages/EV_model.py
```

or launch the application's configured Streamlit entry point.

The multipage interface can then be accessed from the Streamlit sidebar.

---

# 11. Using the Application

### Step 1 — Explore EV modelling

Open the EV Model page and provide an initial and final SOC range.

The application reconstructs the SOC trajectory and predicts P and Q.

### Step 2 — Analyse charging behaviour

Open the EV Charging User Habit page.

1. Select a historical/user-profile dataset.
2. Generate the charging behaviour probability distributions.
3. Select weekday and season.
4. Specify the number of EVs.
5. Select the SOC profiles.
6. Run the simulation.

### Step 3 — Examine the resulting EV load

Inspect:

- Active-power profile.
- Reactive-power profile.
- Charging start times.
- Charging end times.

Download the generated CSV data for downstream analysis.

### Step 4 — Evaluate grid impact

Use the generated EV load profile as an additional network demand and compare different EV-penetration scenarios.

---

# 12. Research / Engineering Applications

The platform is particularly useful for:

- EV penetration studies.
- Distribution-network planning.
- Campus-grid studies.
- EV charging demand forecasting.
- User-behaviour modelling.
- Battery SOC trajectory reconstruction.
- EV active/reactive power estimation.
- Scenario-based power-flow analysis.
- Identification of voltage and loading constraints.
- Generation of reproducible simulation datasets.

---

# 13. Key Design Philosophy

The platform combines three levels of modelling:

### Battery level

```text
Time → SOC
```

using a physics-guided neural model.

### EV level

```text
SOC → P, Q
```

using an LSTM sequence model.

### Fleet / grid level

```text
Individual EVs
      ↓
Charging behaviour
      ↓
Aggregated EV demand
      ↓
Distribution-network impact
```

This hierarchy allows individual vehicle behaviour to be propagated into system-level power-system analysis.

---

# 14. Outputs

Depending on the selected workflow, the application can produce:

- SOC trajectories.
- Predicted active-power profiles.
- Predicted reactive-power profiles.
- Weekday charging-start PDFs.
- Seasonal charging-start PDFs.
- Individual EV charging profiles.
- Aggregate EV load profiles.
- Charging event start/end points.
- Scenario-specific network-impact results.
- Downloadable CSV files.

---

# 15. Reproducibility Notes

For reliable deployment:

- Keep trained model files in the expected project directories.
- Keep `user_profiles/` and `data/` available to the application.
- Ensure SOC-profile filenames match the expected `prediction_SOC*.csv` pattern.
- Ensure the TensorFlow/Keras model is compatible with the deployed TensorFlow version.
- Ensure the PyTorch model can be reconstructed using the architecture parameters stored in the `.pkl` file.
- Keep package versions synchronized between local development and Streamlit deployment.

---

# 16. Limitations and Considerations

The platform is fundamentally a simulation and research environment. Results depend on:

- The quality and representativeness of the user-profile datasets.
- The training quality of the PINN and LSTM models.
- The selected SOC profiles.
- The number of EVs represented in each scenario.
- The assumptions used by the charging-behaviour model.
- The accuracy of the underlying distribution-network model.

Therefore, generated EV demand should be interpreted as model-based scenario output rather than a direct measurement of future charging behaviour.

---

# 17. Future Extensions

Potential future enhancements include:

- Real-time EV telemetry integration.
- Online SOC/model updating.
- Charging-price and tariff modelling.
- Smart-charging optimization.
- Vehicle-to-grid (V2G) operation.
- Renewable-energy-aware charging.
- Battery degradation modelling.
- Probabilistic uncertainty bands for EV demand.
- Automated EV-penetration sensitivity analysis.
- Real-time power-flow coupling.
- Network-congestion and transformer-aging indicators.
- Automated scenario comparison and report generation.

---

# 18. Project Objective

The overarching objective of the EV Grid Impact Intelligence Engine is to provide a unified computational environment in which:

**realistic EV behaviour → battery state → charging power → aggregate EV demand → grid impact**

can be studied in a transparent, interactive, and reproducible manner.

This makes the platform useful as both a **research prototype** and a **decision-support tool for EV-grid integration studies**.

---

## Live Demo

**EV Grid Impact Intelligence Engine**

https://ev-charging-dt.streamlit.app/

---

## License

Add the project's actual license here before public distribution.

## Authors / Contributors

Shrey Verma

PhD Researcher, Power Systems & EV Grid Intelligence
IIT Kanpur

