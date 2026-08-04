import numpy as np
import scipy.signal
from typing import Dict

def extract(waveform: np.ndarray, sr: int, num_peaks: int = 6) -> Dict[str, float]:
    """
    Extract physics-motivated modal features (hypothesis family).
    Focuses on resonance frequencies and damping which should be invariant to contact.
    """
    if len(waveform) == 0 or np.all(waveform == 0):
        return _get_nan_dict(num_peaks)

    features = {}
    
    # 1. Broad band decay time constant
    # Extract envelope via Hilbert transform
    analytic_signal = scipy.signal.hilbert(waveform)
    envelope = np.abs(analytic_signal)
    
    # Simple log decrement on the envelope to find decay time
    envelope_db = 20 * np.log10(envelope + 1e-12)
    # Fit line to envelope_db
    t = np.arange(len(waveform)) / sr
    # Avoid the very beginning (impact transient) and noise floor
    start_idx = int(0.01 * sr)
    if start_idx < len(waveform) // 2:
        fit_t = t[start_idx:]
        fit_env = envelope_db[start_idx:]
        # Find where it hits noise floor roughly
        valid = fit_env > (np.max(fit_env) - 30) # top 30 dB
        if np.sum(valid) > 10:
            slope, _ = np.polyfit(fit_t[valid], fit_env[valid], 1)
            # envelope_db ~ slope * t -> tau ~ -8.686 / slope
            if slope < 0:
                features["broadband_decay_tau"] = -8.686 / slope
            else:
                features["broadband_decay_tau"] = np.nan
        else:
            features["broadband_decay_tau"] = np.nan
    else:
        features["broadband_decay_tau"] = np.nan
        
    # 2. Spectral Peaks
    # Use Welch's method for smoother PSD
    f, pxx = scipy.signal.welch(waveform, fs=sr, nperseg=min(len(waveform), int(sr*0.05)))
    
    # Convert to dB
    pxx_db = 10 * np.log10(pxx + 1e-12)
    
    # Find peaks
    peaks, props = scipy.signal.find_peaks(pxx_db, prominence=5, width=1)
    
    # Sort by prominence and take top N
    if len(peaks) > 0:
        prominences = props["prominences"]
        widths = props["widths"] # full width at half max (half power since pxx_db is 10log10)
        
        # Sort by frequency to keep modes in order
        # Wait, if we sort by prominence, we might get random modes.
        # It's better to sort top N by prominence, THEN sort those by frequency.
        top_indices = np.argsort(prominences)[-num_peaks:]
        top_indices = np.sort(top_indices) # keep them ordered by frequency among the top N
        
        selected_peaks = peaks[top_indices]
        selected_proms = prominences[top_indices]
        selected_widths = widths[top_indices]
        
        f1 = None
        for i in range(num_peaks):
            if i < len(selected_peaks):
                idx = selected_peaks[i]
                peak_f = f[idx]
                peak_prom = selected_proms[i]
                # Width in Hz
                df = f[1] - f[0]
                width_hz = selected_widths[i] * df
                
                q_factor = peak_f / width_hz if width_hz > 0 else np.nan
                zeta = 1.0 / (2.0 * q_factor) if not np.isnan(q_factor) and q_factor > 0 else np.nan
                
                features[f"peak_{i+1}_freq"] = peak_f
                features[f"peak_{i+1}_prominence"] = peak_prom
                features[f"peak_{i+1}_q"] = q_factor
                features[f"peak_{i+1}_zeta"] = zeta
                
                if i == 0:
                    f1 = peak_f
                    
                if f1 is not None and f1 > 0:
                    features[f"peak_{i+1}_ratio"] = peak_f / f1
                else:
                    features[f"peak_{i+1}_ratio"] = np.nan
                    
            else:
                features[f"peak_{i+1}_freq"] = np.nan
                features[f"peak_{i+1}_prominence"] = np.nan
                features[f"peak_{i+1}_q"] = np.nan
                features[f"peak_{i+1}_zeta"] = np.nan
                features[f"peak_{i+1}_ratio"] = np.nan
    else:
        # No peaks found
        features.update(_get_nan_dict(num_peaks))

    return features

def _get_nan_dict(num_peaks: int) -> Dict[str, float]:
    d = {"broadband_decay_tau": np.nan}
    for i in range(num_peaks):
        d[f"peak_{i+1}_freq"] = np.nan
        d[f"peak_{i+1}_prominence"] = np.nan
        d[f"peak_{i+1}_q"] = np.nan
        d[f"peak_{i+1}_zeta"] = np.nan
        d[f"peak_{i+1}_ratio"] = np.nan
    return d
