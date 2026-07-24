import os
import csv
import json
import time
import sys
from datetime import datetime
import requests
from dotenv import load_dotenv

# Thiết lập UTF-8 cho stdout/stderr trên môi trường Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ------------------------------------------------------------
# THIẾT LẬP CẤU HÌNH HỆ THỐNG
# ------------------------------------------------------------
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_FALLBACK_TOKEN_HERE")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

KEYWORDS_FPT = ["SWP391", "PRJ301", "SEP490", "Capstone FPT", "FPT University"]
GLOBAL_LANGUAGES = ["python", "javascript", "java", "go", "cpp", "typescript", "csharp", "php", "ruby", "html"]

CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "crawled_prs.csv"))
METADATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "search_metadata.json"))


def request_with_retry(url: str, params: dict = None, is_search: bool = False):
    """
    Thực hiện gửi HTTP GET Request tới GitHub REST API.
    Tự động xử lý giới hạn tần suất (Rate Limiting) và cơ chế thử lại (Backoff Policy).
    """
    max_retries = 5
    backoff = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=15)
            
            rate_remaining = response.headers.get("X-RateLimit-Remaining")
            rate_reset = response.headers.get("X-RateLimit-Reset")
            
            if response.status_code == 200:
                if rate_remaining and int(rate_remaining) < 5:
                    reset_time = int(rate_reset)
                    sleep_time = max(reset_time - int(time.time()), 0) + 1
                    print(f"\n[WARNING] Tần suất API sắp chạm ngưỡng. Còn lại: {rate_remaining}. Tạm dừng {sleep_time}s...")
                    time.sleep(sleep_time)
                return response
                
            elif response.status_code in [403, 429]:
                body = {}
                try:
                    body = response.json()
                except Exception:
                    pass
                    
                message = body.get("message", "")
                is_secondary = "abuse" in message.lower() or "secondary" in message.lower()
                
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    sleep_time = int(retry_after)
                elif rate_reset:
                    reset_time = int(rate_reset)
                    sleep_time = max(reset_time - int(time.time()), 0) + 1
                else:
                    sleep_time = backoff ** attempt
                
                print(f"\n[WARNING] GitHub API Rate Limit (Mã HTTP {response.status_code}, Giới hạn phụ: {is_secondary}).")
                print(f"[INFO] Chi tiết: {message}")
                print(f"[INFO] Tạm dừng {sleep_time}s trước khi thử lại...")
                time.sleep(sleep_time)
                continue
                
            else:
                print(f"\n[ERROR] HTTP {response.status_code} cho URL: {url}. Thử lại sau {backoff ** attempt}s...")
                time.sleep(backoff ** attempt)
                
        except requests.exceptions.RequestException as e:
            print(f"\n[ERROR] Lỗi kết nối mạng: {e}. Thử lại sau {backoff ** attempt}s...")
            time.sleep(backoff ** attempt)
            
    print(f"\n[ERROR] Không thể lấy dữ liệu từ URL {url} sau {max_retries} lần thử.")
    return None


def fetch_search_results(query: str, target_count: int) -> list:
    """
    Truy vấn danh sách Pull Request từ GitHub Search API theo từ khóa hoặc ngôn ngữ.
    Lọc bỏ các tài khoản tự động (Bot Accounts).
    """
    prs = []
    page = 1
    per_page = 100
    
    print(f"[INFO] Tìm kiếm truy vấn: '{query}'...")
    
    while len(prs) < target_count:
        url = "https://api.github.com/search/issues"
        params = {
            "q": query,
            "per_page": per_page,
            "page": page
        }
        
        response = request_with_retry(url, params=params, is_search=True)
        if not response:
            break
            
        data = response.json()
        items = data.get("items", [])
        if not items:
            break
            
        for item in items:
            user_type = item.get("user", {}).get("type", "")
            user_login = item.get("user", {}).get("login", "")
            
            # Loại bỏ các PR từ Bot
            if user_type == "Bot" or "[bot]" in user_login.lower():
                continue
                
            prs.append({
                "number": item.get("number"),
                "title": item.get("title"),
                "url": item.get("pull_request", {}).get("url"),
                "html_url": item.get("html_url")
            })
            
            if len(prs) >= target_count:
                break
                
        print(f"   -> Đã thu thập: {len(prs)}/{target_count} PRs (Trang {page})")
        page += 1
        time.sleep(2)
        
    return prs


def gather_metadata() -> list:
    """
    Thu thập danh sách metadata của cả 2 tập dữ liệu: FPT University và Global PRs.
    Lưu thông tin danh mục vào file JSON để phục vụ khôi phục khi ngắt kết nối.
    """
    if os.path.exists(METADATA_FILE):
        print(f"[INFO] Phát hiện tệp metadata có sẵn '{METADATA_FILE}'. Đang tải dữ liệu...")
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
            
    print("[INFO] Đang thu thập dữ liệu Metadata cho nhóm FPT University...")
    fpt_prs = []
    seen_fpt_urls = set()
    
    for keyword in KEYWORDS_FPT:
        query = f"is:pr is:closed {keyword}"
        results = fetch_search_results(query, target_count=400)
        for r in results:
            if r["url"] not in seen_fpt_urls:
                seen_fpt_urls.add(r["url"])
                r["is_fpt"] = 1
                r["keyword"] = keyword
                fpt_prs.append(r)
                if len(fpt_prs) >= 1000:
                    break
        if len(fpt_prs) >= 1000:
            break
            
    print(f"[SUCCESS] Đã thu thập {len(fpt_prs)} metadata PR nhóm FPT.")
    
    print("\n[INFO] Đang thu thập dữ liệu Metadata cho nhóm Global PRs...")
    global_prs = []
    seen_global_urls = set()
    
    for lang in GLOBAL_LANGUAGES:
        query = f"is:pr is:closed language:{lang}"
        results = fetch_search_results(query, target_count=100)
        for r in results:
            if r["url"] not in seen_global_urls:
                seen_global_urls.add(r["url"])
                r["is_fpt"] = 0
                r["keyword"] = "global"
                global_prs.append(r)
                
    print(f"[SUCCESS] Đã thu thập {len(global_prs)} metadata PR nhóm Global.")
    
    all_prs = fpt_prs[:1000] + global_prs[:1000]
    
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_prs, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] Đã lưu {len(all_prs)} bản ghi metadata vào tệp '{METADATA_FILE}'.")
    
    return all_prs


def parse_pr_details(pr_data: dict, is_fpt: int, keyword: str) -> list:
    """
    Trích xuất các biến định lượng và đặc trưng định danh từ API response của PR.
    """
    repo_data = pr_data.get("base", {}).get("repo", {}) or {}
    
    created_at = pr_data.get("created_at")
    merged_at = pr_data.get("merged_at")
    duration_minutes = ""
    if created_at and merged_at:
        try:
            fmt = "%Y-%m-%dT%H:%M:%SZ"
            c_dt = datetime.strptime(created_at, fmt)
            m_dt = datetime.strptime(merged_at, fmt)
            duration_minutes = round((m_dt - c_dt).total_seconds() / 60.0, 2)
        except Exception:
            pass
            
    body = pr_data.get("body") or ""
    
    return [
        pr_data.get("id", ""),
        repo_data.get("full_name", ""),
        pr_data.get("number", ""),
        pr_data.get("title", ""),
        len(body),
        pr_data.get("user", {}).get("login", ""),
        pr_data.get("user", {}).get("type", ""),
        created_at,
        pr_data.get("closed_at", ""),
        merged_at,
        duration_minutes,
        pr_data.get("comments", 0),
        pr_data.get("review_comments", 0),
        pr_data.get("commits", 0),
        pr_data.get("additions", 0),
        pr_data.get("deletions", 0),
        pr_data.get("changed_files", 0),
        repo_data.get("language", "") or "Unknown",
        repo_data.get("stargazers_count", 0),
        repo_data.get("forks_count", 0),
        is_fpt,
        keyword
    ]


def main():
    print("=" * 70)
    print("  GITHUB PULL REQUEST DATA CRAWLER (FPT vs Global Dataset)")
    print("=" * 70)
    
    all_prs = gather_metadata()
    total_to_crawl = len(all_prs)
    print(f"\n[INFO] Tổng số PR cần thu thập: {total_to_crawl}")
    
    headers = [
        "pr_id", "repo_full_name", "pr_number", "title", "body_len", 
        "user_login", "user_type", "created_at", "closed_at", "merged_at", 
        "duration_minutes", "comments", "review_comments", "commits", 
        "additions", "deletions", "changed_files", "repo_language", 
        "repo_stars", "repo_forks", "is_fpt", "keyword"
    ]
    
    existing_keys = set()
    if os.path.exists(CSV_FILE):
        print(f"[INFO] Đã tìm thấy tệp CSV '{CSV_FILE}'. Kiểm tra dữ liệu cũ để tiếp tục...")
        try:
            with open(CSV_FILE, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header_row = next(reader, None)
                if header_row:
                    for row in reader:
                        if len(row) >= 3:
                            repo_name = row[1]
                            pr_num = row[2]
                            existing_keys.add(f"{repo_name}#{pr_num}")
            print(f"[INFO] Khôi phục tiến độ: Đã cào sẵn {len(existing_keys)} PRs.")
        except Exception as e:
            print(f"[WARNING] Không thể đọc tệp CSV cũ ({e}). Khởi tạo lại tệp mới.")
            with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    else:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
    prs_queue = []
    for pr in all_prs:
        url = pr["url"]
        parts = url.split('/')
        owner = parts[-4]
        repo = parts[-3]
        num = pr["number"]
        key = f"{owner}/{repo}#{num}"
        if key not in existing_keys:
            prs_queue.append(pr)
            
    remaining_count = len(prs_queue)
    completed_count = total_to_crawl - remaining_count
    print(f"[INFO] Đã hoàn thành: {completed_count}/{total_to_crawl} | Còn lại: {remaining_count}")
    
    if remaining_count == 0:
        print("\n[SUCCESS] Tất cả PRs đã được thu thập hoàn tất!")
        return
        
    print(f"\n[INFO] Thực thi cào chi tiết từng PR và ghi ra file CSV...")
    
    for idx, pr in enumerate(prs_queue, start=completed_count + 1):
        url = pr["url"]
        is_fpt = pr["is_fpt"]
        keyword = pr["keyword"]
        
        parts = url.split('/')
        owner = parts[-4]
        repo = parts[-3]
        num = pr["number"]
        
        response = request_with_retry(url)
        if response:
            try:
                pr_data = response.json()
                row = parse_pr_details(pr_data, is_fpt, keyword)
                
                with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
                    
                pct = (idx / total_to_crawl) * 100
                print(f"\r[PROGRESS] Tiến độ: {idx}/{total_to_crawl} ({pct:.1f}%) | Đã cào: {owner}/{repo}#{num}", end="", flush=True)
            except Exception as e:
                print(f"\n[ERROR] Lỗi xử lý dữ liệu PR {owner}/{repo}#{num}: {e}")
                
    print(f"\n\n[SUCCESS] Hoàn thành quá trình thu thập! Dữ liệu đã lưu tại '{CSV_FILE}'.")


if __name__ == "__main__":
    main()

