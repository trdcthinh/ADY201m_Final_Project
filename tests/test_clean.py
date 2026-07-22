import pytest
import pandas as pd
import numpy as np

def test_duration_calculation(mock_raw_df):
    """Kiểm tra việc chuyển đổi datetime và tính toán duration_minutes."""
    df = mock_raw_df.copy()
    
    for col in ['created_at', 'closed_at', 'merged_at']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        
    end_time = df['closed_at'].combine_first(df['merged_at'])
    df['calculated_duration'] = (end_time - df['created_at']).dt.total_seconds() / 60.0
    
    # PR 101: created 10:00, closed 10:30 -> 30 minutes
    assert df.loc[df['pr_id'] == 101, 'calculated_duration'].values[0] == 30.0
    # PR 102: created 12:00, closed 13:00 -> 60 minutes
    assert df.loc[df['pr_id'] == 102, 'calculated_duration'].values[0] == 60.0

def test_target_variable_creation(mock_raw_df):
    """Kiểm tra tạo nhãn is_merged (1 nếu merged_at có giá trị, 0 nếu không)."""
    df = mock_raw_df.copy()
    df['merged_at'] = pd.to_datetime(df['merged_at'], errors='coerce')
    df['is_merged'] = df['merged_at'].notna().astype(int)
    
    assert df.loc[df['pr_id'] == 101, 'is_merged'].values[0] == 1
    assert df.loc[df['pr_id'] == 102, 'is_merged'].values[0] == 0
    assert df.loc[df['pr_id'] == 103, 'is_merged'].values[0] == 0

def test_missing_values_imputation(mock_raw_df):
    """Kiểm tra xử lý các ô rỗng NaN trên các đặc trưng."""
    df = mock_raw_df.copy()
    df.loc[0, 'user_type'] = np.nan
    df.loc[0, 'repo_language'] = np.nan
    
    df['user_type'] = df['user_type'].fillna('User')
    df['repo_language'] = df['repo_language'].fillna('Unknown')
    
    assert df.loc[0, 'user_type'] == 'User'
    assert df.loc[0, 'repo_language'] == 'Unknown'
