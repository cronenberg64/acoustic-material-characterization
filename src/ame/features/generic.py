import numpy as np
import librosa
from typing import Dict

def extract(waveform: np.ndarray, sr: int) -> Dict[str, float]:
    """
    Extract generic audio features (baseline family).
    Mirrors current robotics practice for acoustic perception.
    """
    if len(waveform) == 0 or np.all(waveform == 0):
        # Handle silence gracefully
        return {k: np.nan for k in _get_keys()}

    features = {}
    
    # 1. RMS Energy
    rms = librosa.feature.rms(y=waveform)[0]
    features["rms_mean"] = rms.mean()
    
    # 2. Zero-crossing rate
    zcr = librosa.feature.zero_crossing_rate(y=waveform)[0]
    features["zcr_mean"] = zcr.mean()
    
    # 3. Spectral features
    centroid = librosa.feature.spectral_centroid(y=waveform, sr=sr)[0]
    features["spectral_centroid"] = centroid.mean()
    
    bandwidth = librosa.feature.spectral_bandwidth(y=waveform, sr=sr)[0]
    features["spectral_bandwidth"] = bandwidth.mean()
    
    rolloff = librosa.feature.spectral_rolloff(y=waveform, sr=sr)[0]
    features["spectral_rolloff"] = rolloff.mean()
    
    flatness = librosa.feature.spectral_flatness(y=waveform)[0]
    features["spectral_flatness"] = flatness.mean()
    
    # Spectral contrast (might fail if signal is too short)
    try:
        contrast = librosa.feature.spectral_contrast(y=waveform, sr=sr)
        features["spectral_contrast_mean"] = contrast.mean()
    except Exception:
        features["spectral_contrast_mean"] = np.nan
        
    # 4. MFCCs (13 coefficients)
    try:
        mfccs = librosa.feature.mfcc(y=waveform, sr=sr, n_mfcc=13)
        for i in range(13):
            features[f"mfcc_{i+1}_mean"] = mfccs[i].mean()
            features[f"mfcc_{i+1}_std"] = mfccs[i].std()
    except Exception:
        for i in range(13):
            features[f"mfcc_{i+1}_mean"] = np.nan
            features[f"mfcc_{i+1}_std"] = np.nan
            
    # 5. Onset/decay time estimate (simple thresholding)
    envelope = np.abs(librosa.core.piptrack(y=waveform, sr=sr)[0])
    # Just a rough estimate for envelope decay
    try:
        onset_env = librosa.onset.onset_strength(y=waveform, sr=sr)
        features["onset_strength_max"] = onset_env.max()
    except Exception:
        features["onset_strength_max"] = np.nan

    return features

def _get_keys() -> list[str]:
    keys = ["rms_mean", "zcr_mean", "spectral_centroid", "spectral_bandwidth", 
            "spectral_rolloff", "spectral_flatness", "spectral_contrast_mean",
            "onset_strength_max"]
    for i in range(13):
        keys.append(f"mfcc_{i+1}_mean")
        keys.append(f"mfcc_{i+1}_std")
    return keys
