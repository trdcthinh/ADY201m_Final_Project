import sys
import os
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, roc_auc_score
from imblearn.over_sampling import SMOTE

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    from catboost import CatBoostClassifier
    HAS_CAT = True
except ImportError:
    HAS_CAT = False

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_prs.csv")

def evaluate_models():
    print("=" * 70)
    print("🤖 HUẤN LUYỆN VÀ ĐÁNH GIÁ CÁC MÔ HÌNH MACHINE LEARNING (FPT VS GLOBAL)")
    print("=" * 70)

    if not os.path.exists(INPUT_PATH):
        print(f"❌ Không tìm thấy dữ liệu tại: {INPUT_PATH}")
        return

    df = pd.read_csv(INPUT_PATH)
    
    # Preprocessing: drop non-feature identification columns
    drop_cols = [
        'pr_id', 'repo_name', 'pr_number', 'title', 'body_len', 'user_login', 'user_type',
        'created_datetime', 'closed_datetime', 'merged_datetime', 'duration_minutes', 'duration_hours'
    ]
    df_processed = df.drop(columns=[c for c in drop_cols if c in df.columns])
    
    # One-hot encoding
    categorical_cols = ['repo_language', 'keyword']
    df_processed = pd.get_dummies(df_processed, columns=[c for c in categorical_cols if c in df_processed.columns], drop_first=True)

    # Separate FPT and Global datasets
    df_fpt = df_processed[df_processed['is_fpt'] == 1].drop(columns=['is_fpt'])
    df_global = df_processed[df_processed['is_fpt'] == 0].drop(columns=['is_fpt'])

    for name, dataset in [("FPT University Dataset", df_fpt), ("Global Open Source Dataset", df_global)]:
        print(f"\n{"="*30} {name} {"="*30}")
        X = dataset.drop(columns=['is_merged'])
        y = dataset['is_merged']

        print(f"Kích thước dữ liệu: {X.shape[0]} bản ghi, {X.shape[1]} đặc trưng.")
        print(f"Phân phối nhãn target (Merged vs Rejected): {dict(y.value_counts())}")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )

        # 1. Baseline Random Forest
        rf_base = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_base.fit(X_train, y_train)
        y_pred_rf = rf_base.predict(X_test)
        print("\n--- 1. Baseline Random Forest ---")
        print(classification_report(y_test, y_pred_rf, digits=4))

        # 2. SMOTE + Random Forest
        smote = SMOTE(random_state=42)
        X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
        rf_smote = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_smote.fit(X_train_sm, y_train_sm)
        y_pred_smote = rf_smote.predict(X_test)
        print("\n--- 2. SMOTE Oversampling + Random Forest ---")
        print(classification_report(y_test, y_pred_smote, digits=4))

        # 3. Soft Ensemble (RF + CatBoost / XGBoost)
        estimators = [('rf', rf_smote)]
        if HAS_XGB:
            estimators.append(('xgb', XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss')))
        if HAS_CAT:
            estimators.append(('cat', CatBoostClassifier(iterations=100, random_state=42, verbose=0)))
        
        ensemble = VotingClassifier(estimators=estimators, voting='soft')
        ensemble.fit(X_train_sm, y_train_sm)
        y_pred_ens = ensemble.predict(X_test)
        
        print("\n--- 3. Soft Voting Ensemble ---")
        print(classification_report(y_test, y_pred_ens, digits=4))

    print("\n" + "=" * 70)
    print("🎉 HOÀN THÀNH HUẤN LUYỆN VÀ ĐÁNH GIÁ MÔ HÌNH!")
    print("=" * 70)

if __name__ == "__main__":
    evaluate_models()
