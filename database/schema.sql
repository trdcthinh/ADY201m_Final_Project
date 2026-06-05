-- ==========================================
-- Database Schema for Pull Request Analysis
-- Designed for SQLite
-- ==========================================

-- Enable Foreign Key support in SQLite (needs to be run per connection)
PRAGMA foreign_keys = ON;

-- 1. Bảng tạm Staging chứa dữ liệu thô import trực tiếp từ file CSV
CREATE TABLE IF NOT EXISTS raw_pull_requests (
    pr_id INTEGER,
    repo_full_name TEXT,
    pr_number INTEGER,
    title TEXT,
    body_len INTEGER,
    user_login TEXT,
    user_type TEXT,
    created_at TEXT,
    closed_at TEXT,
    merged_at TEXT,
    duration_minutes REAL,
    comments INTEGER,
    review_comments INTEGER,
    commits INTEGER,
    additions INTEGER,
    deletions INTEGER,
    changed_files INTEGER,
    repo_language TEXT,
    repo_stars INTEGER,
    repo_forks INTEGER,
    is_fpt INTEGER,
    keyword TEXT
);

-- 2. Bảng chuẩn hóa Repositories (Danh sách các kho lưu trữ mã nguồn)
CREATE TABLE IF NOT EXISTS repositories (
    repo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_name TEXT UNIQUE NOT NULL,
    repo_language TEXT,
    repo_stars INTEGER DEFAULT 0,
    repo_forks INTEGER DEFAULT 0
);

-- 3. Bảng chuẩn hóa Pull Requests (Danh sách Pull Requests chi tiết)
CREATE TABLE IF NOT EXISTS pull_requests (
    pr_id INTEGER PRIMARY KEY,
    repo_id INTEGER NOT NULL,
    pr_number INTEGER NOT NULL,
    title TEXT,
    body_len INTEGER,
    user_login TEXT,
    user_type TEXT,
    created_at TEXT,
    closed_at TEXT,
    merged_at TEXT,
    duration_minutes REAL,
    comments INTEGER DEFAULT 0,
    review_comments INTEGER DEFAULT 0,
    commits INTEGER DEFAULT 0,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    changed_files INTEGER DEFAULT 0,
    is_fpt INTEGER CHECK(is_fpt IN (0, 1)),
    keyword TEXT,
    FOREIGN KEY (repo_id) REFERENCES repositories (repo_id) ON DELETE CASCADE
);

-- 4. Tạo các chỉ mục (INDEX) để tối ưu hiệu năng các câu truy vấn phân tích
CREATE INDEX IF NOT EXISTS idx_pr_is_fpt ON pull_requests(is_fpt);
CREATE INDEX IF NOT EXISTS idx_pr_repo_id ON pull_requests(repo_id);
CREATE INDEX IF NOT EXISTS idx_pr_dates ON pull_requests(created_at, merged_at, closed_at);
