import argparse
import uuid
import os
import datetime
import numpy as np
import pandas as pd
import soundfile as sf
import matplotlib.pyplot as plt
from typing import List, Tuple
from ame.schema import TapRecord

def calculate_modal_frequencies(
    youngs_modulus: float, 
    density: float, 
    geometry_scale: float, 
    num_modes: int = 6
) -> np.ndarray:
    """Calculate physical modal frequencies based on beam theory f_k ~ sqrt(E/rho) / L^2"""
    base_freq = np.sqrt(youngs_modulus / density) / (geometry_scale ** 2)
    # Approximate ratios for a free-free beam
    ratios = np.array([1.0, 2.756, 5.404, 8.933, 13.344, 18.638, 24.819, 31.887])
    ratios = ratios[:num_modes]
    
    # Scale appropriately so base_freq is in a realistic audible/ultrasonic range (e.g. 500Hz)
    # A multiplier makes this realistic
    multiplier = 5e-2
    frequencies = base_freq * ratios * multiplier
    
    # Cap at Nyquist later, but keep as raw physical for now
    return frequencies

def generate_tap_waveform(
    youngs_modulus: float,
    density: float,
    geometry_scale: float,
    force_level: int,
    position_id: int,
    angle_deg: float,
    sr: int = 192000,
    duration: float = 0.2,
    snr_db: float = 40.0,
    add_hum: bool = True
) -> np.ndarray:
    """Generate a synthetic tap waveform."""
    t = np.arange(int(sr * duration)) / sr
    
    # 1. Base frequencies (depend ONLY on material/geometry)
    freqs = calculate_modal_frequencies(youngs_modulus, density, geometry_scale, num_modes=6)
    
    # 2. Excitation envelope & contact time
    # Hertzian contact: t_contact ~ F^(-1/5)
    # Force level 1 to 3 -> F = 5, 10, 15 N roughly
    nominal_force = 5.0 * force_level
    # Use shorter contact time so cutoff freq is high enough to excite modes (e.g. 100 us)
    t_contact = 0.0001 * (nominal_force ** -0.2) 
    cutoff_freq = 1.0 / t_contact
    
    # Mode amplitudes roll off above cutoff_freq
    mode_amplitudes = np.exp(-(freqs / cutoff_freq) ** 2)
    
    # 3. Position effects (spatial nodes)
    # Position ID 1, 2, 3 changes excitation of different modes
    pos_mod = np.ones_like(freqs)
    if position_id == 1:
        pos_mod[1::2] = 0.2 # weakly excite even modes
    elif position_id == 2:
        pos_mod[0::2] = 0.2 # weakly excite odd modes
    elif position_id == 3:
        pos_mod[0] = 0.1    # weakly excite fundamental
        
    mode_amplitudes *= pos_mod
    
    # Angle effects - slightly reduce amplitude
    angle_factor = np.cos(np.radians(angle_deg))
    mode_amplitudes *= angle_factor
    
    # 4. Overall amplitude scales with force
    mode_amplitudes *= nominal_force
    
    # 5. Damping (tau)
    # Base tau depends roughly on material, plus extra for fixture
    base_tau = 0.01 + 1000.0 / youngs_modulus
    # Fixture adds slight damping
    tau = base_tau * np.ones_like(freqs)
    tau *= (1.0 - 0.1 * position_id) # slight variation
    
    # 6. Synthesize
    waveform = np.zeros_like(t)
    pre_trigger_padding_len = int(0.01 * sr)
    
    t_active = t[:-pre_trigger_padding_len]
    active_wave = np.zeros_like(t_active)
    
    for f, A, t_k in zip(freqs, mode_amplitudes, tau):
        if f < sr / 2: # Anti-aliasing
            phase = np.random.uniform(0, 2 * np.pi)
            active_wave += A * np.exp(-t_active / t_k) * np.sin(2 * np.pi * f * t_active + phase)
            
    # Combine padding and active wave
    waveform[pre_trigger_padding_len:] = active_wave
    
    # 7. Add Noise
    signal_power = np.var(waveform)
    if signal_power == 0:
        signal_power = 1e-6
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.random.normal(0, np.sqrt(noise_power), len(waveform))
    waveform += noise
    
    # Mains hum (50 Hz)
    if add_hum:
        hum = np.sqrt(noise_power) * 2 * np.sin(2 * np.pi * 50 * t)
        waveform += hum
        
    # Low frequency drift
    drift = np.sqrt(noise_power) * 5 * np.sin(2 * np.pi * 2 * t)
    waveform += drift
    
    return waveform, freqs

def generate_dataset(
    output_dir: str = "data/raw",
    n_samples: int = 15,
    force_levels: int = 3,
    positions: int = 3,
    reps: int = 20,
    seed: int = 42
):
    """Generate a full synthetic dataset matching experimental design."""
    np.random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    
    materials = ["PLA", "PETG", "TPU"]
    base_properties = {
        "PLA": {"E": 3.5e9, "rho": 1240.0},
        "PETG": {"E": 2.2e9, "rho": 1270.0},
        "TPU": {"E": 0.5e9, "rho": 1100.0}
    }
    
    records = []
    
    for sample_idx in range(n_samples):
        material = materials[sample_idx % len(materials)]
        infill = np.random.choice([15, 30, 50, 70, 100])
        
        # Modify properties by infill
        infill_factor = 0.2 + 0.8 * (infill / 100.0)
        E = base_properties[material]["E"] * infill_factor
        rho = base_properties[material]["rho"] * (0.5 + 0.5 * infill_factor)
        
        sample_id = f"{material}_{infill}_{sample_idx}"
        sample_dir = os.path.join(output_dir, sample_id)
        os.makedirs(sample_dir, exist_ok=True)
        
        for f_lvl in range(1, force_levels + 1):
            for pos in range(1, positions + 1):
                for rep in range(reps):
                    angle = np.random.normal(0, 5) # Slight angle variance
                    measured_force = 5.0 * f_lvl + np.random.normal(0, 0.5)
                    
                    wave, _ = generate_tap_waveform(
                        youngs_modulus=E,
                        density=rho,
                        geometry_scale=0.1,
                        force_level=f_lvl,
                        position_id=pos,
                        angle_deg=angle
                    )
                    
                    # Save audio
                    uid = str(uuid.uuid4())
                    fname = f"{uid}.wav"
                    fpath = os.path.join(sample_dir, fname)
                    sf.write(fpath, wave, 192000)
                    
                    record = TapRecord(
                        sample_id=sample_id,
                        material=material,
                        infill_pct=int(infill),
                        force_level=f_lvl,
                        measured_peak_force_N=measured_force,
                        position_id=pos,
                        angle_deg=angle,
                        tip_id="synth_tip",
                        rep_index=rep,
                        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                        waveform_path=fpath,
                        sample_rate_hz=192000,
                        density_kgm3=rho,
                        density_err_kgm3=10.0,
                        youngs_modulus_pa=E,
                        youngs_err_pa=1e7
                    )
                    records.append(record.model_dump())
                    
    df = pd.DataFrame(records)
    df.to_csv(os.path.join(output_dir, "metadata.csv"), index=False)
    print(f"Generated {len(df)} records in {output_dir}")

def preview():
    wave, freqs = generate_tap_waveform(3.5e9, 1240.0, 0.1, 2, 1, 0.0)
    
    plt.figure(figsize=(10, 6))
    
    plt.subplot(2, 1, 1)
    t = np.arange(len(wave)) / 192000
    plt.plot(t, wave)
    plt.title("Synthetic Tap Waveform")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    
    plt.subplot(2, 1, 2)
    plt.magnitude_spectrum(wave, Fs=192000, scale='dB')
    plt.title("Spectrum")
    plt.xlim(0, 20000) # zoom in on lower frequencies
    
    plt.tight_layout()
    plt.show()
    
    print("Underlying Physical Modal Frequencies:", freqs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="Plot a single synthetic tap")
    parser.add_argument("--generate", action="store_true", help="Generate full synthetic dataset")
    parser.add_argument("--outdir", default="data/raw", help="Output directory")
    args = parser.parse_args()
    
    if args.preview:
        preview()
    elif args.generate:
        generate_dataset(output_dir=args.outdir)
    else:
        parser.print_help()
