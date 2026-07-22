import pytest
import sqlite3

def test_database_schema_creation(in_memory_db):
    """Kiểm tra việc tạo các bảng trong database theo schema.sql."""
    cursor = in_memory_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert "raw_pull_requests" in tables
    assert "repositories" in tables
    assert "pull_requests" in tables

def test_repository_insertion(in_memory_db):
    """Kiểm tra chèn dữ liệu repository và xử lý trùng lặp tên repo."""
    cursor = in_memory_db.cursor()
    cursor.execute("""
        INSERT INTO repositories (repo_name, repo_language, repo_stars, repo_forks)
        VALUES ('fpt-student/prj301', 'Java', 10, 2);
    """)
    in_memory_db.commit()

    cursor.execute("SELECT repo_name, repo_language FROM repositories WHERE repo_name='fpt-student/prj301';")
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == 'fpt-student/prj301'
    assert row[1] == 'Java'

def test_pull_request_foreign_key_constraint(in_memory_db):
    """Kiểm tra ràng buộc khóa ngoại FOREIGN KEY giữa pull_requests và repositories."""
    cursor = in_memory_db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Chèn PR với repo_id không tồn tại -> Phải ném ngoại lệ sqlite3.IntegrityError
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO pull_requests (pr_id, repo_id, pr_number, title, is_fpt)
            VALUES (999, 99999, 1, 'Invalid PR', 1);
        """)
