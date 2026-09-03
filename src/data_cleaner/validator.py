import pandas as pd
import re
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    valid_df: pd.DataFrame
    invalid_df: pd.DataFrame
    logs: list[str]

def validate_data(df: pd.DataFrame) -> ValidationResult:
    """
    Validate the cleaned DataFrame against business rules.

    Rules Enforced:
    1. 'name' and 'email' are strictly required(cannot be null/empty).
    2. 'email' must match a basic format(contains '@' and '.').
    3. 'age' must be a valid number between 18 and 100.
    4. 'salary' must be a valid number strictly greater than 0.

    Design Choice: Evaluates ALL rows for ALL rules. Error are accumulated per row in an '_validation_errors' column, allowing comprehensive reporting.

    Args: df: The DataFrame output rom cleaner.py.

    Returns: ValidationResult contianing valid/invalid DataFrames and summary logs.
    """

    logs=[]
    logs.append("Starting data validation...")

    df_val = df.copy()

    df_val['_validation_errors']=""

    total_rows = len(df_val)

    #========================================
    #Rule 1: Required 'name'
    #========================================

    name_missing = df_val['name'].isna()| (df_val['name'].str.strip()=='')
    df_val.loc[name_missing,'_validation_errors']+="missing required field 'name';"

    #==========================================
    # Rule 2: Required 'email' and Basic Format
    #==========================================

    email_missing = df_val['email'].isna()|(df_val['email'].str.strip()=='')
    df_val.loc[email_missing,'_validation_errors']+="missing required field 'name';"

    #Basic Regex:
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    email_present_but_invalid = ~ email_missing & ~df_val['email'].str.match(email_regex, na=False)
    df_val.loc[email_present_but_invalid, '_validation_errors']+="invalid email format;"

    #=============================================
    # Rule 3: 'age' bounds (18 to 100)
    #=============================================

    if 'age' in df_val.columns:
        age_missing=df_val['age'].isna()
        df_val.loc[age_missing,'_validation_errors']+="missing 'age' value;"

        age_out_of_bounds = (df_val['age']<18)|(df_val['age']>100)
        df_val.loc[age_out_of_bounds,'_validattion_errors'] +="age out of reasonable bounds(18-100);"

        if 'age_was_imputed' in df_val.columns:
            imputed_count = df_val['age_was_imputed'].sum()
            if imputed_count>0:
                logs.append(f"WARNING: {imputed_count} row(s) have imputed 'age' values(original data was invalid/missing).")

    #=================================================
    # Rule 4: 'salary' bounds(>0)
    #=================================================

    if 'salary' in df_val.columns:
        salary_missing = df_val['salary'].isna()
        df_val.loc[salary_missing, '_validation_errors']+="missing 'salary' value;"

        salary_invalid = df_val['salary']<=0
        df_val.loc[salary_invalid,'_validation_errors']+="salary must be greater than 0;"

        if 'salary_was_imputed' in df_val.columns:
            imputed_count = df_val['salary_was_imputed'].sum()
            if imputed_count > 0:
                logs.append(f"WARNING: {imputed_count} row(s) have imputed 'salary'values(original data was invalid/missing).")

    #============================================
    # Split Data and Finalize logs
    #============================================
    is_valid_row = df_val['_validation_errors'].str.strip()==""

    valid_df = df_val[is_valid_row].drop(columns=['_validation_errors']).reset_index(drop=True)
    invalid_df = df_val[~is_valid_row].reset_index(drop=True)

    if not invalid_df.empty:
        invalid_df['_validation_errors']=invalid_df['_validation_errors'].str.strip().str.rstrip(';')

    invalid_count = len(invalid_df)
    valid_count = len(valid_df)

    logs.append(f"Validation complete: {valid_count} valid rows, {invalid_count} iinvalid rows.")

    return ValidationResult(
        is_valid=(invalid_count==0),
        valid_df=valid_df,
        invalid_df=invalid_df,
        logs=logs
    )


        