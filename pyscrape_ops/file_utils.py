# pyscrape_ops/file_utils.py
from pathlib import Path
import pandas as pd
from typing import List, Dict

def ensure_parent_dir(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)

def save_csv_from_df(df: pd.DataFrame, path: str):
    ensure_parent_dir(path)
    df.to_csv(path, index=False, encoding="utf-8-sig")

def save_json_from_df(df: pd.DataFrame, path: str):
    ensure_parent_dir(path)
    df.to_json(path, orient="records", force_ascii=False, indent=2)

def save_records(records: List[Dict], path: str, fmt: str = "csv"):
    df = pd.DataFrame(records)
    if fmt == "csv":
        save_csv_from_df(df, path)
    else:
        save_json_from_df(df, path)
