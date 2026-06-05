import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

import os

# 1. LOAD DATA
csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "crawled_prs.csv")
df = pd.read_csv(csv_path)
df['Project_Type'] = df['is_fpt'].map({1: 'FPT University', 0: 'Global PR'})

# ==========================================
# CỰC KỲ QUAN TRỌNG: LOGIC BẮT REJECT MỚI
# ==========================================
# Ép cột duration_minutes về dạng số. Dòng nào bị rỗng (PR thất bại) sẽ tự biến thành NaN
df['duration_minutes'] = pd.to_numeric(df['duration_minutes'], errors='coerce')

# Bắt Reject: Cứ ô nào bị NaN ở thời gian thì gán nhãn 1 (Thất bại)
df['is_rejected'] = df['duration_minutes'].isna().astype(int)

# In ra Terminal để nghiệm thu xem bắt được bao nhiêu con Reject
print("Kiểm tra phân bổ nhãn (0 = Merged, 1 = Rejected):")
print(df['is_rejected'].value_counts())
print("-" * 30)

# ==========================================
# SETUP KHUNG VẼ DASHBOARD
# ==========================================
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(3, 2, figsize=(18, 16))

# BQ1: VÒNG ĐỜI PR
sns.boxplot(data=df, x='Project_Type', y='duration_minutes', hue='Project_Type', legend=False, ax=axes[0, 0], palette='Set2')
axes[0, 0].set_title('BQ1: Vòng đời PR (Duration Minutes)')
axes[0, 0].set_yscale('log')
axes[0, 0].set_ylabel('Phút (Log scale)')

# BQ2: TỶ LỆ RỦI RO & TỪ CHỐI
rejection_rates = df.groupby('Project_Type')['is_rejected'].mean() * 100
sns.barplot(x=rejection_rates.index, y=rejection_rates.values, hue=rejection_rates.index, legend=False, ax=axes[0, 1], palette='Set1')
axes[0, 1].set_title('BQ2: Tỷ lệ PR bị từ chối (%)')
axes[0, 1].set_ylabel('Phần trăm (%)')

# BQ3: QUY MÔ THAY ĐỔI
sns.boxplot(data=df, x='Project_Type', y='changed_files', hue='Project_Type', legend=False, ax=axes[1, 0], palette='Set3')
axes[1, 0].set_title('BQ3: Quy mô thay đổi (Số file sửa)')
axes[1, 0].set_yscale('log')

# BQ4: VĂN HÓA KIỂM DUYỆT 
df_melted_comments = df.melt(id_vars=['Project_Type'], value_vars=['comments', 'review_comments'], 
                             var_name='Comment_Type', value_name='Count')
sns.barplot(data=df_melted_comments, x='Project_Type', y='Count', hue='Comment_Type', ax=axes[1, 1], estimator='mean')
axes[1, 1].set_title('BQ4: Tương tác & Văn hóa Kiểm duyệt')
axes[1, 1].set_ylabel('Trung bình số bình luận')

# BQ5: CẢNH BÁO SỚM (Logistic Regression)
# Chỉ train mô hình nếu bắt được từ 2 classes (có cả PR thành công và thất bại)
if df['is_rejected'].nunique() < 2:
    axes[2, 0].text(0.5, 0.5, "LỖI DATA:\nChưa bắt được PR Reject!\nHãy kiểm tra lại file CSV.", 
                    horizontalalignment='center', verticalalignment='center', fontsize=14, color='red')
    axes[2, 0].set_title('BQ5: LỖI THIẾU DỮ LIỆU')
else:
    features = ['duration_minutes', 'additions', 'deletions', 'changed_files', 'comments', 'review_comments']
    
    # Những PR bị Reject thì duration_minutes đang là NaN, ta fill = 0 để model chạy được
    X = df[features].fillna(0)
    y = df['is_rejected']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_scaled, y)

    importance_df = pd.DataFrame({'Feature': features, 'Importance (Weight)': model.coef_[0]})
    importance_df = importance_df.sort_values(by='Importance (Weight)', key=abs, ascending=False)

    sns.barplot(data=importance_df, x='Importance (Weight)', y='Feature', hue='Feature', legend=False, ax=axes[2, 0], palette='coolwarm')
    axes[2, 0].set_title('BQ5: Sức ảnh hưởng của các biến (Weights)')
    axes[2, 0].set_xlabel('Mức độ tác động tới nguy cơ bị từ chối')

# Ẩn ô thừa và ép layout cực rộng rãi, nói không với đè chữ
axes[2, 1].axis('off')
plt.tight_layout(pad=3.0, w_pad=4.0, h_pad=6.0)

plt.show()