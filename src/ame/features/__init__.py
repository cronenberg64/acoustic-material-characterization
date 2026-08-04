import numpy as np
import pandas as pd
from typing import Dict, List
from ame.features.generic import extract as extract_generic
from ame.features.modal import extract as extract_modal

def extract_all(waveform: np.ndarray, sr: int) -> Dict[str, float]:
    """
    Extracts both generic and modal features and merges them with prefixes.
    """
    gen_features = extract_generic(waveform, sr)
    mod_features = extract_modal(waveform, sr)
    
    merged = {}
    for k, v in gen_features.items():
        merged[f"gen_{k}"] = v
        
    for k, v in mod_features.items():
        merged[f"mod_{k}"] = v
        
    return merged

def compare_stability(df: pd.DataFrame, feature_cols: List[str], group_col: str = 'sample_id', vary_col: str = 'force_level') -> pd.DataFrame:
    """
    Computes a discriminability ratio (between-sample variance / within-sample variance)
    for each feature to answer RQ3. Higher means the feature is more stable across contact variations
    while remaining discriminative between samples.
    """
    results = []
    
    for feat in feature_cols:
        # Filter NaNs
        valid_df = df.dropna(subset=[feat])
        if len(valid_df) == 0:
            results.append({"feature": feat, "ratio": np.nan, "between_var": np.nan, "within_var": np.nan})
            continue
            
        # Overall mean
        overall_mean = valid_df[feat].mean()
        
        # Between-sample variance
        # Mean of feature for each sample
        sample_means = valid_df.groupby(group_col)[feat].mean()
        between_var = np.var(sample_means, ddof=1) if len(sample_means) > 1 else 0
        
        # Within-sample variance across the vary_col (e.g. force_level)
        # For each sample, compute variance across conditions, then average
        within_vars = valid_df.groupby(group_col)[feat].var(ddof=1)
        within_var_mean = within_vars.mean()
        
        if within_var_mean is not None and within_var_mean > 0:
            ratio = between_var / within_var_mean
        elif between_var > 0:
            ratio = np.inf
        else:
            ratio = np.nan
        
        results.append({
            "feature": feat,
            "ratio": ratio,
            "between_var": between_var,
            "within_var": within_var_mean
        })
        
    return pd.DataFrame(results).sort_values("ratio", ascending=False)
