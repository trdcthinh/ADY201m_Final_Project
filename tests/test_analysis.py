import pytest
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIGURES_DIR = os.path.join(BASE_DIR, "docs", "figures")

def test_figures_exist_and_non_empty():
    """Kiểm tra tất cả các file biểu đồ PNG đều tồn tại và dung lượng > 0 byte."""
    expected_figures = [
        "bq1_pr_lifecycle.png",
        "bq2_rejection_rates.png",
        "bq3_code_scale.png",
        "bq4_review_culture.png",
        "bq5_feature_importance.png",
        "shap_summary.png"
    ]
    
    for fig_name in expected_figures:
        fig_path = os.path.join(FIGURES_DIR, fig_name)
        assert os.path.exists(fig_path), f"Thiếu file biểu đồ: {fig_name}"
        assert os.path.getsize(fig_path) > 0, f"File biểu đồ rỗng: {fig_name}"
