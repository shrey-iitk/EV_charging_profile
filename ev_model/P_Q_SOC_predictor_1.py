import numpy as np
import pickle
import os

import torch
import torch.nn as nn

import tensorflow as tf
from tensorflow.keras.models import load_model as keras_load_model
from tensorflow.keras.losses import MeanSquaredError

from scipy.optimize import brentq


def predict_from_soc_range(
    SOC_initial,
    SOC_final,
    step=0.01,
    soc_tools_path="pinn_soc_model.pkl",
    model_path="LSTM_model_text_7_new.h5"
):
    # ---- Absolute path to this file ----
    base_dir = os.path.dirname(os.path.abspath(__file__))

    model_path     = os.path.join(base_dir, model_path)
    soc_tools_path = os.path.join(base_dir, soc_tools_path)

    # Folder where pinn_vs_nn_comparison.py saved everything

    def soft_clamp(x, lo=0.0, hi=100.0):
        x = lo + np.log1p(np.exp(-np.abs(x - lo))) + np.maximum(x - lo, 0)
        x = hi - (np.log1p(np.exp(-np.abs(hi - x))) + np.maximum(hi - x, 0))
        return x
    # ============================================================
    # 1. Create the same neural network architecture used in training
    # ============================================================
    def create_model(hidden=32, n_layers=2):
        layers = [nn.Linear(1, hidden),nn.Tanh()]
        for _ in range(n_layers - 1):
            layers += [nn.Linear(hidden, hidden),nn.Tanh()]
        layers += [nn.Linear(hidden, 1)]
        model = nn.Sequential(*layers)
        return model
    # ===========================================================
    # 2. Load saved .pkl model
    # ============================================================
    def load_pinn_model(filename):
        with open(filename, "rb") as f:
            d = pickle.load(f)
        # Rebuild the network with the SAME architecture it was trained with
        model = create_model(hidden=d["hidden"],n_layers=d["n_layers"])
        state = {}
        for key, value in d["state_dict"].items():
            # Trained model wraps the Sequential in self.net -- strip that
            # prefix so the keys line up with the bare nn.Sequential here.
            new_key = key.replace("net.", "", 1)
            state[new_key] = torch.tensor(value,dtype=torch.float32)
        model.load_state_dict(state)
        model.eval()
        # Normalization constants used during training
        t_min = d["t_min"]
        t_max = d["t_max"]
        soc_mean = d["soc_mean"]
        soc_std = d["soc_std"]
        # Physics constants (kept for reference only -- already baked into
        # the trained weights, not needed again for inference)
        Q_N = d["Q_N"]
        V_N = d["V_N"]
        print("Model loaded:", filename)
        print(f"Physics constants used during training: "
            f"Q_n = {Q_N} Ah, V_n = {V_N} V")
        return (model,t_min,t_max,soc_mean,soc_std,Q_N,V_N)
    # ============================================================
    # 3. Predict SOC from time
    # ============================================================
    def predict_soc(t_query,model,t_min,t_max,soc_mean,soc_std):
        t_query = np.atleast_1d(np.asarray(t_query, dtype=np.float64))
        # Normalize time the SAME way it was normalized during training
        # (min-max to [0, 1], not z-score)
        t_scaled = (t_query - t_min) / (t_max - t_min)
        t_tensor = torch.tensor(t_scaled,dtype=torch.float32).view(-1, 1)
        with torch.no_grad():
            soc_pred_scaled = model(t_tensor).numpy().flatten()
        # Un-normalize SOC (network was trained on z-scored SOC)
        soc_pred = (soc_pred_scaled * soc_std + soc_mean)
        # Hard-guarantee the physical bound, even for out-of-range queries
        soc_pred = soft_clamp(soc_pred, 0.0, 100.0)
        return soc_pred
    # ============================================================
    # 4. Find time corresponding to a given SOC
    # ============================================================
    def find_time_from_soc(soc_target,model,t_min,t_max,soc_mean,soc_std):
        def error(t):
            predicted_soc = predict_soc([t],model,t_min,t_max,soc_mean,soc_std)[0]
            return predicted_soc - soc_target
        # Search within the trained time range first
        lo, hi = t_min, t_max
        for _ in range(10):
            f_lo = error(lo)
            f_hi = error(hi)
            if np.sign(f_lo) != np.sign(f_hi):
                return brentq(error,lo,hi, xtol=1e-4)
            # Expand search window if target SOC is outside current bracket
            span = hi - lo
            lo -= span / 2
            hi += span / 2
        raise ValueError( f"Could not find time for SOC={soc_target}%" )
    # ============================================================
    # 5. Generate complete SOC series
    # ============================================================
    def generate_soc_series(soc_initial,soc_final,step,model,t_min,t_max,soc_mean,soc_std):
        t_start = find_time_from_soc(soc_initial,model,t_min,t_max,soc_mean,soc_std)
        t_end = find_time_from_soc(soc_final,model,t_min,t_max,soc_mean, soc_std)
        time_series = np.arange(t_start,t_end,step)
        SOC_series = predict_soc(time_series,model,t_min,t_max,soc_mean,soc_std)
        return time_series, SOC_series


    @st.cache_resource
    def load_pinn_model_cached(model_path):
        return load_pinn_model(model_path)
        
    pinn_model, t_min, t_max, soc_mean, soc_std, Q_N, V_N = \
    load_pinn_model_cached(soc_tools_path)
    # (model,t_min,t_max,soc_mean,soc_std,Q_N,V_N) = load_pinn_model(
    #     os.path.join(soc_tools_path))
    # --------------------------------------------------------
    # Generate SOC series
    # --------------------------------------------------------
    time_series, SOC_series = generate_soc_series(SOC_initial,SOC_final, step=0.01,model=model,t_min=t_min,t_max=t_max,soc_mean=soc_mean,soc_std=soc_std)

    #Generate new time value from 0 till last value as time_series values are cooresponding to that value
    def arithmetic_sequence(a1, d, n):
        return [a1 + (i * d) for i in range(n)]

     # Example usage
    a1 = 0
    d = 0.01
    n = len(SOC_series)
    time = arithmetic_sequence(a1, d, n)
    
    tf.keras.backend.clear_session()
    # model = tf.keras.models.load_model(
    #     model_path,
    #     custom_objects={'mse': tf.keras.losses.MeanSquaredError()}
    #     )
    @st.cache_resource
    def load_lstm_model(model_path):
        return keras_load_model(
        model_path,
        custom_objects={"mse": MeanSquaredError()},
        compile=False
        )
    lstm_model = load_lstm_model(model_path)
    # model = keras_load_model(
    #     model_path,
    #     custom_objects={'mse': MeanSquaredError()},
    #     compile=False
    # )
    # model = load_model("model.h5", compile=False)

    # Extract 'SOC' column and reshape it to match the structure
    X = SOC_series.reshape(-1, 1, 1)  # Reshape to (samples, timesteps, features)
    X= X/100

    # Predict the outputs
    predicted_outputs = np.array(model.predict(X))  # Ensure predictions are a NumPy array

    # Reshape predictions to remove redundant dimensions
    predicted_outputs = predicted_outputs.squeeze()  # Remove all axes of size 1


    # Extract 'P' and 'Q' predictions
    predicted_y1 = predicted_outputs[0, :]  # Assuming the first index corresponds to 'P'
    predicted_y2 = predicted_outputs[1, :]  # Assuming the second index corresponds to 'Q'
    
    

    return time, predicted_y1, predicted_y2, SOC_series
