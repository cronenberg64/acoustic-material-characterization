import pandas as pd
import numpy as np
import os
import soundfile as sf
import warnings
from sklearn.model_selection import KFold
from ame.synth.generator import generate_dataset
from ame.features import extract_all
from ame.models.harness import get_models, LeaveOneSampleOut, LeaveOneContactConditionOut, evaluate_model

warnings.filterwarnings('ignore')

def main():
    print("Generating synthetic data for harness testing...")
    tmp_dir = "results/synthetic_data"
    generate_dataset(output_dir=tmp_dir, n_samples=5, force_levels=3, positions=1, reps=5, seed=42)
    
    metadata = pd.read_csv(os.path.join(tmp_dir, "metadata.csv"))
    
    print("Extracting features...")
    all_records = []
    for _, row in metadata.iterrows():
        wave, sr = sf.read(row["waveform_path"])
        feats = extract_all(wave, sr)
        merged = {**row.to_dict(), **feats}
        all_records.append(merged)
        
    df = pd.DataFrame(all_records)
    
    # Define feature sets
    feat_cols = [c for c in df.columns if c.startswith("gen_") or c.startswith("mod_")]
    gen_cols = [c for c in feat_cols if c.startswith("gen_")]
    mod_cols = [c for c in feat_cols if c.startswith("mod_")]
    
    feature_sets = {
        "all": feat_cols,
        "generic": gen_cols,
        "modal": mod_cols
    }
    
    targets = ["youngs_modulus_pa", "density_kgm3"]
    
    protocols = {
        "RandomKFold": KFold(n_splits=5, shuffle=True, random_state=42),
        "LeaveOneSampleOut": LeaveOneSampleOut(),
        "LeaveOneForceOut": LeaveOneContactConditionOut("force_level")
    }
    
    models = get_models()
    
    results = []
    
    print("Running experiments...")
    for target in targets:
        for fset_name, fcols in feature_sets.items():
            X = df[fcols]
            y = df[target]
            
            # Fill NaNs with 0 for simplicity in this harness testing
            X = X.fillna(0)
            
            for proto_name, cv in protocols.items():
                for model_name, model in models.items():
                    print(f"Eval: {target} | {fset_name} | {proto_name} | {model_name}")
                    
                    mae, r2, mae_baseline = evaluate_model(
                        model=model, 
                        X=X, 
                        y=y, 
                        cv=cv, 
                        groups=df["sample_id"].values, 
                        conditions=df["force_level"].values
                    )
                    
                    results.append({
                        "target": target,
                        "feature_set": fset_name,
                        "protocol": proto_name,
                        "model": model_name,
                        "mae": mae,
                        "r2": r2,
                        "mae_baseline": mae_baseline
                    })
                    
    results_df = pd.DataFrame(results)
    os.makedirs("results", exist_ok=True)
    results_df.to_csv("results/experiment_results.csv", index=False)
    print("Done! Results written to results/experiment_results.csv")
    
    print("\nSummary (R2 across protocols):")
    summary = results_df.groupby(["target", "feature_set", "protocol"])["r2"].mean().unstack()
    print(summary)

if __name__ == "__main__":
    main()
