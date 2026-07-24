-- ============================================================
-- SQL DATA WRANGLING & ANALYTICS QUERIES
-- Target DBMS: SQLite 3.x
-- Objectives: Data Validation, Feature Engineering, Business Intelligence
-- ============================================================

PRAGMA foreign_keys = ON;

-- ============================================================
-- PHẦN 1: KIỂM TRA THỐNG KÊ TỔNG QUAN (DB HEALTH CHECK)
-- ============================================================

-- 1.1. Thống kê tổng số lượng bản ghi trên từng bảng
SELECT 'repositories' AS table_name, COUNT(*) AS total_rows FROM repositories
UNION ALL
SELECT 'pull_requests' AS table_name, COUNT(*) AS total_rows FROM pull_requests
UNION ALL
SELECT 'raw_pull_requests' AS table_name, COUNT(*) AS total_rows FROM raw_pull_requests;

-- 1.2. Phân bổ mẫu dữ liệu: FPT University vs. Global PRs
SELECT 
    is_fpt,
    CASE is_fpt WHEN 1 THEN 'FPT University' ELSE 'Global PRs' END AS group_name,
    COUNT(*) AS pr_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM pull_requests), 2) AS percentage
FROM pull_requests
GROUP BY is_fpt;

-- 1.3. Thống kê phân bổ ngôn ngữ lập trình theo tập dữ liệu
SELECT 
    repo_language,
    COUNT(*) AS repo_count,
    SUM(CASE WHEN is_fpt = 1 THEN 1 ELSE 0 END) AS fpt_repos,
    SUM(CASE WHEN is_fpt = 0 THEN 1 ELSE 0 END) AS global_repos
FROM repositories r
JOIN pull_requests p ON r.repo_id = p.repo_id
GROUP BY repo_language
ORDER BY repo_count DESC;


-- ============================================================
-- PHẦN 2: CHUẨN HÓA & TRÍCH XUẤT ĐẶC TRƯNG (DATA WRANGLING VIEW)
-- ============================================================

-- View view_pr_clean thực hiện:
-- 1. Xử lý giá trị thiếu (COALESCE cho title, body_len, duration).
-- 2. Chuẩn hóa chuỗi thời gian sang định dạng DATETIME (yyyy-mm-dd hh:mm:ss).
-- 3. Trích xuất đặc trưng thời gian (created_hour, created_day_of_week).
-- 4. Xác định nhãn phân loại (is_merged: 1 = Merged, 0 = Rejected/Closed).

DROP VIEW IF EXISTS view_pr_clean;
CREATE VIEW view_pr_clean AS
SELECT 
    p.pr_id,
    r.repo_name,
    p.pr_number,
    COALESCE(p.title, 'No Title') AS title,
    COALESCE(p.body_len, 0) AS body_len,
    p.user_login,
    p.user_type,
    
    -- Định dạng Datetime chuẩn ISO
    datetime(p.created_at) AS created_datetime,
    datetime(p.closed_at) AS closed_datetime,
    datetime(p.merged_at) AS merged_datetime,
    
    -- Trích xuất đặc trưng thời gian phục vụ mô hình hóa
    CAST(strftime('%H', p.created_at) AS INTEGER) AS created_hour,
    CAST(strftime('%w', p.created_at) AS INTEGER) AS created_day_of_week,
    
    -- Chuẩn hóa thời gian xử lý (Phút & Giờ)
    COALESCE(p.duration_minutes, 0.0) AS duration_minutes,
    ROUND(COALESCE(p.duration_minutes, 0.0) / 60.0, 2) AS duration_hours,
    
    p.comments,
    p.review_comments,
    p.commits,
    p.additions,
    p.deletions,
    p.changed_files,
    
    r.repo_language,
    r.repo_stars,
    r.repo_forks,
    
    p.is_fpt,
    p.keyword,
    
    -- Nhãn kết quả PR (Target Variable)
    CASE WHEN p.merged_at IS NOT NULL THEN 1 ELSE 0 END AS is_merged
FROM pull_requests p
JOIN repositories r ON p.repo_id = r.repo_id;


-- ============================================================
-- PHẦN 3: PHÂN TÍCH VÀ GIẢI QUYẾT 5 CÂU HỎI KINH DOANH
-- ============================================================

-- Câu hỏi 1: Vòng đời Pull Request (PR Lifecycle)
-- So sánh thời gian xử lý PR trung bình giữa sinh viên FPT và cộng đồng quốc tế.
SELECT 
    CASE is_fpt WHEN 1 THEN 'FPT University' ELSE 'Global PRs' END AS group_name,
    COUNT(*) AS merged_prs_count,
    ROUND(AVG(duration_minutes), 2) AS avg_duration_mins,
    ROUND(AVG(duration_minutes) / 60.0, 2) AS avg_duration_hours,
    ROUND(MIN(duration_minutes), 2) AS min_duration_mins,
    ROUND(MAX(duration_minutes) / 60.0 / 24.0, 2) AS max_duration_days
FROM view_pr_clean
WHERE is_merged = 1
GROUP BY is_fpt;

-- Câu hỏi 2: Tỷ lệ Từ chối PR (Rejection Rate Analysis)
-- Đánh giá tỷ lệ PR bị đóng mà không được tích hợp (is_merged = 0).
SELECT 
    CASE is_fpt WHEN 1 THEN 'FPT University' ELSE 'Global PRs' END AS group_name,
    COUNT(*) AS total_prs,
    SUM(CASE WHEN is_merged = 1 THEN 1 ELSE 0 END) AS merged_prs,
    SUM(CASE WHEN is_merged = 0 THEN 1 ELSE 0 END) AS rejected_prs,
    ROUND(SUM(CASE WHEN is_merged = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS rejection_rate_percent
FROM view_pr_clean
GROUP BY is_fpt;

-- Câu hỏi 3: Quy mô thay đổi mã nguồn (Code Churn Metrics)
-- So sánh khối lượng dòng code thêm, xóa và số lượng file chỉnh sửa.
SELECT 
    CASE is_fpt WHEN 1 THEN 'FPT University' ELSE 'Global PRs' END AS group_name,
    ROUND(AVG(additions), 2) AS avg_additions,
    ROUND(AVG(deletions), 2) AS avg_deletions,
    ROUND(AVG(changed_files), 2) AS avg_changed_files,
    MAX(changed_files) AS max_changed_files_single_pr
FROM view_pr_clean
GROUP BY is_fpt;

-- Câu hỏi 4: Mức độ tương tác và kiểm duyệt (Review Culture & Collaboration)
-- Phân tích tần suất thảo luận, nhận xét mã nguồn và tỷ lệ PR không có phản hồi.
SELECT 
    CASE is_fpt WHEN 1 THEN 'FPT University' ELSE 'Global PRs' END AS group_name,
    ROUND(AVG(comments), 2) AS avg_conversation_comments,
    ROUND(AVG(review_comments), 2) AS avg_inline_review_comments,
    ROUND(AVG(commits), 2) AS avg_commits_count,
    ROUND(SUM(CASE WHEN comments = 0 AND review_comments = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS no_comment_pr_rate_percent
FROM view_pr_clean
GROUP BY is_fpt;

-- Câu hỏi 5: Tương quan giữa Quy mô PR và Tỷ lệ Từ chối (PR Size vs. Rejection Risk)
-- Phân nhóm PR theo số file thay đổi để khảo sát xác suất bị từ chối.
SELECT 
    CASE is_fpt WHEN 1 THEN 'FPT University' ELSE 'Global PRs' END AS group_name,
    CASE 
        WHEN changed_files <= 2 THEN 'Small (1-2 files)'
        WHEN changed_files <= 5 THEN 'Medium (3-5 files)'
        WHEN changed_files <= 15 THEN 'Large (6-15 files)'
        ELSE 'Huge (>15 files)'
    END AS pr_size,
    COUNT(*) AS pr_count,
    ROUND(SUM(CASE WHEN is_merged = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS rejection_rate_percent
FROM view_pr_clean
GROUP BY is_fpt, 
    CASE 
        WHEN changed_files <= 2 THEN 'Small (1-2 files)'
        WHEN changed_files <= 5 THEN 'Medium (3-5 files)'
        WHEN changed_files <= 15 THEN 'Large (6-15 files)'
        ELSE 'Huge (>15 files)'
    END
ORDER BY is_fpt, pr_size;

