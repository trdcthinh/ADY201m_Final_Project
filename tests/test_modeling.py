import pytest
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

def test_data_leakage_train_test_independence():
    """Kiểm tra tính độc lập tuyệt đối giữa tập Train và Test (No index overlap)."""
    np.random.seed(42)
    X = pd.DataFrame(np.random.randn(100, 5), columns=[f'feat_{i}' for i in range(5)])
    y = pd.Series(np.random.choice([0, 1], size=100))
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Đảm bảo index trùng lặp = 0
    overlap = set(X_train.index).intersection(set(X_test.index))
    assert len(overlap) == 0

def test_smote_resampling_on_train_only():
    """Kiểm tra SMOTE chỉ nhân bản mẫu trên X_train, không làm thay đổi X_test."""
    np.random.seed(42)
    # Mất cân bằng lớp: 90 mẫu lớp 1, 10 mẫu lớp 0
    X = pd.DataFrame(np.random.randn(100, 4))
    y = pd.Series([1]*90 + [0]*10)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    test_len_before = len(X_test)
    
    smote = SMOTE(random_state=42)
    X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
    
    # Tập train đã cân bằng
    assert y_train_sm.value_counts()[0] == y_train_sm.value_counts()[1]
    # Tập test giữ nguyên kích thước ban đầu
    assert len(X_test) == test_len_before

def test_model_prediction_shape():
    """Kiểm tra ma trận dự đoán xác suất output từ Random Forest."""
    X_train = np.random.randn(50, 4)
    y_train = np.random.choice([0, 1], size=50)
    X_test = np.random.randn(10, 4)
    
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X_train, y_train)
    
    probs = clf.predict_proba(X_test)
    assert probs.shape == (10, 2)
    assert np.all(probs >= 0.0) and np.all(probs <= 1.0)
