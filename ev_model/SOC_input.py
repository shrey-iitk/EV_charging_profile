from P_Q_SOC_predictor import predict_from_soc_range
import numpy as np
import os
import pandas as pd

def run_batch_soc_predictions(soc_ranges, output_dir):
    """
    Runs EV charging predictions for multiple SOC ranges and saves results to CSV.

    Parameters
    ----------
    soc_ranges : list of tuples
        [(soc_start, soc_end), ...]
        Example: [(25,61), (10,99)]

    output_dir : str
        Directory where CSV files will be saved.

    Returns
    -------
    batch_results : dict
        Dictionary containing time, P, Q, SOC arrays for each SOC range
    """
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    batch_results = {}

    for soc_i, soc_f in soc_ranges:
        print(f"\nRunning prediction for SOC range {soc_i} → {soc_f} ...")

        # Call your existing model
        time, P, Q, SOC = predict_from_soc_range(soc_i, soc_f)

        key = f"{soc_i}_{soc_f}"

        batch_results[key] = {
            "time": time,
            "P": P,
            "Q": Q,
            "SOC": SOC,
        }

        # Create DataFrame
        df = pd.DataFrame({
            "time": time,
            "P": P,
            "Q": Q,
            "SOC": SOC,
        })

        # Save to CSV
        filename = f"prediction_SOC_{soc_i}_to_{soc_f}.csv"
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)

        print(f"Saved CSV: {filepath}")

    return batch_results


soc_ranges = [
    (25, 61),
    (10,35),
]
output_dir = r"/Users/shreyverma/EV Grid Impact Intelligence Engine/data"
batch_results = run_batch_soc_predictions(soc_ranges, output_dir)