import requests
import time
import sys

# Reconfigure stdout/stderr to UTF-8 to prevent console encode errors on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_pr_feasibility(keywords):
    # Header tiêu chuẩn của GitHub API
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    print("🔍 BẮT ĐẦU QUÉT SỐ LƯỢNG PULL REQUEST (PR) HỢP LỆ...\n")
    total_valid_prs = 0
    
    for keyword in keywords:
        # Bộ lọc: Là PR + Đã Merge + Chứa từ khóa
        query = f"is:pr is:merged {keyword}"
        url = f"https://api.github.com/search/issues?q={query}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('total_count', 0)
            print(f"✅ Từ khóa '{keyword}': Tìm thấy {count} PR đã được merge.")
            total_valid_prs += count
        else:
            print(f"❌ Lỗi chặn API với '{keyword}': Mã {response.status_code}")
        
        # Nghỉ 2s giữa các lần quét để không bị GitHub đá văng
        time.sleep(2)

    print("-" * 40)
    print(f"🎯 TỔNG CỘNG DATA CÓ THỂ CÀO: {total_valid_prs} PR hợp lệ.")
    
    # Đánh giá khả năng làm Data Science
    if total_valid_prs >= 1000:
        print("🔥 Đánh giá: CỰC KỲ KHẢ THI! Đủ data để làm Hồi quy và Thống kê tẹt ga.")
    elif 500 <= total_valid_prs < 1000:
        print("⚠️ Đánh giá: TẠM ỔN. Đủ làm thống kê nhưng lúc dọn data (cleaning) phải thật khéo.")
    else:
        print("💀 Đánh giá: RẤT RỦI RO. Quá ít data, cần tìm thêm từ khóa đồ án khác.")

# Danh sách từ khóa test thử
keywords_fpt = ["SWP391", "PRJ301", "SEP490", "Capstone FPT", "FPT University"]
check_pr_feasibility(keywords_fpt)