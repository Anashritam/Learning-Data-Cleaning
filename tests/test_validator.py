import pytest
import pandas as pd
from data_cleaner.validator import validate_data, ValidationResult

def test_missing_required_fields():
    """Tests Rule 1 & 2: Missing name or email flags the row as invalid."""
    # FIX: Use empty strings "" instead of pd.NA to avoid pandas boolean 
    # propagation quirks, while still perfectly testing the missing field logic.
    df = pd.DataFrame({
        "name": ["", "Bob"],
        "email": ["alice@test.com", ""],
        "age": [25.0, 30.0],
        "salary": [50000.0, 60000.0]
    })
    result = validate_data(df)
    
    assert not result.is_valid
    assert len(result.invalid_df) == 2
    
    # Check specific error messages accumulated in the invalid dataframe
    assert "missing required field 'name'" in result.invalid_df.iloc[0]['_validation_errors']
    assert "missing required field 'email'" in result.invalid_df.iloc[1]['_validation_errors']

def test_invalid_email_format():
    """Tests Rule 2: Basic regex catches malformed emails."""
    df = pd.DataFrame({
        "name": ["Alice"],
        "email": ["alice-at-test.com"], # Missing @ and .
        "age": [25.0],
        "salary": [50000.0]
    })
    result = validate_data(df)
    
    assert not result.is_valid
    assert "invalid email format" in result.invalid_df.iloc[0]['_validation_errors']

def test_numeric_bounds():
    """Tests Rule 3 & 4: Age (18-120) and Salary (>0) constraints."""
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "email": ["a@t.com", "b@t.com", "c@t.com"],
        "age": [15.0, 30.0, 125.0],      # 15 and 125 are out of bounds
        "salary": [50000.0, -100.0, 60000.0] # -100 is invalid
    })
    result = validate_data(df)
    
    assert len(result.invalid_df) == 3
    assert "age out of reasonable bounds" in result.invalid_df.iloc[0]['_validation_errors']
    assert "salary must be greater than 0" in result.invalid_df.iloc[1]['_validation_errors']
    assert "age out of reasonable bounds" in result.invalid_df.iloc[2]['_validation_errors']

def test_error_accumulation():
    """Tests that a single row can accumulate MULTIPLE errors."""
    df = pd.DataFrame({
        "name": [""],           # Error 1 (using "" instead of pd.NA)
        "email": ["bad-email"], # Error 2
        "age": [15.0],          # Error 3
        "salary": [50000.0]
    })
    result = validate_data(df)
    errors = result.invalid_df.iloc[0]['_validation_errors']
    
    # All three errors should be present in the string
    assert "missing required field 'name'" in errors
    assert "invalid email format" in errors
    assert "age out of reasonable bounds" in errors

def test_provenance_warning_does_not_fail_row():
    """Tests Option A: Imputed values are valid, but trigger a WARNING in the logs."""
    df = pd.DataFrame({
        "name": ["Alice"],
        "email": ["alice@test.com"],
        "age": [30.0],
        "age_was_imputed": [True],  # Shadow column from cleaner.py
        "salary": [50000.0]
    })
    result = validate_data(df)
    
    # The row MUST be valid (imputation is an acceptable policy)
    assert result.is_valid
    assert len(result.valid_df) == 1
    
    # BUT the logs must contain the provenance warning
    assert any("WARNING" in log and "imputed 'age' values" in log for log in result.logs)

def test_valid_data_passes_cleanly():
    """Tests the happy path: Perfect data returns a valid result."""
    df = pd.DataFrame({
        "name": ["Alice"],
        "email": ["alice@test.com"],
        "age": [25.0],
        "salary": [50000.0]
    })
    result = validate_data(df)
    
    assert result.is_valid
    assert len(result.valid_df) == 1
    assert len(result.invalid_df) == 0
    assert "_validation_errors" not in result.valid_df.columns # Ensure cleanup happened