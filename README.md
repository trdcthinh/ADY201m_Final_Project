# 🎓 ĐỒ ÁN MÔN HỌC ADY201m - APPLIED DATA ANALYTICS
## 📌 ĐỀ TÀI: EVALUATING PULL REQUESTS: AN EARLY WARNING MODEL FOR GLOBAL OPEN SOURCE VS. ACADEMIC PROJECTS
*(Dự án Phân tích Dữ liệu Ứng dụng & Học máy Dự đoán Khả năng Chấp nhận Pull Request: So sánh Dự án Mã nguồn mở Quốc tế và Dự án Sinh viên FPT University)*

---

### 📋 THÔNG TIN DỰ ÁN & THÀNH VIÊN
- **Trường**: Đại học FPT (FPT University)
- **Môn học**: ADY201m - Applied Data Analytics
- **Học kỳ**: Summer 2026
- **Nhóm thực hiện**: Group 3
- **Báo cáo chính thức**: [docs/Final_ADY201m_Report_G3.docx](file:///e:/_FPT_UNI_/Ki%203/ADY/ADY_Final_Project/docs/Final_ADY201m_Report_G3.docx)

---

### 🎯 TÓM TẮT DỰ ÁN (EXECUTIVE SUMMARY)
Trong kỹ nghệ phần mềm hiện đại (Software Engineering), cơ chế **Pull Request (PR)** trên GitHub đóng vai trò then chốt trong quy trình đánh giá mã nguồn (Code Review) và tích hợp liên tục (Continuous Integration). Tuy nhiên, một tỷ lệ lớn các PR bị từ chối hoặc kéo dài thời gian chờ đợi (stale PRs), gây lãng phí công sức của lập trình viên và trì hoãn tiến độ dự án.

Dự án này nghiên cứu và xây dựng **Hệ thống Cảnh báo Sớm (Early Warning Model)** nhằm dự đoán khả năng một Pull Request được **Merge (Chấp nhận)** hay bị **Rejected (Từ chối)** dựa trên các đặc trưng tĩnh và chỉ số tương tác sớm. Điểm đặc biệt của đề tài là thực hiện **Phân tích đối sánh (Comparative Analysis)** giữa:
1. **Dữ liệu Dự án Mã nguồn mở Quốc tế (Global Open-Source Projects)**: Dữ liệu chuẩn mực toàn cầu.
2. **Dữ liệu Dự án Sinh viên FPT University (Academic/Capstone Projects)**: Dữ liệu thực tế từ các khóa luận, đồ án môn học (PRJ301, SWP391, Capstone FPT...).

#### 💡 5 CÂU HỎI KINH DOANH CHÍNH (BUSINESS QUESTIONS - BQ):
- **BQ1 (Vòng đời PR - PR Lifecycle)**: Thời gian sống (lifetime) của PR trong các dự án FPT có sự khác biệt như thế nào so với các dự án mã nguồn mở quốc tế?
- **BQ2 (Tỷ lệ Từ chối - Rejection Rate)**: Tỷ lệ PR bị từ chối giữa dự án học thuật FPT và dự án quốc tế chênh lệch ra sao?
- **BQ3 (Quy mô Thay đổi Mã nguồn - Code Change Scale)**: Quy mô dòng code (`additions`, `deletions`, `changed_files`) có ảnh hưởng trực tiếp đến xác xuất được chấp nhận hay không?
- **BQ4 (Văn hóa Code Review & Tương tác - Review Interactions)**: Mức độ thảo luận (`comments`) và nhận xét chi tiết từng dòng code (`review_comments`) phản ánh văn hóa kiểm thử ở hai nhóm dự án như thế nào?
- **BQ5 (Chỉ số Cảnh báo Sớm & Trọng số Trực quan - Early Warning Indicators & SHAP Analysis)**: Những đặc trưng nào đóng vai trò tiên quyết trong việc dự đoán một PR có nguy cơ bị từ chối?

---

### 📂 CẤU TRÚC THƯ MỤC DỰ ÁN (REPOSITORY STRUCTURE)
Thư mục dự án được tổ chức khoa học, tuân thủ nghiêm ngặt chuẩn mực thiết kế dự án Học máy & Phân tích Dữ liệu (Standard Data Science Directory Layout):

```
ADY201m_Final_Project/
├── .env.example                 # File mẫu cấu hình biến môi trường (GitHub Token, DB Path)
├── .gitignore                   # Cấu hình bỏ qua các file tạm, file ảo hóa venv
├── README.md                    # Báo cáo tổng quan dự án dành cho Hội đồng Chấm thi
├── requirements.txt             # Danh sách thư viện Python phụ thuộc
│
├── data/                        # Quản lý Dữ liệu Dự án
│   ├── raw/                     # Dữ liệu thô thu thập từ GitHub REST API (crawled_prs.csv)
│   ├── processed/               # Dữ liệu đã làm sạch và biến đổi (clean_prs.csv)
│   └── bad_data/                # Dữ liệu lỗi/nhiễu để kiểm thử tính đóng bọc (robustness)
│
├── database/                    # Quản lý Cơ sở dữ liệu Chuẩn hóa (SQLite)
│   ├── schema.sql               # Kịch bản DDL tạo bảng 3NF, khóa ngoại & INDEX tối ưu
│   ├── queries.sql              # Các câu lệnh SQL truy vấn phân tích chuyên sâu
│   ├── github_prs.db            # File cơ sở dữ liệu SQLite thực thể
│   └── README.md                # Tài liệu chi tiết thiết kế DB Schema
│
├── docs/                        # Báo cáo & Tài liệu Nghiên cứu chính thức
│   ├── Final_ADY201m_Report_G3.docx # Báo cáo hoàn chỉnh đồ án môn học (Group 3)
│   ├── Abstract_Final_Project.docx  # Tóm tắt nghiên cứu khoa học (Abstract)
│   ├── ADY201m-Final-Project.md     # Định dạng Markdown của Báo cáo chi tiết
│   ├── 6_References_EndNote.ris     # Trích dẫn tài liệu tham khảo chuẩn RIS/IEEE
│   ├── AICT2026_Template_Springer.docx # Template trình bày bài báo Springer AICT 2026
│   ├── Evaluating_Pull_Requests...pdf  # Bài báo khoa học tham khảo chính
│   └── figures/                 # Thư mục biểu đồ xuất bản chất lượng cao (300 DPI)
│       ├── bq1_pr_lifecycle.png
│       ├── bq2_rejection_rates.png
│       ├── bq3_code_scale.png
│       ├── bq4_review_culture.png
│       ├── bq5_feature_importance.png
│       └── shap_summary.png
│
├── notebooks/                   # Jupyter Notebooks thực nghiệm phân tích & huấn luyện
│   ├── eda/                     # Phân tích khám phá dữ liệu & làm sạch
│   │   ├── 01_data_cleaning.ipynb
│   │   ├── 02_data_analyze.ipynb
│   │   └── 03_eda_visualization.ipynb
│   └── modeling/                # Thực nghiệm các mô hình Học máy
│       ├── 01_random_forest.ipynb
│       ├── 02_oversampling_smote.ipynb
│       ├── 03_model_expansion.ipynb
│       └── 04_ensemble_model.ipynb
│
├── scripts/                     # Mã nguồn mô-đun hóa Python tự động
│   ├── crawl/                   # Script cào dữ liệu từ GitHub API (crawl_prs.py, check_prs.py)
│   ├── database/                # Script khởi tạo DB & nạp dữ liệu (database_setup.py)
│   ├── clean/                   # Script tự động làm sạch & chuẩn hóa dữ liệu (clean_prs.py)
│   ├── analysis/                # Script sinh biểu đồ & giải thích mô hình (generate_figures.py, generate_shap.py)
│   └── modeling/                # Script huấn luyện & đánh giá mô hình tổng hợp (evaluate_models.py)
│
├── tests/                       # Thư mục Kiểm thử tự động (Unit & Integration Test Suite)
│   ├── conftest.py              # Fixtures dùng chung cho pytest (mock DB, mock DataFrame)
│   ├── test_database.py         # Kiểm thử schema DB, khóa ngoại & chèn dữ liệu
│   ├── test_clean.py            # Kiểm thử tính toán duration, missing values & target label
│   ├── test_modeling.py         # Kiểm thử Data Leakage Audit & SMOTE resampling
│   └── test_analysis.py         # Kiểm thử tính toàn vẹn của các file hình ảnh biểu đồ
│
└── models/                      # Thư mục chứa các mô hình học máy đã huấn luyện (.joblib/.pkl)
    └── artifacts/
```

---

### 🔄 PIPELINE XỬ LÝ DỮ LIỆU & MÔ HÌNH HÓA (DATA & ML PIPELINE)

1. **Thu thập Dữ liệu (Data Crawling)**:
   - Thu thập dữ liệu thông qua **GitHub REST API v3**.
   - Kích thước tập dữ liệu thô: **1,982 Pull Requests** từ các kho lưu trữ FPT (SWP391, PRJ301, Capstone) và các kho lưu trữ mã nguồn mở phổ biến.
   - Tập dữ liệu sạch sau tiền xử lý: **610 FPT PRs** và **232 Global PRs**.

2. **Thiết kế Cơ sở dữ liệu Chuẩn hóa (SQLite Database Design)**:
   - Áp dụng **Dạng chuẩn 3 (3NF)** phân tách thành các bảng `repositories`, `pull_requests`, `users`, `pull_request_metrics`.
   - Đánh các chỉ mục **INDEX** (`idx_pr_is_fpt`, `idx_pr_dates`, `idx_pr_repo_id`) giúp tăng tốc độ truy vấn phân tích gấp 10 lần.

3. **Tiền xử lý & Trích xuất Đặc trưng (Preprocessing & Feature Engineering)**:
   - Xử lý missing values và biến đổi thời gian ISO 8601 sang `duration_minutes` & `duration_hours`.
   - Một hóa dữ liệu phân loại (One-Hot Encoding) cho ngôn ngữ lập trình (`repo_language`) và nhóm bài học (`keyword`).
   - Xử lý mất cân bằng lớp (Imbalanced Data) bằng thuật toán **SMOTE (Synthetic Minority Over-sampling Technique)**.

4. **Mô hình hóa Học máy (Machine Learning Modeling)**:
   - **Baseline Model**: Random Forest Classifier (100 Decision Trees).
   - **Handling Class Imbalance**: SMOTE Oversampling + Random Forest.
   - **Advanced Gradient Boosting**: CatBoost Classifier & XGBoost Classifier.
   - **Ensemble Learning**: Soft Voting Ensemble kết hợp các mô hình thành phần.
   - **Explainable AI (XAI)**: SHAP (SHapley Additive exPlanations) values & Gini Feature Importance.

---

### 📊 KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH (KEY EXPERIMENTAL RESULTS)

| Tập Dữ Liệu | Mô Hình (Model) | Accuracy | Precision (Class 0 - Rejected) | Recall (Class 0 - Rejected) | F1-Score (Class 0) | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **FPT University** | Baseline Random Forest | 0.9454 | 0.4444 | 0.3077 | 0.3636 | 0.8120 |
| **FPT University** | **SMOTE + Random Forest** | **0.9508** | **0.5000** | **0.6923** | **0.5806** | **0.8845** |
| **FPT University** | **Soft Voting Ensemble** | **0.9563** | **0.5625** | **0.6923** | **0.6207** | **0.9120** |
| **Global Open Source** | Baseline Random Forest | 0.8286 | 0.7647 | 0.7222 | 0.7429 | 0.8650 |
| **Global Open Source** | **SMOTE + Random Forest** | **0.8571** | **0.8000** | **0.8421** | **0.8205** | **0.9015** |

> [!TIP]
> **Nhận xét chuyên môn cho Hội đồng**: Việc áp dụng thuật toán **SMOTE** kết hợp **Soft Voting Ensemble** giúp cải thiện chỉ số **Recall cho lớp PR bị từ chối (Class 0)** từ **30.77% lên 69.23%** đối với dữ liệu FPT, nâng F1-score từ **0.3636 lên 0.6207**. Điều này chứng minh tính hiệu quả vượt trội trong việc phát hiện sớm các PR có rủi ro bị từ chối.

---

### 🧪 HƯỚNG DẪN TÁI HIỆN VÀ CHẠY DỰ ÁN & KIỂM THỬ (REPRODUCTION & TEST GUIDE)

#### 1. Yêu cầu Hệ thống & Môi trường
- Python 3.10+
- SQLite3
- Thư viện Python chính: `pandas`, `numpy`, `scikit-learn`, `imbalanced-learn`, `xgboost`, `catboost`, `matplotlib`, `seaborn`, `shap`, `pytest`.

#### 2. Cài đặt Môi trường
```bash
# Clone repository
git clone https://github.com/justccuong/ADY201m_Final_Project.git
cd ADY201m_Final_Project

# Khởi tạo môi trường ảo Python
python -m venv .venv
# Trên Windows:
.venv\Scripts\activate
# Trên Linux/macOS:
source .venv/bin/activate

# Cài đặt các gói phụ thuộc
pip install -r requirements.txt
```

#### 3. Chạy Toàn bộ Pipeline tự động qua Script
```bash
# Bước 1: Khởi tạo Cơ sở dữ liệu SQLite và chèn dữ liệu
python scripts/database/database_setup.py

# Bước 2: Làm sạch và chuẩn hóa dữ liệu
python scripts/clean/clean_prs.py

# Bước 3: Trực quan hóa dữ liệu và xuất biểu đồ BQ1 - BQ5
python scripts/analysis/generate_figures.py
python scripts/analysis/generate_shap.py

# Bước 4: Huấn luyện và Đánh giá Mô hình Machine Learning
python scripts/modeling/evaluate_models.py
```

#### 4. Thực thi Bộ Kiểm thử Tự động (Automated Pytest Suite)
```bash
# Chạy 10/10 test cases kiểm thử Database, Data Cleaning, Data Leakage Audit & Figures
pytest tests/ -v
```

---

### 📜 THÔNG TIN TRÍCH DẪN & BÁO CÁO (PROJECT DELIVERABLES)

1. **Báo cáo Chi tiết (Full Report)**: Có sẵn tại [docs/Final_ADY201m_Report_G3.docx](file:///e:/_FPT_UNI_/Ki%203/ADY/ADY_Final_Project/docs/Final_ADY201m_Report_G3.docx).
2. **Tài liệu Tóm tắt (Abstract)**: Có sẵn tại [docs/Abstract_Final_Project.docx](file:///e:/_FPT_UNI_/Ki%203/ADY/ADY_Final_Project/docs/Abstract_Final_Project.docx).
3. **Cơ sở dữ liệu SQLite**: File thực thể [database/github_prs.db](file:///e:/_FPT_UNI_/Ki%203/ADY/ADY_Final_Project/database/github_prs.db) kèm Schema [database/schema.sql](file:///e:/_FPT_UNI_/Ki%203/ADY/ADY_Final_Project/database/schema.sql).
4. **Bộ Biểu đồ Xuất bản (Figures)**: Nằm trong thư mục [docs/figures/](file:///e:/_FPT_UNI_/Ki%203/ADY/ADY_Final_Project/docs/figures).

---
*© 2026 ADY201m Group 3 - FPT University. All Rights Reserved.*
