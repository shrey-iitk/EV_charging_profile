<h1>⚡ EV-Grid-Intelligence</h1>

<h3>AI-Powered Risk & Hosting Capacity Engine for EV-Integrated Distribution Grids</h3>

> A physics-aware, data-driven simulation platform that predicts how electric vehicle charging will stress real distribution networks — identifying voltage violations, transformer overloads, and grid failure risks before they happen.

<h3>🚀 Why this exists</h3>

Mass EV adoption is fundamentally reshaping power distribution networks.
Traditional planning tools assume static loads and fail to capture:

* Stochastic EV arrival patterns

* Charger and battery physics

* Unbalanced three-phase power flow

* Real-time grid stress under fast charging

This leads to:

* Undetected voltage collapse

* Transformer overheating

* Harmonic violations

* Premature asset failure

**EV-Grid-Intelligence solves this by combining physics, data, and AI into one coherent simulation engine.**

<h3>🧠 What this system does</h3>

Given:

* A real distribution feeder (OpenDSS)

* EV charging demand (stochastic PDFs)

* Physics-based charger and battery models

It computes:

* Bus voltages (3-phase, unbalanced)

* Transformer and line loading

* Losses and harmonics

* Probability of grid violations

* Maximum safe EV hosting capacity

This turns EV planning from **guesswork** into **quantified risk analysis.**

<h3> 🧩 Core Architecture</h3>

*EV Demand (PDFs, SOC, Duration)* <br>
    &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; ↓<br>
*Charger + Battery Physics*<br>
            &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; ↓<br>
*Unbalanced Power Flow (OpenDSS)*<br>
            &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; ↓<br>
*Grid Stress & Risk Analytics*<br>
            &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; &ensp; ↓<br>
*Hosting Capacity + Failure Prediction*



Each EV is modeled as a **dynamic cyber-physical system**, not a static kW load.

<h3> 📊 What you get </h3>

| **Feature** | **Description** |
|------------|-----------------|
| Stochastic EV modeling | Start times, charging durations, and SOCs are sampled from real-world probability distributions |
| Physics-based chargers | Inverter, DC–DC converter, battery, and control loops are explicitly modeled |
| Unbalanced power flow | True three-phase feeder simulation using OpenDSS |
| Hosting capacity | Computes the maximum number of EVs before voltage or thermal violations occur |
| Monte-Carlo risk | Estimates probability of grid failure across thousands of randomized days |
| Harmonics | IEEE-519 compliant harmonic distortion analysis |
| Smart charging | Supports reactive power control and load shifting strategies |


<h3> 🖥️ Live Demo </h3>

The system includes an interactive dashboard:

streamlit run ui/app.py


You can:

* Set number of EVs

* Choose fast vs slow chargers

* Select weekday/weekend

* Enable smart charging

And see:

* Voltage heatmaps

* Transformer overloads

* Weakest buses

* Failure probability




<h3> 🧪 Example Use Cases </h3>
**1. How many EVs can this feeder host?**

>Hosting capacity calculation before voltage or transformer limits are violated.

**2. Where will the grid fail first?**

>Identifies the weakest buses and overloaded assets.

**3. How risky is EV adoption?**

>Monte-Carlo simulation gives probability of violations.

**4. Can smart charging help?**

>Quantifies how much reactive power or load shifting increases capacity.

<h3> 🔬 Scientific Foundation </h3>

This engine is built on:

* Physics-based state-space models of EV chargers and batteries

* Stochastic EV arrival and SOC distributions

* Unbalanced time-series power flow

* Real-time simulation data from Typhoon HIL

* IEEE-519 harmonic standards

This is not a black-box ML model — it is **physics-informed AI.**

<h3> 🧑‍💻 Why this matters </h3>

Utilities, fleet operators, and grid planners need to know:

> “Will EVs break my grid — and where?”

This platform answers that with **engineering precision and probabilistic confidence.**

<h2> 📬 Author </h2>

**Shrey Verma**<br>
PhD Researcher, Power Systems & EV Grid Intelligence
IIT Kanpur

>Specialized in physics-informed AI for cyber-physical energy systems.