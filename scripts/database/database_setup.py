import os
import sys
import sqlite3
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV_PATH = os.path.join(BASE_DIR, "data", "raw", "crawled_prs.csv")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
DB_PATH = os.path.join(BASE_DIR, "database", "github_prs.db")

def main():
    print("=" * 60)
    print("🚀 BẮT ĐẦU KHỞI TẠO CƠ SỞ DỮ LIỆU & IMPORT DATA...")
    print("=" * 60)
    
    # 1. Kết nối cơ sở dữ liệu SQLite
    print(f"🔗 Kết nối database SQLite tại: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 2. Đọc và thực thi schema.sql để khởi tạo bảng
    print(f"📖 Đọc schema từ: {SCHEMA_PATH}")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("✅ Đã khởi tạo các bảng và index thành công.")
    
    # 3. Đọc dữ liệu từ CSV
    if not os.path.exists(CSV_PATH):
        print(f"❌ Lỗi: Không tìm thấy file dữ liệu thô tại '{CSV_PATH}'")
        return
        
    print(f"📂 Đang tải dữ liệu từ CSV: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"📊 Tổng số bản ghi dữ liệu thô: {len(df)}")
    
    # Chuẩn hóa tên cột
    if 'repo_full_name' in df.columns and 'repo_name' not in df.columns:
        df['repo_name'] = df['repo_full_name']

    # Import vào bảng raw_pull_requests
    df.to_sql('raw_pull_requests', conn, if_exists='replace', index=False)
    print("  -> Đã chèn dữ liệu vào 'raw_pull_requests'.")

    # Import Repositories
    repos = df[['repo_name', 'repo_language', 'repo_stars', 'repo_forks']].drop_duplicates(subset=['repo_name'])
    for _, row in repos.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO repositories (repo_name, repo_language, repo_stars, repo_forks)
            VALUES (?, ?, ?, ?);
        """, (row['repo_name'], row['repo_language'], int(row['repo_stars'] if pd.notna(row['repo_stars']) else 0), int(row['repo_forks'] if pd.notna(row['repo_forks']) else 0)))

    # Import Pull Requests
    cursor.execute("SELECT repo_name, repo_id FROM repositories;")
    repo_map = dict(cursor.fetchall())

    pr_records = []
    for _, row in df.iterrows():
        repo_id = repo_map.get(row['repo_name'])
        if repo_id is None:
            continue
        pr_records.append((
            int(row['pr_id']), repo_id, int(row['pr_number']), 
            str(row['title']) if pd.notna(row.get('title')) else None,
            int(row.get('body_len', 0) if pd.notna(row.get('body_len')) else 0),
            str(row['user_login']) if pd.notna(row.get('user_login')) else None, 
            str(row['user_type']) if pd.notna(row.get('user_type')) else 'User',
            str(row['created_at']) if pd.notna(row.get('created_at')) else None, 
            str(row['closed_at']) if pd.notna(row.get('closed_at')) else None, 
            str(row['merged_at']) if pd.notna(row.get('merged_at')) else None,
            float(row.get('duration_minutes', 0) if pd.notna(row.get('duration_minutes')) else 0),
            int(row.get('comments', 0) if pd.notna(row.get('comments')) else 0),
            int(row.get('review_comments', 0) if pd.notna(row.get('review_comments')) else 0),
            int(row.get('commits', 0) if pd.notna(row.get('commits')) else 0),
            int(row.get('additions', 0) if pd.notna(row.get('additions')) else 0),
            int(row.get('deletions', 0) if pd.notna(row.get('deletions')) else 0),
            int(row.get('changed_files', 0) if pd.notna(row.get('changed_files')) else 0),
            int(row.get('is_fpt', 0)), 
            str(row['keyword']) if pd.notna(row.get('keyword')) else 'General'
        ))

    cursor.executemany("""
        INSERT OR REPLACE INTO pull_requests (
            pr_id, repo_id, pr_number, title, body_len, user_login, user_type,
            created_at, closed_at, merged_at, duration_minutes, comments, review_comments,
            commits, additions, deletions, changed_files, is_fpt, keyword
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, pr_records)

    conn.commit()
    conn.close()
    
    print("=" * 60)
    print("🎉 HOÀN THÀNH QUÁ TRÌNH KHỞI TẠO VÀ CHÈN DỮ LIỆU VÀO DATABASE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
