import numpy as np
import pandas as pd
from ame.models.harness import LeaveOneSampleOut, LeaveOneContactConditionOut

def test_leave_one_sample_out():
    X = pd.DataFrame(np.random.randn(10, 5))
    y = pd.Series(np.random.randn(10))
    groups = np.array(["A", "A", "B", "B", "C", "C", "D", "D", "E", "E"])
    
    cv = LeaveOneSampleOut()
    splits = list(cv.split(X, y, groups))
    
    assert len(splits) == 5
    for train_idx, test_idx in splits:
        train_groups = groups[train_idx]
        test_groups = groups[test_idx]
        # Ensure no overlap
        assert len(set(train_groups).intersection(set(test_groups))) == 0

def test_leave_one_contact_condition_out():
    X = pd.DataFrame(np.random.randn(12, 5))
    y = pd.Series(np.random.randn(12))
    groups = np.array(["A", "A", "B", "B", "C", "C", "A", "A", "B", "B", "C", "C"])
    conditions = np.array([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2])
    
    cv = LeaveOneContactConditionOut("force_level")
    splits = list(cv.split(X, y, groups, conditions))
    
    # 2 conditions * 3 groups = 6 splits
    assert len(splits) == 6
    
    for train_idx, test_idx in splits:
        train_groups = groups[train_idx]
        test_groups = groups[test_idx]
        train_conds = conditions[train_idx]
        test_conds = conditions[test_idx]
        
        # 1. No overlapping samples between train and test
        assert len(set(train_groups).intersection(set(test_groups))) == 0
        
        # 2. No overlapping conditions between train and test
        assert len(set(train_conds).intersection(set(test_conds))) == 0
