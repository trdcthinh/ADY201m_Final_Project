-- ============================================================
-- DATABASE SCHEMA: GITHUB PULL REQUEST ANALYSIS
-- Target DBMS: SQLite 3.x
-- Architecture: Staging -> Relational Schema (3NF)
-- ============================================================

-- Kích hoạt ràng buộc khóa ngoại (Foreign Key Constraints)
PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- 1. BẢNG NGUỒN / STAGING (Raw Data Import)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_pull_requests (
    pr_id           INTEGER,
    repo_full_name  TEXT,
    pr_number       INTEGER,
    title           TEXT,
    body_len        INTEGER,
    user_login      TEXT,
    user_type       TEXT,
    created_at      TEXT,
    closed_at       TEXT,
    merged_at       TEXT,
    duration_minutes REAL,
    comments        INTEGER,
    review_comments INTEGER,
    commits         INTEGER,
    additions       INTEGER,
    deletions       INTEGER,
    changed_files   INTEGER,
    repo_language   TEXT,
    repo_stars      INTEGER,
    repo_forks      INTEGER,
    is_fpt          INTEGER,
    keyword         TEXT
);

-- ------------------------------------------------------------
-- 2. BẢNG THỰC THỂ REPOSITORIES (Kho lưu trữ mã nguồn)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS repositories (
    repo_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_name     TEXT UNIQUE NOT NULL,
    repo_language TEXT,
    repo_stars    INTEGER DEFAULT 0,
    repo_forks    INTEGER DEFAULT 0
);

-- ------------------------------------------------------------
-- 3. BẢNG CHÍNH PULL_REQUESTS (Dữ liệu giao dịch PR)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pull_requests (
    pr_id            INTEGER PRIMARY KEY,
    repo_id          INTEGER NOT NULL,
    pr_number        INTEGER NOT NULL,
    title            TEXT,
    body_len         INTEGER,
    user_login       TEXT,
    user_type        TEXT,
    created_at       TEXT,
    closed_at        TEXT,
    merged_at        TEXT,
    duration_minutes REAL,
    comments         INTEGER DEFAULT 0,
    review_comments  INTEGER DEFAULT 0,
    commits          INTEGER DEFAULT 0,
    additions        INTEGER DEFAULT 0,
    deletions        INTEGER DEFAULT 0,
    changed_files    INTEGER DEFAULT 0,
    is_fpt           INTEGER CHECK(is_fpt IN (0, 1)),
    keyword          TEXT,
    FOREIGN KEY (repo_id) REFERENCES repositories (repo_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 4. TỐI ƯU HÓA HIỆU NĂNG TÌM KIẾM (Indexing)
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_pr_is_fpt   ON pull_requests(is_fpt);
CREATE INDEX IF NOT EXISTS idx_pr_repo_id  ON pull_requests(repo_id);
CREATE INDEX IF NOT EXISTS idx_pr_dates    ON pull_requests(created_at, merged_at, closed_at);

