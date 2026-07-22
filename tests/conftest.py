import pytest
import pandas as pd
import numpy as np
import os
import sqlite3

@pytest.fixture
def mock_raw_df():
    """Tạo DataFrame thô giả lập để kiểm thử làm sạch và import DB."""
    data = {
        'pr_id': [101, 102, 103],
        'repo_full_name': ['fpt-student/prj301', 'fpt-student/prj301', 'global/vscode'],
        'pr_number': [1, 2, 15],
        'title': ['Fix bug login', 'Add feat payment', 'Refactor parser'],
        'body_len': [25, 100, 0],
        'user_login': ['dev1', 'dev2', 'dev3'],
        'user_type': ['User', 'User', 'User'],
        'created_at': ['2026-05-01T10:00:00Z', '2026-05-02T12:00:00Z', '2026-05-03T15:30:00Z'],
        'closed_at': ['2026-05-01T10:30:00Z', '2026-05-02T13:00:00Z', None],
        'merged_at': ['2026-05-01T10:30:00Z', None, None],
        'duration_minutes': [30.0, 60.0, 0.0],
        'comments': [2, 5, 0],
        'review_comments': [1, 0, 0],
        'commits': [3, 10, 1],
        'additions': [150, 450, 20],
        'deletions': [20, 100, 5],
        'changed_files': [4, 12, 1],
        'repo_language': ['Java', 'Java', 'TypeScript'],
        'repo_stars': [10, 10, 15000],
        'repo_forks': [2, 2, 3000],
        'is_fpt': [1, 1, 0],
        'keyword': ['PRJ301', 'PRJ301', 'VSCode']
    }
    return pd.DataFrame(data)

@pytest.fixture
def in_memory_db():
    """Tạo kết nối SQLite trên bộ nhớ tạm (In-Memory DB)."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql"))
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
    conn.commit()
    yield conn
    conn.close()
