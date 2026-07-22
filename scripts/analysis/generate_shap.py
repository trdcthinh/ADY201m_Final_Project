import sys
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import shap

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_prs.csv")
FIGURES_DIR = os.path.join(BASE_DIR, "docs", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

def generate_shap_plot():
    print("=" * 60)
    print("🔮 BẮT ĐẦU TÍNH TOÁN VÀ XUẤT SHAP FEATURE IMPORTANCE (NOT MERGED PRS)...")
    print("=" * 60)

    if not os.path.exists(INPUT_PATH):
        print(f"❌ Không tìm thấy dữ liệu tại: {INPUT_PATH}")
        return

    df = pd.read_csv(INPUT_PATH)
    
    # Preprocessing & One-Hot Encoding
    df_processed = pd.get_dummies(df, columns=['repo_language', 'keyword'], drop_first=False)
    df_fpt = df_processed[df_processed['is_fpt'] == 1]
    
    # Exclude identifiers and datetime target/duration columns, keeping body_len, created_hour, additions, deletions, etc.
    drop_cols = [
        'pr_id', 'repo_name', 'pr_number', 'title', 'user_login', 'user_type', 
        'created_datetime', 'closed_datetime', 'merged_datetime', 'duration_minutes', 'duration_hours', 'is_merged', 'is_fpt'
    ]
    
    X = df_fpt.drop(columns=[c for c in drop_cols if c in df_fpt.columns])
    y = df_fpt['is_merged']
    
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)
    
    print("🌲 Đang huấn luyện mô hình Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_resampled, y_resampled)
    
    print("📊 Đang tính toán SHAP Values...")
    explainer = shap.TreeExplainer(rf_model)
    shap_values = explainer.shap_values(X_resampled)
    
    plt.figure(figsize=(9, 6))
    
    # Handle list vs ndarray shap_values format
    if isinstance(shap_values, list):
        target_shap = shap_values[0] # Class 0: Not Merged PRs
    elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
        target_shap = shap_values[:, :, 0] # Class 0
    else:
        target_shap = shap_values
        
    shap.summary_plot(
        target_shap, 
        X_resampled, 
        plot_type='bar', 
        show=False, 
        max_display=10
    )
    
    plt.title("SHAP Feature Importance (Not Merged PRs)", fontsize=14, pad=15)
    plt.tight_layout()
    
    output_path = os.path.join(FIGURES_DIR, "shap_summary.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Đã xuất biểu đồ SHAP chuẩn khớp báo cáo vào: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    generate_shap_plot()
