import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Reconfigure stdout/stderr to UTF-8 to prevent console encode errors
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

CSV_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "crawled_prs.csv")
OUTPUT_PLOT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "figures", "pca_pr_visualization.png")

def main():
    print("=" * 60)
    print("🧠 PCA PR DATA VISUALIZATION")
    print("=" * 60)
    
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: CSV file '{CSV_FILE}' not found! Please run the crawler first.")
        return
        
    print(f"📖 Reading dataset from '{CSV_FILE}'...")
    df = pd.read_csv(CSV_FILE)
    
    # 1. Select numeric features for PCA
    numeric_features = [
        "body_len", "duration_minutes", "comments", "review_comments", 
        "commits", "additions", "deletions", "changed_files", 
        "repo_stars", "repo_forks"
    ]
    
    # Ensure all selected features exist in the dataframe
    numeric_features = [f for f in numeric_features if f in df.columns]
    print(f"📊 Numeric features selected for PCA: {numeric_features}")
    
    # Extract feature matrix X and target labels y
    X = df[numeric_features].copy()
    y = df["is_fpt"].copy()
    
    # 2. Preprocessing: Handle missing values
    # Fill NaN values with median of each column
    missing_count = X.isnull().sum().sum()
    if missing_count > 0:
        print(f"⚠️ Found {missing_count} missing values. Filling with column medians...")
        X = X.fillna(X.median())
        
    # Remove rows where all features are zero (if any) or handle constant columns
    # Let's drop columns that have zero variance (all values identical)
    constant_cols = [col for col in X.columns if X[col].nunique() <= 1]
    if constant_cols:
        print(f"⚠️ Dropping columns with zero variance: {constant_cols}")
        X = X.drop(columns=constant_cols)
        numeric_features = [f for f in numeric_features if f not in constant_cols]
        
    print(f"📐 Data shape for PCA: {X.shape}")
    
    # 3. Standardize the features (Mean=0, Variance=1)
    # StandardScaler is critical since features have highly different scales (e.g. stars vs changed_files)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 4. Apply Principal Component Analysis (PCA)
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    
    # Create a DataFrame for the PCA results
    pca_df = pd.DataFrame(data=X_pca, columns=["PC1", "PC2"])
    pca_df["is_fpt"] = y.values
    pca_df["Category"] = pca_df["is_fpt"].map({1: "FPT University PRs", 0: "Global PRs"})
    
    # Explain Variance Ratio
    var_exp = pca.explained_variance_ratio_
    print(f"\n📈 Variance Explained by PC1: {var_exp[0]*100:.2f}%")
    print(f"📈 Variance Explained by PC2: {var_exp[1]*100:.2f}%")
    print(f"📈 Total Variance Explained: {sum(var_exp)*100:.2f}%")
    
    # 5. Output feature loadings to understand PC interpretation
    loadings = pd.DataFrame(
        pca.components_.T, 
        columns=["PC1", "PC2"], 
        index=numeric_features
    )
    print("\n🔍 Feature Loadings (Weights on Principal Components):")
    print(loadings.round(3))
    
    # 6. Generate the Visualization Plot
    print(f"\n🎨 Generating PCA plot...")
    plt.figure(figsize=(10, 8), dpi=150)
    sns.set_theme(style="whitegrid")
    
    # Palette
    colors = {"FPT University PRs": "#FF7F0E", "Global PRs": "#1F77B4"}
    
    # Scatter Plot
    sns.scatterplot(
        x="PC1", 
        y="PC2", 
        hue="Category", 
        data=pca_df, 
        palette=colors,
        alpha=0.6,
        edgecolor="w",
        linewidth=0.5,
        s=40
    )
    
    # Title & Labels
    plt.title("2D PCA Visualization: FPT vs. Global Pull Requests", fontsize=16, fontweight="bold", pad=15)
    plt.xlabel(f"Principal Component 1 ({var_exp[0]*100:.1f}% Variance Explained)", fontsize=12)
    plt.ylabel(f"Principal Component 2 ({var_exp[1]*100:.1f}% Variance Explained)", fontsize=12)
    
    # Legend
    plt.legend(title="PR Dataset Source", fontsize=11, title_fontsize=12, loc="upper right")
    
    # Tight Layout and Save
    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT)
    plt.close()
    
    print(f"💾 PCA plot successfully saved to '{OUTPUT_PLOT}'!")
    print("=" * 60)

if __name__ == "__main__":
    main()
