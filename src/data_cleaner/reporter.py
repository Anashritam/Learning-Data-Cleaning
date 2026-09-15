import pandas as pd
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from data_cleaner.validator import ValidationResult

@dataclass
class PipelineMatrics:
    """
    Lightweight dataclass to hold aggregate metrics collected during the pipeline run.
    This prevent us from having to pass having to pass heavy raw/clean DataFrame to the reporter.
    """

    input_rows: int
    output_rows: int
    duplicates_removed: int
    valid_rows: int
    invalid_rows: int 
    missing_values_initial: int
    invalid_numerics_coerced: int
    values_imputed: int

def generate_report(
        metrics: PipelineMatrics,
        validation_result: ValidationResult,
        report_path: str | Path
)-> None:
    # Calculates final statistics and writes a comprehensive summery report to disk.
    path = Path(report_path)
    path.parent.mkdir(parents = True, exist_ok = True)

    valid_df = validation_result.valid_df

    def get_numeric_stats(col: str)-> dict:
        if col in valid_df.columns and not valid_df[col].empty:
            series= valid_df[col].dropna()
            if not series.empty:
                return {
                    "count": int(series.count()),
                    "mean": round(float(series.mean()),2),
                    "min": float(series.min()),
                    "max": float(series.max())
                }
        return {
            "count": 0,
            "mean": 0.0,
            "min": 0.0,
            "max": 0.0
        }
    age_stats = get_numeric_stats("age")
    salary_stats = get_numeric_stats("salary")

    report_lines = [
        "="*60,
        "DATA PIPELINE EXECUTION REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "="*60,
        "",
        "📊 DATASET SIZE & REDUCTION",
        f" Input Rows:  {metrics.input_rows}",
        f" Output Rows: {metrics.output_rows}",
        f" Duplicates Removed: {metrics.duplicates_removed}",
        f" Valid Rows: {metrics.valid_rows}",
        f" Invalid Rows: {metrics.invalid_rows} (Rejected)",
        ""
        "DATA QUALITY ACTIONS",
        f" Initial Missing Values Detected: {metrics.missing_values_initial}",
        f" Invalid numerics Coerced to NaN: {metrics.invalid_numerics_coerced}",
        f" Missing Values Imputed (Mean):{metrics.values_imputed}",
        "",
        "NUMERIC STATISTICS (Valid Data Only)",
        "   Age:",
        f"  -Count: {age_stats['count']}",
        f"  -Mean: {age_stats['mean']}",
        f"  -Min: {age_stats['min']}",
        f"  -Max: {age_stats['max']}",
        "   Salary:"
        f"  -Count: {salary_stats['count']}"
        f"  -Mean: {salary_stats['mean']}",
        f"  -Min: {salary_stats['min']}",
        f"  -Max: {salary_stats['max']}",
        "",
        "-"*60,
        "EXECUTION LOGS:",
    ]

    for log in validation_result.logs:
        report_lines.append(f" •{log}")

    report_lines.append("="*60)
    report_lines.append("Note: Rejected rows have been saved to 'rejected_data.csv' for manual review.")
    report_lines.append("="*60)

    with open(path, 'w', encoding= 'utf-8') as f:
        f.write("\n".join(report_lines))