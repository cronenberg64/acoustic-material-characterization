import pandas as pd
import numpy as np
import scipy.stats as stats
import os
import glob
from pathlib import Path

def calculate_density(mass, mass_err, length, len_err, width, wid_err, thickness, thick_err):
    """
    Calculate density and propagate uncertainty.
    Inputs in g and mm. Output in kg/m^3.
    """
    # Convert to kg and m
    m = mass / 1000.0
    m_err = mass_err / 1000.0
    l = length / 1000.0
    l_err = len_err / 1000.0
    w = width / 1000.0
    w_err = wid_err / 1000.0
    t = thickness / 1000.0
    t_err = thick_err / 1000.0
    
    volume = l * w * t
    density = m / volume
    
    # Fractional uncertainties (quadrature)
    frac_err_m = m_err / m
    frac_err_l = l_err / l
    frac_err_w = w_err / w
    frac_err_t = t_err / t
    
    frac_err_vol = np.sqrt(frac_err_l**2 + frac_err_w**2 + frac_err_t**2)
    frac_err_density = np.sqrt(frac_err_m**2 + frac_err_vol**2)
    
    density_err = density * frac_err_density
    return density, density_err

def calculate_youngs_modulus(bend_df, width_mm, thickness_mm, span_mm=80.0):
    """
    Calculate Young's Modulus using 3-point bend data.
    E = (F * L^3) / (48 * delta * I)
    """
    force_n = bend_df['Force_N'].values
    deflection_mm = bend_df['Deflection_mm'].values
    deflection_m = deflection_mm / 1000.0
    
    # Linear regression to find stiffness k = F / delta
    res = stats.linregress(deflection_m, force_n)
    k = res.slope
    r_squared = res.rvalue**2
    
    # Geometric properties in m
    b = width_mm / 1000.0
    h = thickness_mm / 1000.0
    L = span_mm / 1000.0
    
    # Area moment of inertia
    I = (b * h**3) / 12.0
    
    # Young's Modulus (Pa)
    E = (k * L**3) / (48 * I)
    
    # Convert to GPa for readability
    E_gpa = E / 1e9
    
    return E, E_gpa, r_squared

def predict_first_bending_mode(E_pa, density_kg_m3, length_mm, width_mm, thickness_mm):
    """
    Predict the first free-free bending mode frequency (Hz).
    Using Euler-Bernoulli beam theory: f1 = (22.373 / (2*pi*L^2)) * sqrt(E*I / (rho*A))
    """
    L = length_mm / 1000.0
    b = width_mm / 1000.0
    h = thickness_mm / 1000.0
    
    I = (b * h**3) / 12.0
    A = b * h
    
    f1 = (22.3733 / (2 * np.pi * L**2)) * np.sqrt((E_pa * I) / (density_kg_m3 * A))
    return f1

def process_ground_truth(data_dir="data/raw_measurements"):
    meta_path = os.path.join(data_dir, "sample_metadata.csv")
    if not os.path.exists(meta_path):
        print(f"Error: {meta_path} not found.")
        return
        
    df_meta = pd.read_csv(meta_path)
    
    results = []
    
    for _, row in df_meta.iterrows():
        sid = row['sample_id']
        
        # Calculate Density
        rho, rho_err = calculate_density(
            row['mass_g'], row['mass_err_g'],
            row['length_mm'], row['length_err_mm'],
            row['width_mm'], row['width_err_mm'],
            row['thickness_mm'], row['thickness_err_mm']
        )
        
        # Find bend data
        bend_path = os.path.join(data_dir, f"bend_{sid}.csv")
        if not os.path.exists(bend_path):
            print(f"Warning: No bend data found for {sid}. Skipping Young's modulus.")
            continue
            
        df_bend = pd.read_csv(bend_path)
        E_pa, E_gpa, r2 = calculate_youngs_modulus(df_bend, row['width_mm'], row['thickness_mm'])
        
        if r2 < 0.98:
            print(f"WARNING: Poor linear fit for {sid} (R^2 = {r2:.4f}). Check for plastic deformation.")
            
        f1_pred = predict_first_bending_mode(E_pa, rho, row['length_mm'], row['width_mm'], row['thickness_mm'])
        
        results.append({
            'sample_id': sid,
            'density_kg_m3': round(rho, 2),
            'density_err_kg_m3': round(rho_err, 2),
            'youngs_modulus_gpa': round(E_gpa, 4),
            'E_r_squared': round(r2, 4),
            'predicted_f1_hz': round(f1_pred, 1)
        })
        
    df_results = pd.DataFrame(results)
    
    out_dir = "data"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ground_truth.csv")
    df_results.to_csv(out_path, index=False)
    print(f"Successfully processed ground truth data and saved to {out_path}")
    print(df_results)

if __name__ == "__main__":
    process_ground_truth()
