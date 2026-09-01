import pandas as pd
def clean_data(df: pd.DataFrame)-> tuple[pd.DataFrame, list[str]]:
    logs=[]

    df_clean=df.copy()
    initial_row_count = len(df_clean)

    #-------------------------------
    # 1. Trim WhiteSpace
    #-------------------------------

    for col in df_clean.columns:
        df_clean[col] = df_clean[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    logs.append("Trimmed leading/trailing whitespace from all string columns.")

    #-------------------------------
    # 2. Normalized Emails
    #-------------------------------

    if 'email' in df_clean.columns:
        df_clean['email']=df_clean['email'].str.lower()
        logs.append("Normalized 'email' column to lowercase.")

    #----------------------------------------------------
    # 3. Convert Numeric Columns & Handle Invalid Values
    #----------------------------------------------------

    numeric_cols=['age','salary']
    cols_to_process=[col for col in numeric_cols if col in df_clean.columns]

    for col in cols_to_process:
        missing_before=df_clean[col].isna().sum()

        df_clean[col]=pd.to_numeric(df_clean[col], errors='coerce')

        missing_after = df_clean[col].isna().sum()
        newly_invalid = missing_after - missing_before
        if newly_invalid > 0:
            logs.append(f"Coerced {newly_invalid} invalid value(s) in '{col}' to missing.")

    #------------------------------------------------------
    # 4. Impute Missing Numeric Values (PPLICY DECISION)
    #------------------------------------------------------

    for col in cols_to_process:
        missing_count =df_clean[col].isna().sum()
        if missing_count > 0:
            col_mean = df_clean[col].mean()

            if pd.isna(col_mean):
                col_mean=0.0

            df_clean[col]=df_clean[col].fillna(col_mean)
            logs.append(f"Imputed {missing_count} missing value(s) in {col} with column mean: {col_mean:.2f}.")

    #------------------------------------
    # 5. Remove Exact Duplicates
    #------------------------------------

    df_clean = df_clean.drop_duplicates().reset_index(drop = True)

    duplicates_removed = initial_row_count -len(df_clean)
    if duplicates_removed > 0:
        logs.append(f"Removed {duplicates_removed} exact duplicate row(s) post-normalization.")
    else:
        logs.append("No duplicate rows found post-normalization.")

    #--------------------------------------------
    # 6. Validation Handoff Note
    #--------------------------------------------

    logs.append("Cleaning complete. Required field validation (name/email) deferred to validatior.py.")

    return df_clean.logs
            