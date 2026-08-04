import pandas as pd
from ame.synth.generator import generate_dataset
from ame.features import extract_all, compare_stability
import os
import soundfile as sf
import uuid

def test_feature_stability(tmp_path):
    """
    Test that modal features have higher discriminability ratio than generic features
    on synthetic data.
    """
    # Generate small dataset to tmp_path
    generate_dataset(output_dir=str(tmp_path), n_samples=3, force_levels=2, positions=1, reps=2, seed=42)
    
    metadata = pd.read_csv(os.path.join(tmp_path, "metadata.csv"))
    
    # Extract features for each record
    all_features = []
    for _, row in metadata.iterrows():
        wave, sr = sf.read(row["waveform_path"])
        feats = extract_all(wave, sr)
        
        # Merge dicts
        merged = {**row.to_dict(), **feats}
        all_features.append(merged)
        
    df = pd.DataFrame(all_features)
    
    # Get feature columns
    feat_cols = [c for c in df.columns if c.startswith("gen_") or c.startswith("mod_")]
    
    # Compare stability
    stability_df = compare_stability(df, feature_cols=feat_cols, group_col="sample_id", vary_col="force_level")
    
    # Assert that top feature by ratio is a modal feature
    top_feature = stability_df.iloc[0]["feature"]
    assert top_feature.startswith("mod_")
    
    # Also assert that gen_rms_mean ratio is lower than mod_peak_1_freq ratio
    mod_f1 = stability_df[stability_df["feature"] == "mod_peak_1_freq"]["ratio"].values
    gen_rms = stability_df[stability_df["feature"] == "gen_rms_mean"]["ratio"].values
    
    if len(mod_f1) > 0 and len(gen_rms) > 0:
        assert mod_f1[0] > gen_rms[0]
