import os
import csv
import json
import time
import sys
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Reconfigure stdout/stderr to use UTF-8 to handle emojis and special characters on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# --- CONFIGURATION ---
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_FALLBACK_TOKEN_HERE")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

KEYWORDS_FPT = ["SWP391", "PRJ301", "SEP490", "Capstone FPT", "FPT University"]
GLOBAL_LANGUAGES = ["python", "javascript", "java", "go", "cpp", "typescript", "csharp", "php", "ruby", "html"]

CSV_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "crawled_prs.csv")
METADATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "search_metadata.json")

# Thread safety lock for CSV writing
csv_lock = threading.Lock()

def request_with_retry(url, params=None, is_search=False):
    """
    Sends a GET request to GitHub API with robust handling for:
    - Search API rate limit (30 requests/min)
    - Core API rate limit (5000 requests/hour)
    - Secondary rate limits / abuse detection
    - Network glitches and timeouts
    """
    max_retries = 5
    backoff = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=15)
            
            # Extract rate limit info from response headers
            rate_remaining = response.headers.get("X-RateLimit-Remaining")
            rate_reset = response.headers.get("X-RateLimit-Reset")
            
            if response.status_code == 200:
                # If remaining core/search rate limit is extremely low, sleep until reset
                if rate_remaining and int(rate_remaining) < 5:
                    reset_time = int(rate_reset)
                    sleep_time = max(reset_time - int(time.time()), 0) + 1
                    print(f"\n⚠️ Rate limit almost exhausted. Remaining: {rate_remaining}. Sleeping for {sleep_time}s...")
                    time.sleep(sleep_time)
                return response
                
            elif response.status_code in [403, 429]:
                # Rate limit hit or abuse detection triggered
                body = {}
                try:
                    body = response.json()
                except Exception:
                    pass
                    
                message = body.get("message", "")
                is_secondary = "abuse" in message.lower() or "secondary" in message.lower()
                
                # Check Retry-After header first, then reset header
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    sleep_time = int(retry_after)
                elif rate_reset:
                    reset_time = int(rate_reset)
                    sleep_time = max(reset_time - int(time.time()), 0) + 1
                else:
                    sleep_time = backoff ** attempt
                
                print(f"\n🛑 GitHub Rate Limit Hit (Status {response.status_code}, Secondary Limit: {is_secondary}).")
                print(f"Message: {message}")
                print(f"Sleeping for {sleep_time}s before retrying...")
                time.sleep(sleep_time)
                continue
                
            else:
                print(f"\n❌ HTTP {response.status_code} for URL: {url}. Retrying in {backoff ** attempt}s...")
                time.sleep(backoff ** attempt)
                
        except requests.exceptions.RequestException as e:
            print(f"\n🔌 Connection error: {e}. Retrying in {backoff ** attempt}s...")
            time.sleep(backoff ** attempt)
            
    print(f"\n💥 Failed to fetch {url} after {max_retries} retries.")
    return None

def fetch_search_results(query, target_count):
    """
    Fetches up to target_count PRs from GitHub Search matching the query.
    Filters out bots.
    """
    prs = []
    page = 1
    per_page = 100
    
    print(f"🔍 Searching for query: '{query}'...")
    
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
            break  # No more results
            
        for item in items:
            user_type = item.get("user", {}).get("type", "")
            user_login = item.get("user", {}).get("login", "")
            
            # Filter out bot PRs
            if user_type == "Bot" or "[bot]" in user_login.lower():
                continue
                
            prs.append({
                "number": item.get("number"),
                "title": item.get("title"),
                "url": item.get("pull_request", {}).get("url"), # Detailed PR API endpoint
                "html_url": item.get("html_url")
            })
            
            if len(prs) >= target_count:
                break
                
        print(f"   Collected {len(prs)}/{target_count} PRs (Page {page})")
        page += 1
        
        # Sleep slightly to avoid search secondary limits (max 30 requests/min)
        time.sleep(2)
        
    return prs

def gather_metadata():
    """
    Searches for FPT and Global PRs and returns a metadata list.
    Saves search metadata to metadata file to allow quick restarts without re-searching.
    """
    if os.path.exists(METADATA_FILE):
        print(f"📖 Found existing search metadata file '{METADATA_FILE}'. Loading...")
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
            
    print("🚀 Gathering FPT PR metadata...")
    fpt_prs = []
    seen_fpt_urls = set()
    
    # Search each keyword for FPT
    for keyword in KEYWORDS_FPT:
        query = f"is:pr is:closed {keyword}"
        # We need 1000 in total. We search each keyword and take up to 400 from each to maintain diversity
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
            
    print(f"✅ Total FPT PRs gathered: {len(fpt_prs)}")
    
    print("\n🚀 Gathering Global PR metadata...")
    global_prs = []
    seen_global_urls = set()
    
    # Get 100 non-bot PRs from 10 languages
    for lang in GLOBAL_LANGUAGES:
        query = f"is:pr is:closed language:{lang}"
        results = fetch_search_results(query, target_count=100)
        for r in results:
            if r["url"] not in seen_global_urls:
                seen_global_urls.add(r["url"])
                r["is_fpt"] = 0
                r["keyword"] = "global"
                global_prs.append(r)
                
    print(f"✅ Total Global PRs gathered: {len(global_prs)}")
    
    all_prs = fpt_prs[:1000] + global_prs[:1000]
    
    # Save metadata so we can resume easily
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_prs, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved {len(all_prs)} metadata entries to '{METADATA_FILE}'")
    
    return all_prs

def parse_pr_details(pr_data, is_fpt, keyword):
    """
    Extracts relevant metrics from GitHub Pull Request and Repository API data.
    """
    repo_data = pr_data.get("base", {}).get("repo", {}) or {}
    
    # Calculate PR resolution duration in minutes
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

def crawl_details_worker(pr, existing_keys, total_count, progress_counter):
    """
    Worker function to fetch detailed PR data and write to CSV in a thread-safe manner.
    """
    url = pr["url"]
    is_fpt = pr["is_fpt"]
    keyword = pr["keyword"]
    
    # Build a unique key for checking existing rows
    # Extract owner and repo name from URL (e.g. https://api.github.com/repos/owner/repo/pulls/num)
    parts = url.split('/')
    owner = parts[-4]
    repo = parts[-3]
    num = pr["number"]
    key = f"{owner}/{repo}#{num}"
    
    if key in existing_keys:
        return True # Already crawled
        
    response = request_with_retry(url)
    if not response:
        return False
        
    try:
        pr_data = response.json()
        row = parse_pr_details(pr_data, is_fpt, keyword)
        
        # Write to CSV in a thread-safe way
        with csv_lock:
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(row)
                f.flush()
                
        # Update progress
        progress_counter[0] += 1
        pct = (progress_counter[0] / total_count) * 100
        print(f"\r📥 Progress: {progress_counter[0]}/{total_count} ({pct:.1f}%) | Crawled: {owner}/{repo}#{num}", end="", flush=True)
        return True
    except Exception as e:
        print(f"\n❌ Error parsing PR {key}: {e}")
        return False

def main():
    print("=" * 60)
    print("🐙 GITHUB PR CRAWLER (1000 Global & 1000 FPT University PRs)")
    print("=" * 60)
    
    # Step 1: Gather list of PRs to crawl
    all_prs = gather_metadata()
    total_to_crawl = len(all_prs)
    print(f"\n📋 Total PRs in target list: {total_to_crawl}")
    
    # Step 2: Initialize CSV and check existing crawled PRs for resumption
    headers = [
        "pr_id", "repo_full_name", "pr_number", "title", "body_len", 
        "user_login", "user_type", "created_at", "closed_at", "merged_at", 
        "duration_minutes", "comments", "review_comments", "commits", 
        "additions", "deletions", "changed_files", "repo_language", 
        "repo_stars", "repo_forks", "is_fpt", "keyword"
    ]
    
    existing_keys = set()
    if os.path.exists(CSV_FILE):
        print(f"📂 Found existing CSV file '{CSV_FILE}'. Reading already crawled PRs for resumption...")
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
            print(f"🔄 Resuming crawling. Already crawled {len(existing_keys)} PRs.")
        except Exception as e:
            print(f"⚠️ Error reading CSV for resumption: {e}. Starting fresh.")
            # Delete and write headers
            with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    else:
        # Create CSV and write headers
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
    # Remove already completed PRs from queue
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
    print(f"📊 Completed: {completed_count}/{total_to_crawl} | Remaining: {remaining_count}")
    
    if remaining_count == 0:
        print("\n🎉 All PRs have already been crawled! The dataset is complete.")
        return
        
    # Step 3: Fetch details concurrently
    # We use a ThreadPoolExecutor with 8 workers to run faster without hitting abuse limits
    num_workers = 8
    print(f"\n⚡ Crawling details using {num_workers} concurrent threads...")
    
    progress_counter = [completed_count]
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(crawl_details_worker, pr, existing_keys, total_to_crawl, progress_counter): pr for pr in prs_queue}
        
        try:
            for future in as_completed(futures):
                pr = futures[future]
                try:
                    success = future.result()
                    if not success:
                        # Re-add to queue or handle error
                        pass
                except Exception as e:
                    url = pr["url"]
                    print(f"\n💥 Thread raised exception for {url}: {e}")
        except KeyboardInterrupt:
            print("\n🛑 Crawling paused by user. Progress saved. Run again to resume!")
            executor.shutdown(wait=False, cancel_futures=True)
            return

    print(f"\n\n🎉 Done! All PR details saved to '{CSV_FILE}'.")
    
if __name__ == "__main__":
    main()
