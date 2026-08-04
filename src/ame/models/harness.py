import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import KFold, LeaveOneGroupOut
from typing import Iterator, Tuple

def get_models():
    """Return dictionary of models wrapped in a standard scaling pipeline."""
    base_models = {
        "knn": KNeighborsRegressor(),
        "rf": RandomForestRegressor(n_estimators=100, random_state=42),
        "hgb": HistGradientBoostingRegressor(random_state=42),
        "ridge": Ridge(),
        "mlp": MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    }
    
    pipelines = {}
    for name, model in base_models.items():
        pipelines[name] = Pipeline([
            ("scaler", StandardScaler()),
            ("model", model)
        ])
    return pipelines

class LeaveOneSampleOut:
    """Leave one sample (geometry/material instance) out."""
    def split(self, X, y, groups):
        logo = LeaveOneGroupOut()
        return logo.split(X, y, groups)

class LeaveOneContactConditionOut:
    """
    Train on a subset of contact conditions and a subset of samples.
    Test on held-out samples AND held-out contact conditions.
    Ensures that for a test sample, the model has NEVER seen its geometry,
    AND the model has NEVER seen the test contact condition during training.
    """
    def __init__(self, condition_col: str):
        self.condition_col = condition_col
        
    def split(self, X, y, groups, conditions):
        # groups = sample_ids
        # conditions = e.g. force_levels
        
        unique_groups = np.unique(groups)
        unique_conditions = np.unique(conditions)
        
        for test_condition in unique_conditions:
            # We also need to leave out some samples. Let's do K-fold on samples.
            # To keep it simple, let's just do LeaveOneGroupOut on the condition, 
            # and ALSO leave out one sample for testing.
            # So for each sample AND each condition:
            for test_sample in unique_groups:
                train_idx = np.where((groups != test_sample) & (conditions != test_condition))[0]
                test_idx = np.where((groups == test_sample) & (conditions == test_condition))[0]
                
                if len(train_idx) > 0 and len(test_idx) > 0:
                    yield train_idx, test_idx

def evaluate_model(model, X, y, cv, groups=None, conditions=None):
    """Evaluate a single model using a specific CV protocol."""
    from sklearn.metrics import mean_absolute_error, r2_score
    
    y_true_all = []
    y_pred_all = []
    
    if isinstance(cv, KFold):
        splits = cv.split(X)
    elif isinstance(cv, LeaveOneSampleOut):
        splits = cv.split(X, y, groups)
    elif isinstance(cv, LeaveOneContactConditionOut):
        splits = cv.split(X, y, groups, conditions)
    else:
        raise ValueError("Unknown CV")
        
    for train_idx, test_idx in splits:
        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]
        
        # Drop NaNs
        valid_train = ~np.isnan(y_train)
        valid_test = ~np.isnan(y_test)
        
        if np.sum(valid_train) == 0 or np.sum(valid_test) == 0:
            continue
            
        model.fit(X_train[valid_train], y_train[valid_train])
        preds = model.predict(X_test[valid_test])
        
        y_true_all.extend(y_test[valid_test].values)
        y_pred_all.extend(preds)
        
    y_true_all = np.array(y_true_all)
    y_pred_all = np.array(y_pred_all)
    
    if len(y_true_all) == 0:
        return np.nan, np.nan, np.nan
        
    mae = mean_absolute_error(y_true_all, y_pred_all)
    r2 = r2_score(y_true_all, y_pred_all)
    
    # Predict the mean baseline MAE
    mean_pred = np.full_like(y_true_all, np.mean(y_true_all))
    mae_baseline = mean_absolute_error(y_true_all, mean_pred)
    
    return mae, r2, mae_baseline
