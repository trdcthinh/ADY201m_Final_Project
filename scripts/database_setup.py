import os
import sys
import sqlite3
import pandas as pd
import numpy as np

# Reconfigure stdout/stderr to use UTF-8 to handle emojis and special characters on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


# Đường dẫn đến các file liên quan
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    
    # Kích hoạt hỗ trợ khóa ngoại
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 2. Đọc và thực thi schema.sql để khởi tạo bảng
    print(f"📖 Đọc schema từ: {SCHEMA_PATH}")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("✅ Đã khởi tạo các bảng và index thành công.")
    
    # 3. Đọc dữ liệu từ CSV bằng Pandas
    if not os.path.exists(CSV_PATH):
        print(f"❌ Lỗi: Không tìm thấy file dữ liệu thô tại '{CSV_PATH}'")
        return
        
    print(f"📂 Đang tải dữ liệu từ CSV: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"📊 Đã tải {len(df)} dòng dữ liệu từ CSV.")
    
    # Chuẩn hóa các giá trị NaN/NaT thành None để lưu vào DB dưới dạng NULL
    df = df.replace({np.nan: None})
    
    # Xóa dữ liệu cũ nếu chạy lại script
    cursor.execute("DELETE FROM pull_requests;")
    cursor.execute("DELETE FROM repositories;")
    cursor.execute("DELETE FROM raw_pull_requests;")
    conn.commit()
    
    # 4. Import dữ liệu thô vào bảng raw_pull_requests (staging table)
    print("📥 Đang import dữ liệu thô vào bảng raw_pull_requests...")
    # Chuyển đổi DataFrame thành list các tuple
    raw_data = df.to_records(index=False).tolist()
    
    # Thực hiện chèn hàng loạt
    cursor.executemany("""
        INSERT INTO raw_pull_requests (
            pr_id, repo_full_name, pr_number, title, body_len, 
            user_login, user_type, created_at, closed_at, merged_at, 
            duration_minutes, comments, review_comments, commits, 
            additions, deletions, changed_files, repo_language, 
            repo_stars, repo_forks, is_fpt, keyword
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, raw_data)
    conn.commit()
    print(f"✅ Đã import thành công {cursor.rowcount} dòng vào bảng raw_pull_requests.")
    
    # 5. Phân tách và import dữ liệu vào bảng repositories
    print("🛠️ Đang trích xuất và chuẩn hóa bảng repositories...")
    
    # Nhóm theo repo_full_name để trích xuất repo duy nhất
    repos_df = df.groupby("repo_full_name").agg({
        "repo_language": lambda x: next((lang for lang in x if lang is not None), "Unknown"),
        "repo_stars": "max",
        "repo_forks": "max"
    }).reset_index()
    
    # Ghi đè trường hợp language trống
    repos_df["repo_language"] = repos_df["repo_language"].fillna("Unknown")
    
    # Chuẩn hóa NaN/None của repo data
    repos_df = repos_df.replace({np.nan: None})
    repo_tuples = repos_df.to_records(index=False).tolist()
    
    cursor.executemany("""
        INSERT INTO repositories (repo_name, repo_language, repo_stars, repo_forks)
        VALUES (?, ?, ?, ?)
    """, repo_tuples)
    conn.commit()
    print(f"✅ Đã tạo {cursor.rowcount} repository duy nhất trong bảng repositories.")
    
    # 6. Lấy mapping của repo_name -> repo_id từ DB
    cursor.execute("SELECT repo_id, repo_name FROM repositories;")
    repo_mapping = {name: r_id for r_id, name in cursor.fetchall()}
    
    # 7. Import dữ liệu vào bảng pull_requests (Deduplicated)
    print("🛠️ Đang import dữ liệu vào bảng pull_requests (Loại bỏ trùng lặp và liên kết khóa ngoại)...")
    
    # Loại bỏ các PR trùng lặp dựa trên pr_id (giữ lại dòng đầu tiên)
    unique_prs_df = df.drop_duplicates(subset=["pr_id"])
    duplicate_count = len(df) - len(unique_prs_df)
    if duplicate_count > 0:
        print(f"⚠️ Phát hiện và loại bỏ {duplicate_count} PR trùng lặp trong dữ liệu thô.")
        
    pr_rows = []
    for _, row in unique_prs_df.iterrows():
        repo_name = row["repo_full_name"]
        repo_id = repo_mapping.get(repo_name)
        if repo_id is None:
            # Phòng trường hợp không ánh xạ được
            continue
            
        pr_rows.append((
            row["pr_id"],
            repo_id,
            row["pr_number"],
            row["title"],
            row["body_len"],
            row["user_login"],
            row["user_type"],
            row["created_at"],
            row["closed_at"],
            row["merged_at"],
            row["duration_minutes"],
            row["comments"],
            row["review_comments"],
            row["commits"],
            row["additions"],
            row["deletions"],
            row["changed_files"],
            row["is_fpt"],
            row["keyword"]
        ))
        
    cursor.executemany("""
        INSERT INTO pull_requests (
            pr_id, repo_id, pr_number, title, body_len, 
            user_login, user_type, created_at, closed_at, merged_at, 
            duration_minutes, comments, review_comments, commits, 
            additions, deletions, changed_files, is_fpt, keyword
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, pr_rows)
    conn.commit()
    print(f"✅ Đã import thành công {cursor.rowcount} PRs vào bảng pull_requests.")
    
    # 8. Hiển thị báo cáo tổng quan
    print("\n📊 BÁO CÁO CƠ SỞ DỮ LIỆU SAU KHI NẠP DỮ LIỆU:")
    cursor.execute("SELECT COUNT(*) FROM repositories")
    num_repos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pull_requests")
    num_prs = cursor.fetchone()[0]
    cursor.execute("SELECT is_fpt, COUNT(*) FROM pull_requests GROUP BY is_fpt")
    dist = cursor.fetchall()
    
    print(f" - Tổng số Repositories: {num_repos}")
    print(f" - Tổng số Pull Requests (đã chuẩn hóa): {num_prs}")
    for is_f, count in dist:
        group_name = "FPT University (Local)" if is_f == 1 else "Global Projects"
        print(f"   + {group_name}: {count} PRs")
        
    conn.close()
    print("\n🎉 HOÀN THÀNH SETUP DATABASE THÀNH CÔNG!")
    print("=" * 60)

if __name__ == "__main__":
    main()
