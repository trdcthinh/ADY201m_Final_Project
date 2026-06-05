-- ============================================================
-- SQL DATA WRANGLING & ANALYSIS QUERIES
-- Designed for SQLite
-- ============================================================

-- BẬT hỗ trợ khóa ngoại
PRAGMA foreign_keys = ON;

-- ============================================================
-- PHẦN 1: KIỂM TRA THỐNG KÊ TỔNG QUAN (DB HEALTH CHECK)
-- ============================================================

-- 1.1. Kiểm tra số lượng dòng trong các bảng
SELECT 'repositories' AS table_name, COUNT(*) AS total_rows FROM repositories
UNION ALL
SELECT 'pull_requests' AS table_name, COUNT(*) AS total_rows FROM pull_requests
UNION ALL
SELECT 'raw_pull_requests' AS table_name, COUNT(*) AS total_rows FROM raw_pull_requests;

-- 1.2. Kiểm tra tỷ lệ phân bổ dữ liệu FPT vs Global
SELECT 
    is_fpt,
    CASE is_fpt WHEN 1 THEN 'FPT University' ELSE 'Global PRs' END AS group_name,
    COUNT(*) AS pr_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM pull_requests), 2) AS percentage
FROM pull_requests
GROUP BY is_fpt;

-- 1.3. Thống kê ngôn ngữ lập trình phổ biến nhất trong tập dữ liệu
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
-- PHẦN 2: DATA WRANGLING & DATA CLEANING VIA SQL VIEWS
-- ============================================================

-- Tạo View chuẩn hóa dữ liệu để phục vụ cho phân tích và làm sạch
-- View này xử lý các vấn đề:
-- 1. Xử lý giá trị NULL: Thay thế title/body trống bằng giá trị mặc định.
-- 2. Định dạng thời gian: Chuyển đổi định dạng chuỗi Datetime (ISO 8601) thành định dạng chuẩn SQLite.
-- 3. Phân tách thời gian: Trích xuất giờ tạo PR (hour) và ngày trong tuần (day of week) phục vụ dự đoán.
-- 4. Phân loại trạng thái PR: Xác định PR đã được Merge (Thành công) hay Bị đóng mà không merge (Bị từ chối).
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
    
    -- Chuyển đổi Datetime về chuẩn SQLite yyyy-mm-dd hh:mm:ss
    datetime(p.created_at) AS created_datetime,
    datetime(p.closed_at) AS closed_datetime,
    datetime(p.merged_at) AS merged_datetime,
    
    -- Trích xuất các thuộc tính thời gian
    CAST(strftime('%H', p.created_at) AS INTEGER) AS created_hour,
    -- 0=Chủ nhật, 1=Thứ hai, ..., 6=Thứ bảy
    CAST(strftime('%w', p.created_at) AS INTEGER) AS created_day_of_week,
    
    -- Xử lý thời gian duration
    COALESCE(p.duration_minutes, 0.0) AS duration_minutes,
    ROUND(COALESCE(p.duration_minutes, 0.0) / 60.0, 2) AS duration_hours,
    
    p.comments,
    p.review_comments,
    p.commits,
    p.additions,
    p.deletions,
    p.changed_files,
    
    -- Các trường từ repo liên kết
    r.repo_language,
    r.repo_stars,
    r.repo_forks,
    
    -- Nhãn phân loại
    p.is_fpt,
    p.keyword,
    
    -- Biến phân loại PR: 1 = Đã Merge (Thành công), 0 = Đóng mà không Merge (Bị từ chối/Revert)
    CASE WHEN p.merged_at IS NOT NULL THEN 1 ELSE 0 END AS is_merged
FROM pull_requests p
JOIN repositories r ON p.repo_id = r.repo_id;


-- ============================================================
-- PHẦN 3: GIẢI QUYẾT 5 CÂU HỎI KINH DOANH (BUSINESS QUESTIONS)
-- ============================================================

-- Câu hỏi 1: Vòng đời Pull Request (PR Lifecycle)
-- Thời gian xử lý PR trung bình và trung vị (Median proxy) của FPT vs Global.
-- (Chỉ tính cho các PR đã được merge để phản ánh thời gian hoàn thành công việc).
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

-- Câu hỏi 2: Tỷ lệ Từ chối & Rủi ro (Rejection Rate)
-- Tỷ lệ PR bị đóng mà không được merge (is_merged = 0) của FPT vs Global.
SELECT 
    CASE is_fpt WHEN 1 THEN 'FPT University' ELSE 'Global PRs' END AS group_name,
    COUNT(*) AS total_prs,
    SUM(CASE WHEN is_merged = 1 THEN 1 ELSE 0 END) AS merged_prs,
    SUM(CASE WHEN is_merged = 0 THEN 1 ELSE 0 END) AS rejected_prs,
    ROUND(SUM(CASE WHEN is_merged = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS rejection_rate_percent
FROM view_pr_clean
GROUP BY is_fpt;

-- Câu hỏi 3: Quy mô thay đổi mã nguồn (Code Chunks)
-- So sánh quy mô commit trung bình (số additions, deletions, changed_files)
SELECT 
    CASE is_fpt WHEN 1 THEN 'FPT University' ELSE 'Global PRs' END AS group_name,
    ROUND(AVG(additions), 2) AS avg_additions,
    ROUND(AVG(deletions), 2) AS avg_deletions,
    ROUND(AVG(changed_files), 2) AS avg_changed_files,
    MAX(changed_files) AS max_changed_files_single_pr
FROM view_pr_clean
GROUP BY is_fpt;

-- Câu hỏi 4: Văn hóa Kiểm duyệt & Tương tác (Review Culture)
-- So sánh mức độ thảo luận trên PR (comments, review_comments, commits)
SELECT 
    CASE is_fpt WHEN 1 THEN 'FPT University' ELSE 'Global PRs' END AS group_name,
    ROUND(AVG(comments), 2) AS avg_conversation_comments,
    ROUND(AVG(review_comments), 2) AS avg_inline_review_comments,
    ROUND(AVG(commits), 2) AS avg_commits_count,
    -- Tỷ lệ PR không có bình luận nào
    ROUND(SUM(CASE WHEN comments = 0 AND review_comments = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS no_comment_pr_rate_percent
FROM view_pr_clean
GROUP BY is_fpt;

-- Câu hỏi 5: Phân tích tương quan đặc trưng (Early Warning Correlation Proxy)
-- Xem xét tỷ lệ bị từ chối (rejection rate) theo quy mô số file thay đổi
-- (Để kiểm chứng xem có đúng là sửa càng nhiều file thì tỷ lệ bị reject càng cao không)
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
