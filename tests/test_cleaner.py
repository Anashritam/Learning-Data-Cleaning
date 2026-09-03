import pytest
import pandas as pd
from data_cleaner.cleaner import clean_data

def test_trim_whitespace_and_normalize_email():
    df = pd.DataFrame({
        "name": [" Alice ", " Bob"],
        "email": ["ALICE@TEST.COM", "bob@test.com "]
    })
    cleaned, logs = clean_data(df)
    
    assert cleaned.loc[0, "name"] == "Alice"
    assert cleaned.loc[1, "name"] == "Bob"
    assert cleaned.loc[0, "email"] == "alice@test.com"
    assert cleaned.loc[1, "email"] == "bob@test.com"
    assert any("Trimmed" in log for log in logs)
    assert any("Normalized" in log for log in logs)

def test_numeric_coercion_and_imputation():
    df = pd.DataFrame({
        "age": ["25", "twenty", "35"],
        "salary": ["50000", "60000", "high"]
    })
    cleaned, logs = clean_data(df)
    
    # Check imputation values (will be float64 due to NaN presence)
    assert cleaned.loc[1, "age"] == 30.0
    assert cleaned.loc[2, "salary"] == 55000.0
    
    # Check provenance shadow columns (Option A)
    # Using 'not' is safer than '== False' for pandas/numpy booleans
    assert not cleaned.loc[0, "age_was_imputed"]
    assert cleaned.loc[1, "age_was_imputed"]
    assert cleaned.loc[2, "salary_was_imputed"]
    
    assert any("Coerced" in log for log in logs)
    assert any("Imputed" in log for log in logs)

def test_duplicate_removal_happens_after_cleaning():
    df = pd.DataFrame({
        "name": [" Alice ", "Alice", "Bob"],
        "email": ["ALICE@TEST.COM", "alice@test.com", "bob@test.com"]
    })
    cleaned, logs = clean_data(df)
    
    # " Alice " and "Alice" become identical after Step 1 & 2.
    assert len(cleaned) == 2
    assert any("duplicate" in log.lower() for log in logs)

def test_empty_string_handling():
    df = pd.DataFrame({
        "name": ["  ", "Bob"]
    })
    cleaned, logs = clean_data(df)
    
    # The first row's name should be stripped to "", then replaced with pd.NA
    assert pd.isna(cleaned.loc[0, "name"])
    assert cleaned.loc[1, "name"] == "Bob"