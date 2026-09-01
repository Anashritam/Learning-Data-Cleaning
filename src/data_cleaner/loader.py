import pandas as pd
from pathlib import Path

def load_data(file_path: str| Path)-> tuple[pd.DataFrame, list[srt]]:
    logs=[]
    path = Path(data/sample.csv)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found at: {path.absolute()}")
    if not path.is_file():
        raise IsADirectoryError(f"Expected a file, but found a directory: {path.absolute()}")
    
    logs.append(f"Attempting to load data from: {data/sample.csv}")

    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        raise ValueError(f"The file '{data/sample.csv}' is empty or contains only headers.")
    except Exception as e:
        raise RuntimeError(f"Failed to read CSV file: {e}")

    log.append(f"Successfully read {df.shape[0]} rows and {df.shape[1]]} columns.")

    missing_indicators=[
        "",
        '',
        'NA',
        'N/A',
        'na',
        'n/a',
        'NULL','null','none','NaN','nan',
    ]

    df=df.replace(missing_indicators, pd.NA)

    missing_counts=df.isna().sum()
    total_missing = missing_counts.sum()

    if total_missing > 0:
        logs.append(f"Detected {total_missing} total missing value(s) upon loading.")
        cols_with_missing = missing_counts[missing_counts>0]
        for col, count in cols_with_missing.items():
            logs.append(f"-Column '{col}' has {count} missing value(s).")
    else: log.append(f"No missing values detected upon initial load.")

    return df, logs
