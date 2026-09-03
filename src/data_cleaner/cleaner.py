import pandas as pd

def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    logs = []
    df_clean = df.copy()
    initial_row_count = len(df_clean)

    #-------------------------------
    # 1. Trim Whitespace & Handle Empty Strings
    #-------------------------------
    def clean_string(x):
        if isinstance(x, str):
            stripped = x.strip()
            # If it becomes empty after stripping, convert to pd.NA immediately
            return pd.NA if stripped == "" else stripped
        return x

    for col in df_clean.columns:
        df_clean[col] = df_clean[col].apply(clean_string)
        
    logs.append("Trimmed leading/trailing whitespace and converted empty strings to missing values.")

    #-------------------------------
    # 2. Normalize Emails
    #-------------------------------
    if 'email' in df_clean.columns:
        df_clean['email'] = df_clean['email'].str.lower()
        logs.append("Normalized 'email' column to lowercase.")

    #----------------------------------------------------
    # 3. Convert Numeric Columns & Handle Invalid Values
    #----------------------------------------------------
    numeric_cols = ['age', 'salary']
    cols_to_process = [col for col in numeric_cols if col in df_clean.columns]

    for col in cols_to_process:
        missing_before = df_clean[col].isna().sum()
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        missing_after = df_clean[col].isna().sum()
        newly_invalid = missing_after - missing_before
        
        if newly_invalid > 0:
            logs.append(f"Coerced {newly_invalid} invalid value(s) in '{col}' to missing.")

    #------------------------------------------------------
    # 4. Impute Missing Numeric Values (POLICY DECISION)
    #------------------------------------------------------
    for col in cols_to_process:
        missing_mask = df_clean[col].isna()
        missing_count = missing_mask.sum()

        imputed_col_name = f"{col}_was_imputed"
        df_clean[imputed_col_name] = missing_mask

        if missing_count > 0:
            col_mean = df_clean[col].mean()

            if pd.isna(col_mean):
                col_mean = 0.0

            df_clean[col] = df_clean[col].fillna(col_mean)
            logs.append(f"Imputed {missing_count} missing value(s) in '{col}' with mean: {col_mean:.2f}. Flagged in '{imputed_col_name}'.")
        else:
            logs.append(f"No missing values in '{col}' to impute. '{imputed_col_name}' is all False.")

    #------------------------------------
    # 5. Remove Exact Duplicates
    #------------------------------------
    df_clean = df_clean.drop_duplicates().reset_index(drop=True)
    duplicates_removed = initial_row_count - len(df_clean)
    
    if duplicates_removed > 0:
        logs.append(f"Removed {duplicates_removed} exact duplicate row(s) post-normalization.")
    else:
        logs.append("No duplicate rows found post-normalization.")

    #--------------------------------------------
    # 6. Validation Handoff Note
    #--------------------------------------------
    logs.append("Cleaning complete.")

    return df_clean, logs