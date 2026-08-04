import pandas as pd
import numpy as np
import os
import soundfile as sf
import librosa
import warnings
from sklearn.model_selection import KFold
from ame.synth.generator import generate_dataset
from ame.features import extract_all
from ame.models.harness import get_models, LeaveOneSampleOut, LeaveOneContactConditionOut, evaluate_model

warnings.filterwarnings('ignore')

def main():
    print("generating synthetic data for harness testing...")
    tmp_dir = "results/synthetic_data"
    generate_dataset(output_dir=tmp_dir, n_samples=5, force_levels=3, positions=1, reps=5, seed=42)
    
    metadata = pd.read_csv(os.path.join(tmp_dir, "metadata.csv"))
    
    print("extracting features...")
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
    
    print("running experiments...")
    for target in targets:
        for fset_name, fcols in feature_sets.items():
            X = df[fcols]
            y = df[target]
            
            # Fill NaNs with 0 for simplicity in this harness testing
            X = X.fillna(0)
            
            for proto_name, cv in protocols.items():
                for model_name, model in models.items():
                    print(f"eval: {target} | {fset_name} | {proto_name} | {model_name}")
                    
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
    print("done! results written to results/experiment_results.csv")
    
    print("\nsummary (r2 across protocols):")
    summary = results_df.groupby(["target", "feature_set", "protocol"])["r2"].mean().unstack()
    print(summary)

import argparse
from sklearn.metrics import accuracy_score, f1_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def run_external_evaluation(dataset_dir: str):
    print(f"running pipeline sanity check on external dataset ({dataset_dir})")
    metadata_path = os.path.join(dataset_dir, "metadata.csv")
    if not os.path.exists(metadata_path):
        print("external metadata not found. run import_real_impact.py first.")
        return
        
    metadata = pd.read_csv(metadata_path)
    
    print("extracting features from real acoustic recordings...")
    all_records = []
    for _, row in metadata.iterrows():
        try:
            # Use librosa to load since soundfile can be finicky with ogg/mp3
            wave, sr = librosa.load(row["audio_path"], sr=None)
            # the librosa outputs a 1D array, which works fine
            feats = extract_all(wave, sr)
            merged = {**row.to_dict(), **feats}
            all_records.append(merged)
        except Exception as e:
            print(f"failed to extract {row['audio_path']}: {e}")
            
    df = pd.DataFrame(all_records)
    if len(df) < 2:
        print("not enough data to run classifier.")
        return
        
    # Drop NaNs
    df = df.dropna(subset=["gen_rms_mean"])
    
    # We will classify 'material'
    X = df[[c for c in df.columns if c.startswith("gen_") or c.startswith("mod_")]].fillna(0)
    y = df["material"]
    
    # Simple leave-one-out or random fold classification since it's a sanity check
    cv = KFold(n_splits=min(5, len(df)), shuffle=True, random_state=42)
    clf = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    y_true_all = []
    y_pred_all = []
    
    for train_idx, test_idx in cv.split(X):
        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]
        
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)
        
        y_true_all.extend(y_test.values)
        y_pred_all.extend(preds)
        
    acc = accuracy_score(y_true_all, y_pred_all)
    f1 = f1_score(y_true_all, y_pred_all, average="weighted")
    print("\nexternal dataset evaluation results:")
    print("note: this experiment uses different objects, geometries, and forces than GR1.")
    print("it is strictly a sanity check for feature robustness on real audio.")
    print(f"material classification accuracy: {acc:.2f}")
    print(f"material classification f1-score: {f1:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="synthetic", help="'synthetic' or 'internet'")
    args = parser.parse_args()
    
    if args.dataset == "internet":
        run_external_evaluation("results/external_data")
    else:
        main()
