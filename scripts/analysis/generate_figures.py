import sys
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình đường dẫn tương đối
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_prs.csv")
FIGURES_DIR = os.path.join(BASE_DIR, "docs", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Thiết lập style vẽ biểu đồ
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12

def main():
    print("=" * 60)
    print("📊 BẮT ĐẦU TRỰC QUAN HÓA CÁC BIỂU ĐỒ BQ1 - BQ5...")
    print("=" * 60)

    if not os.path.exists(INPUT_PATH):
        print(f"❌ Không tìm thấy dữ liệu sạch tại: {INPUT_PATH}")
        return

    df = pd.read_csv(INPUT_PATH)
    df['Project_Type'] = df['is_fpt'].map({1: 'FPT University', 0: 'Global PR'})
    print(f"📂 Kích thước dữ liệu sạch: {df.shape}")

    # BQ1: Lifecycle
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='Project_Type', y='duration_hours', hue='Project_Type', legend=False, palette='pastel')
    plt.title('BQ1: Pull Request Lifecycle Comparison (Log Scale)', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Lifetime (Hours - Log Scale)', fontsize=12)
    plt.xlabel('Project Group', fontsize=12)
    plt.yscale('log')
    plt.savefig(os.path.join(FIGURES_DIR, "bq1_pr_lifecycle.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Đã xuất biểu đồ BQ1: bq1_pr_lifecycle.png")

    # BQ2: Rejection Rate
    df['is_rejected'] = (df['is_merged'] == 0).astype(int)
    bq2_rates = df.groupby('Project_Type')['is_rejected'].mean() * 100

    plt.figure(figsize=(7, 5))
    ax = sns.barplot(x=bq2_rates.index, y=bq2_rates.values, hue=bq2_rates.index, legend=False, palette='coolwarm')
    plt.title('BQ2: Pull Request Rejection Rate (%)', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Rejection Rate (%)', fontsize=12)
    plt.xlabel('Project Group', fontsize=12)
    plt.ylim(0, 15)

    for p in ax.patches:
        ax.annotate(f"{p.get_height():.2f}%", (p.get_x() + p.get_width() / 2., p.get_height() + 0.3),
                    ha='center', va='center', fontsize=11, color='black', xytext=(0, 5),
                    textcoords='offset points', fontweight='semibold')

    plt.savefig(os.path.join(FIGURES_DIR, "bq2_rejection_rates.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Đã xuất biểu đồ BQ2: bq2_rejection_rates.png")

    # BQ3: Scale of Changes
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='Project_Type', y='changed_files', hue='Project_Type', legend=False, palette='Set3')
    plt.title('BQ3: Code Modification Scale (Number of Changed Files)', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Number of Changed Files (Log Scale)', fontsize=12)
    plt.xlabel('Project Group', fontsize=12)
    plt.yscale('log')
    plt.savefig(os.path.join(FIGURES_DIR, "bq3_code_scale.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Đã xuất biểu đồ BQ3: bq3_code_scale.png")

    # BQ4: Review Interactions
    df_comments = df.melt(id_vars=['Project_Type'], value_vars=['comments', 'review_comments'],
                          var_name='Comment_Type', value_name='Count')
    df_comments['Comment_Type'] = df_comments['Comment_Type'].map({
        'comments': 'General Comments',
        'review_comments': 'Inline Review Comments'
    })

    plt.figure(figsize=(9, 6))
    sns.barplot(data=df_comments, x='Project_Type', y='Count', hue='Comment_Type', palette='muted', errorbar=None)
    plt.title('BQ4: Comparison of Code Review Interactions', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Average Number of Comments', fontsize=12)
    plt.xlabel('Project Group', fontsize=12)
    plt.legend(title="Comment Type")
    plt.savefig(os.path.join(FIGURES_DIR, "bq4_review_culture.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Đã xuất biểu đồ BQ4: bq4_review_culture.png")

    # BQ5: Feature Weights
    features = ['additions', 'deletions', 'changed_files', 'comments', 'review_comments']
    X = df[features]
    y = df['is_rejected']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_scaled, y)

    importance_df = pd.DataFrame({
        'Feature': [f.replace('_', ' ').title() for f in features],
        'Weight (Coefficients)': model.coef_[0]
    }).sort_values(by='Weight (Coefficients)', key=abs, ascending=False)

    plt.figure(figsize=(8, 6))
    sns.barplot(data=importance_df, x='Weight (Coefficients)', y='Feature', hue='Feature', legend=False, palette='coolwarm')
    plt.axvline(x=0, color='grey', linestyle='--')
    plt.title('BQ5: Coefficients of Early Warning Indicators for PR Rejection', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Regression Coefficient (Weight)', fontsize=12)
    plt.ylabel('Feature', fontsize=12)
    plt.savefig(os.path.join(FIGURES_DIR, "bq5_feature_importance.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Đã xuất biểu đồ BQ5: bq5_feature_importance.png")
    print("=" * 60)

if __name__ == "__main__":
    main()
