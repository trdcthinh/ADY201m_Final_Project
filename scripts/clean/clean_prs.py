import os
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "crawled_prs.csv")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_prs.csv")

def clean_data():
    print("=" * 60)
    print("🧹 BẮT ĐẦU QUÁ TRÌNH LÀM SẠCH VÀ TIỀN XỬ LÝ DỮ LIỆU PR...")
    print("=" * 60)

    if not os.path.exists(RAW_PATH):
        print(f"❌ Lỗi: Không tìm thấy file dữ liệu thô tại '{RAW_PATH}'")
        return

    df = pd.read_csv(RAW_PATH)
    print(f"📂 Đã tải dữ liệu thô: {df.shape[0]} bản ghi, {df.shape[1]} cột.")

    if 'repo_full_name' in df.columns and 'repo_name' not in df.columns:
        df['repo_name'] = df['repo_full_name']

    # 1. Chuyển đổi Datetime và tính toán Feature thời gian
    for col in ['created_at', 'closed_at', 'merged_at']:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    df['created_datetime'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['closed_datetime'] = df['closed_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['merged_datetime'] = df['merged_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

    df['created_hour'] = df['created_at'].dt.hour
    df['created_day_of_week'] = df['created_at'].dt.dayofweek

    # 2. Tính toán thời gian sống của PR (duration_minutes & duration_hours)
    end_time = df['closed_at'].combine_first(df['merged_at'])
    df['duration_minutes'] = (end_time - df['created_at']).dt.total_seconds() / 60.0
    df['duration_hours'] = df['duration_minutes'] / 60.0

    # Target is_merged
    df['is_merged'] = df['merged_at'].notna().astype(int)

    # 3. Điền giá trị rỗng và làm sạch text
    if 'body_len' not in df.columns:
        df['body_len'] = df['body'].fillna('').apply(len) if 'body' in df.columns else 0

    df['user_type'] = df['user_type'].fillna('User') if 'user_type' in df.columns else 'User'
    df['repo_language'] = df['repo_language'].fillna('Unknown')
    df['keyword'] = df['keyword'].fillna('General')

    # 4. Sắp xếp các cột chuẩn hóa
    cols_order = [
        'pr_id', 'repo_name', 'pr_number', 'title', 'body_len', 'user_login', 'user_type',
        'created_datetime', 'closed_datetime', 'merged_datetime', 'created_hour', 'created_day_of_week',
        'duration_minutes', 'duration_hours', 'comments', 'review_comments', 'commits', 'additions',
        'deletions', 'changed_files', 'repo_language', 'repo_stars', 'repo_forks', 'is_fpt', 'keyword', 'is_merged'
    ]

    df_clean = df[[c for c in cols_order if c in df.columns]]
    
    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
    df_clean.to_csv(PROCESSED_PATH, index=False, encoding='utf-8')
    print(f"✅ Đã lưu dữ liệu sạch ({df_clean.shape[0]} bản ghi) vào: {PROCESSED_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    clean_data()
