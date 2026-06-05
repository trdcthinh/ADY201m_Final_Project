# Phân tích Đối chiếu & Xây dựng Mô hình Cảnh báo Sớm cho Pull Request

Dự án nghiên cứu so sánh quy trình kiểm duyệt mã nguồn (Review Pull Request) giữa môi trường dự án công nghiệp mã nguồn mở toàn cầu và môi trường đồ án học thuật tại **Đại học FPT (FPT University)**. Dự án xây dựng một **Mô hình Cảnh báo Sớm** giúp đánh giá xác suất một PR mới có nguy cơ bị Revert hoặc Đóng thất bại nhằm tối ưu hóa thời gian review.

Môn học: **ADY201m - Introduction to Data Science** | Lớp: **AI2013** | Giảng viên hướng dẫn: **Thầy Đặng Văn Hiếu**

## 👥 Thành viên nhóm & Phân công nhiệm vụ

| STT | Họ và Tên | MSSV | Vai trò | Nhiệm vụ |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Đặng Cao Cường** | HE204075 | Data Engineer | Cào dữ liệu qua GitHub API, Thiết kế DB, SQL Queries, Quản lý Git/GitHub |
| 2 | **Đào Thế Việt** | HE204143 | Data Scientist | Phân tích toán/thống kê, Xây dựng Mô hình dự đoán Hồi quy Logistic |
| 3 | **Trần Đức Thịnh** | HE201309 | Data Analyst | Tiền xử lý dữ liệu (Pandas/NumPy), Trực quan hóa kết quả, Báo cáo & Slide |

---

## 📂 Cấu trúc Thư mục Dự án

```text
fpt-repo-checking/
├── data/                     # Thư mục dữ liệu
│   ├── raw/                  # Dữ liệu thô cào về (CSV, JSON)
│   ├── processed/            # Dữ liệu sạch sau khi tiền xử lý
│   └── bad_data/             # Các tệp dữ liệu lỗi, không hợp lệ
├── database/                 # Các file SQL thiết kế cơ sở dữ liệu và truy vấn phân tích
├── models/                   # Chứa các file mô hình hồi quy đã được huấn luyện (.pkl, .joblib)
├── notebooks/                # Các file Jupyter Notebook (.ipynb) để EDA và huấn luyện mô hình
├── docs/                     # Tài liệu báo cáo, slide và hình ảnh
│   └── figures/              # Biểu đồ kết quả trực quan hóa
├── scripts/                  # Mã nguồn Python
│   ├── crawl/                # Scripts thu thập dữ liệu (check_prs.py, crawl_prs.py)
│   ├── clean/                # Scripts tiền xử lý dữ liệu (.py)
│   ├── analysis/             # Scripts phân tích & vẽ biểu đồ (business_ques_ans.py, pca_visualization.py)
│   └── modeling/             # Scripts huấn luyện và dự đoán từ mô hình (.py)
├── .env.example              # Mẫu file cấu hình môi trường chứa biến GITHUB_TOKEN
├── .gitignore                # Khai báo các file loại trừ không commit lên GitHub
├── requirements.txt          # Các thư viện Python cần cài đặt
└── README.md                 # Tài liệu hướng dẫn sử dụng (File này)
```

---

## 🚀 Hướng dẫn Cài đặt & Chạy Dự án

### 1. Chuẩn bị môi trường Python
Khuyên dùng môi trường ảo `venv` để tránh xung đột thư viện:

```bash
# Tạo môi trường ảo (ví dụ đặt tên là .venv)
python -m venv .venv

# Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Trên Windows (CMD):
.venv\Scripts\activate.bat
# Trên macOS/Linux:
source .venv/bin/activate
```

### 2. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 3. Cấu hình GitHub Token để cào dữ liệu
Do GitHub API giới hạn số lượng request đối với người dùng không xác thực, bạn cần cấu hình mã **Personal Access Token (PAT)**:
1. Tạo một bản sao từ file `.env.example` và đặt tên là `.env` ở thư mục gốc:
   ```bash
   cp .env.example .env
   ```
2. Mở file `.env` vừa tạo và điền mã Token GitHub của bạn:
   ```env
   GITHUB_TOKEN=ghp_your_actual_token_here
   ```

### 4. Chạy các Scripts trong dự án

* **Kiểm tra tính khả thi lượng dữ liệu:**
  ```bash
  python scripts/crawl/check_prs.py
  ```
* **Cào chi tiết Pull Requests:**
  ```bash
  python scripts/crawl/crawl_prs.py
  ```
  *Dữ liệu thô sau khi thu thập sẽ được ghi trực tiếp vào `data/raw/crawled_prs.csv`.*
* **Phân tích 5 câu hỏi kinh doanh & Trực quan hóa dashboard:**
  ```bash
  python scripts/analysis/business_ques_ans.py
  ```
* **Phân tích giảm chiều PCA & Trực quan hóa cụm FPT vs Global:**
  ```bash
  python scripts/analysis/pca_visualization.py
  ```
  *Biểu đồ kết quả sẽ được lưu tự động vào thư mục `docs/figures/pca_pr_visualization.png`.*
