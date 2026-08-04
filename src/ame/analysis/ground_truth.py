import json
import os
import argparse
import numpy as np
import pandas as pd
from scipy.stats import linregress

def calculate_density(mass_kg: float, l_m: float, w_m: float, t_m: float) -> float:
    """Calculates density from mass and bounding box dimensions."""
    volume = l_m * w_m * t_m
    return mass_kg / volume

def calculate_youngs_modulus(forces_N: list, deflections_m: list, L_span_m: float, w_m: float, t_m: float) -> tuple:
    """
    Calculates Young's Modulus using a 3-point bend test.
    E = (k * L^3) / (48 * I) where I = (w * t^3) / 12
    Returns (E_Pa, r_squared)
    """
    if len(forces_N) < 2:
        return np.nan, 0.0
        
    # Find slope k = dF/d_deflection in the elastic region
    slope, intercept, r_value, p_value, std_err = linregress(deflections_m, forces_N)
    
    # Area moment of inertia
    I = (w_m * (t_m ** 3)) / 12.0
    
    # Young's modulus
    E_Pa = (slope * (L_span_m ** 3)) / (48 * I)
    
    return E_Pa, (r_value ** 2)

def predict_first_bending_mode(E_Pa: float, rho_kgm3: float, L_m: float, w_m: float, t_m: float) -> float:
    """
    Predicts the first free-free bending mode frequency using Euler-Bernoulli beam theory.
    """
    A = w_m * t_m
    I = (w_m * (t_m ** 3)) / 12.0
    
    # 22.3733 is roughly 4.73004^2
    f1 = (22.3733 / (2 * np.pi * (L_m ** 2))) * np.sqrt((E_Pa * I) / (rho_kgm3 * A))
    return f1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/raw_measurements.json", help="Path to raw measurements")
    parser.add_argument("--output", type=str, default="data/ground_truth.csv", help="Output ground truth path")
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"error: input file {args.input} not found.")
        print("please create it to process your physical measurements.")
        # Create a dummy template for them
        os.makedirs("data", exist_ok=True)
        template = [
            {
                "sample_id": "PLA_100_infill",
                "mass_kg": 0.019,
                "length_m": 0.100,
                "width_m": 0.020,
                "thickness_m": 0.008,
                "bend_span_m": 0.080,
                "bend_forces_N": [0.0, 5.0, 10.0, 15.0],
                "bend_deflections_m": [0.0, 0.0001, 0.0002, 0.0003]
            }
        ]
        with open(args.input, "w") as f:
            json.dump(template, f, indent=4)
        print(f"i created a template for you at {args.input}. fill it with your real data!")
        return
        
    with open(args.input, "r") as f:
        raw_data = json.load(f)
        
    records = []
    for item in raw_data:
        rho = calculate_density(item["mass_kg"], item["length_m"], item["width_m"], item["thickness_m"])
        
        E, r2 = calculate_youngs_modulus(
            item["bend_forces_N"], 
            item["bend_deflections_m"], 
            item["bend_span_m"], 
            item["width_m"], 
            item["thickness_m"]
        )
        
        if r2 < 0.95:
            print(f"warning: poor bend fit for {item['sample_id']} (r2={r2:.3f}). possible slipping?")
            
        f1_predicted = predict_first_bending_mode(E, rho, item["length_m"], item["width_m"], item["thickness_m"])
        
        records.append({
            "sample_id": item["sample_id"],
            "density_kgm3": rho,
            "youngs_modulus_pa": E,
            "bend_r2": r2,
            "predicted_mode_1_hz": f1_predicted
        })
        
    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"processed {len(records)} physical samples. saved to {args.output}")

if __name__ == "__main__":
    main()
