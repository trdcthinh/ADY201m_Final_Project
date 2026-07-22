# 🎓 ADY201m FINAL PROJECT - APPLIED DATA ANALYTICS
## 📌 EVALUATING PULL REQUESTS: AN EARLY WARNING MODEL FOR GLOBAL OPEN SOURCE VS. ACADEMIC PROJECTS

[🇬🇧 English Version](#-english-default) | [🇻🇳 Bản Tiếng Việt](#-bản-tiếng-việt)

---

## 🇬🇧 ENGLISH (DEFAULT)

### 📋 PROJECT INFORMATION
- **Institution**: FPT University
- **Course**: ADY201m - Applied Data Analytics
- **Term**: Summer 2026
- **Team**: Group 3
- **Official Documentation**: [docs/Final_ADY201m_Report_G3.docx](file:///e:/_FPT_UNI_/Ki%203/ADY/ADY_Final_Project/docs/Final_ADY201m_Report_G3.docx)

---

### 🎯 EXECUTIVE SUMMARY
In modern Software Engineering, **Pull Requests (PRs)** on GitHub play a central role in Code Review and Continuous Integration (CI). However, a high proportion of PRs suffer from delays or rejection (stale/rejected PRs), wasting developer effort and stalling project progress.

This project designs an **Early Warning Model** to predict whether a Pull Request will be **Merged** or **Rejected** based on static code metrics and early interaction indicators. A core highlight of this research is a **Comparative Analysis** between:
1. **Global Open-Source Projects**: Industry standard GitHub repositories.
2. **FPT University Academic Projects**: Student repositories from Capstone, PRJ301, and SWP391 courses.

#### 💡 5 CORE BUSINESS QUESTIONS (BQ):
- **BQ1 (PR Lifecycle)**: How does PR lifetime compare between FPT student projects and global open-source repositories?
- **BQ2 (Rejection Rate)**: What is the disparity in PR rejection rates between academic FPT projects and global projects?
- **BQ3 (Code Change Scale)**: Does the scale of modifications (`additions`, `deletions`, `changed_files`) directly impact the likelihood of PR acceptance?
- **BQ4 (Review Interactions)**: How do general discussions (`comments`) and inline code reviews (`review_comments`) reflect review culture across both project groups?
- **BQ5 (Early Warning Indicators & SHAP Analysis)**: Which specific features act as early warning signals for PR rejection risk?

---

### 📂 REPOSITORY ARCHITECTURE
The repository follows standard Production-Grade Data Science Layout guidelines:

```
ADY201m_Final_Project/
├── .env.example                 # Environment variable template (GitHub Token, DB Path)
├── .gitignore                   # Ignore rules for virtual environments & temporary caches
├── README.md                    # Bilingual comprehensive project documentation
├── requirements.txt             # Dependency requirements list
│
├── data/                        # Project Data Management
│   ├── raw/                     # Raw GitHub REST API data (crawled_prs.csv)
│   ├── processed/               # Cleaned & transformed dataset (clean_prs.csv)
│   └── bad_data/                # Noise dataset for robustness testing
│
├── database/                    # Normalized SQLite Database (3NF)
│   ├── schema.sql               # DDL Script (3NF Tables, Foreign Keys, Indexes)
│   ├── queries.sql              # Analytical SQL queries
│   ├── github_prs.db            # SQLite database file
│   └── README.md                # DB Schema Documentation
│
├── docs/                        # Official Project Deliverables
│   ├── Final_ADY201m_Report_G3.docx # Official Group 3 Report (Word Document)
│   ├── Abstract_Final_Project.docx  # Academic Research Abstract
│   ├── ADY201m-Final-Project.md     # Markdown version of full report
│   ├── 6_References_EndNote.ris     # RIS/IEEE standard references
│   ├── AICT2026_Template_Springer.docx # Springer AICT 2026 paper template
│   └── figures/                 # High-resolution (300 DPI) publication charts
│       ├── bq1_pr_lifecycle.png
│       ├── bq2_rejection_rates.png
│       ├── bq3_code_scale.png
│       ├── bq4_review_culture.png
│       ├── bq5_feature_importance.png
│       └── shap_summary.png
│
├── notebooks/                   # Jupyter Notebook Experiments
│   ├── eda/                     # Data Cleaning & Exploratory Data Analysis
│   │   ├── 01_data_cleaning.ipynb
│   │   ├── 02_data_analyze.ipynb
│   │   └── 03_eda_visualization.ipynb
│   └── modeling/                # Machine Learning Experiments
│       ├── 01_random_forest.ipynb
│       ├── 02_oversampling_smote.ipynb
│       ├── 03_model_expansion.ipynb
│       └── 04_ensemble_model.ipynb
│
├── scripts/                     # Modular Automation Scripts
│   ├── crawl/                   # GitHub REST API Crawlers (crawl_prs.py, check_prs.py)
│   ├── database/                # SQLite Initialization & Setup (database_setup.py)
│   ├── clean/                   # Automated Preprocessing (clean_prs.py)
│   ├── analysis/                # Chart Generation & SHAP Analysis (generate_figures.py, generate_shap.py)
│   └── modeling/                # Model Training & Evaluation (evaluate_models.py)
│
├── tests/                       # Automated Test Suite (Pytest)
│   ├── conftest.py              # Shared fixtures (mock DB, mock DataFrame)
│   ├── test_database.py         # DB schema, foreign keys & insertion tests
│   ├── test_clean.py            # Preprocessing, duration & missing value tests
│   ├── test_modeling.py         # Data leakage audit & SMOTE isolation tests
│   └── test_analysis.py         # Figure PNG existence & non-empty tests
│
└── models/                      # Trained Model Binaries
    └── artifacts/
```

---

### 🔄 DATA & MACHINE LEARNING PIPELINE

1. **Data Collection**:
   - Crawled via **GitHub REST API v3**.
   - Raw Dataset: **1,982 Pull Requests** across FPT academic repos and global open-source repos.
   - Cleaned Dataset: **610 FPT PRs** vs **232 Global PRs**.

2. **Database Architecture**:
   - **Third Normal Form (3NF)** schema separating `repositories`, `pull_requests`, `users`, and `pull_request_metrics`.
   - Optimized with `INDEX` (`idx_pr_is_fpt`, `idx_pr_dates`, `idx_pr_repo_id`) boosting query performance by 10x.

3. **Preprocessing & Feature Engineering**:
   - Time conversion to `duration_minutes` & `duration_hours`.
   - One-Hot Encoding for categorical attributes (`repo_language`, `keyword`).
   - Class imbalance mitigation using **SMOTE (Synthetic Minority Over-sampling Technique)**.

4. **Machine Learning Modeling**:
   - **Baseline Model**: Random Forest Classifier (100 Decision Trees).
   - **Class Imbalance Handling**: SMOTE Oversampling + Random Forest.
   - **Gradient Boosting**: CatBoost Classifier & XGBoost Classifier.
   - **Ensemble Learning**: Soft Voting Ensemble.
   - **Explainable AI (XAI)**: SHAP (SHapley Additive exPlanations) values & Feature Importance.

---

### 📊 KEY EXPERIMENTAL RESULTS

| Dataset | Model | Accuracy | Precision (Class 0 - Rejected) | Recall (Class 0 - Rejected) | F1-Score (Class 0) | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **FPT University** | Baseline Random Forest | 0.9454 | 0.4444 | 0.3077 | 0.3636 | 0.8120 |
| **FPT University** | **SMOTE + Random Forest** | **0.9508** | **0.5000** | **0.6923** | **0.5806** | **0.8845** |
| **FPT University** | **Soft Voting Ensemble** | **0.9563** | **0.5625** | **0.6923** | **0.6207** | **0.9120** |
| **Global Open Source** | Baseline Random Forest | 0.8286 | 0.7647 | 0.7222 | 0.7429 | 0.8650 |
| **Global Open Source** | **SMOTE + Random Forest** | **0.8571** | **0.8000** | **0.8421** | **0.8205** | **0.9015** |

> [!TIP]
> **Key Finding**: Applying **SMOTE** alongside **Soft Voting Ensemble** increased **Recall for Rejected PRs (Class 0)** from **30.77% to 69.23%** on FPT data, boosting F1-score from **0.3636 to 0.6207**.

---

### 🛠️ REPRODUCTION & AUTOMATED TEST GUIDE

#### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/justccuong/ADY201m_Final_Project.git
cd ADY201m_Final_Project

# Create virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Execute Automated Pipeline Scripts
```bash
# Step 1: Database Setup & Data Insertion
python scripts/database/database_setup.py

# Step 2: Data Cleaning & Preprocessing
python scripts/clean/clean_prs.py

# Step 3: Figure Generation & SHAP Analysis
python scripts/analysis/generate_figures.py
python scripts/analysis/generate_shap.py

# Step 4: Machine Learning Model Training & Evaluation
python scripts/modeling/evaluate_models.py
```

#### 3. Run Automated Pytest Suite
```bash
# Run 10/10 automated tests covering DB, Cleaning, Leakage Audit & Figures
pytest tests/ -v
```

---

<br>

---

## 🇻🇳 BẢN TIẾNG VIỆT

### 📋 THÔNG TIN DỰ ÁN
- **Trường**: Đại học FPT (FPT University)
- **Môn học**: ADY201m - Applied Data Analytics
- **Học kỳ**: Summer 2026
- **Nhóm thực hiện**: Group 3
- **Báo cáo chính thức**: [docs/Final_ADY201m_Report_G3.docx](file:///e:/_FPT_UNI_/Ki%203/ADY/ADY_Final_Project/docs/Final_ADY201m_Report_G3.docx)

---

### 🎯 TÓM TẮT DỰ ÁN
Trong kỹ nghệ phần mềm hiện đại, cơ chế **Pull Request (PR)** trên GitHub đóng vai trò then chốt trong quy trình đánh giá mã nguồn (Code Review) và tích hợp liên tục (CI). Tuy nhiên, một tỷ lệ lớn các PR bị từ chối hoặc kéo dài thời gian chờ đợi (stale PRs), gây lãng phí công sức của lập trình viên và trì hoãn tiến độ dự án.

Dự án này nghiên cứu và xây dựng **Hệ thống Cảnh báo Sớm (Early Warning Model)** nhằm dự đoán khả năng một Pull Request được **Merge (Chấp nhận)** hay bị **Rejected (Từ chối)** dựa trên các đặc trưng tĩnh và chỉ số tương tác sớm. Điểm đặc biệt của đề tài là thực hiện **Phân tích đối sánh (Comparative Analysis)** giữa:
1. **Dữ liệu Dự án Mã nguồn mở Quốc tế (Global Open-Source Projects)**.
2. **Dữ liệu Dự án Sinh viên FPT University (Academic/Capstone Projects)**.

#### 💡 5 CÂU HỎI KINH DOANH CHÍNH (BQ):
- **BQ1 (Vòng đời PR)**: Thời gian sống (lifetime) của PR trong các dự án FPT có sự khác biệt như thế nào so với các dự án quốc tế?
- **BQ2 (Tỷ lệ Từ chối)**: Tỷ lệ PR bị từ chối giữa dự án học thuật FPT và dự án quốc tế chênh lệch ra sao?
- **BQ3 (Quy mô Thay đổi Mã nguồn)**: Quy mô dòng code (`additions`, `deletions`, `changed_files`) có ảnh hưởng trực tiếp đến xác xuất được chấp nhận hay không?
- **BQ4 (Văn hóa Code Review & Tương tác)**: Mức độ thảo luận (`comments`) và nhận xét chi tiết từng dòng code (`review_comments`) phản ánh văn hóa kiểm thử ở hai nhóm dự án như thế nào?
- **BQ5 (Chỉ số Cảnh báo Sớm & Trọng số Trực quan)**: Những đặc trưng nào đóng vai trò tiên quyết trong việc dự đoán một PR có nguy cơ bị từ chối?

---

### 🔄 TÓM TẮT KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH

| Tập Dữ Liệu | Mô Hình (Model) | Accuracy | Precision (Class 0 - Rejected) | Recall (Class 0 - Rejected) | F1-Score (Class 0) | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **FPT University** | Baseline Random Forest | 0.9454 | 0.4444 | 0.3077 | 0.3636 | 0.8120 |
| **FPT University** | **SMOTE + Random Forest** | **0.9508** | **0.5000** | **0.6923** | **0.5806** | **0.8845** |
| **FPT University** | **Soft Voting Ensemble** | **0.9563** | **0.5625** | **0.6923** | **0.6207** | **0.9120** |

---

### 🧪 HƯỚNG DẪN CHẠY KIỂM THỬ TỰ ĐỘNG (PYTEST)
```bash
# Thực thi 10/10 test cases tự động
pytest tests/ -v
```

---
*© 2026 ADY201m Group 3 - FPT University. All Rights Reserved.*
