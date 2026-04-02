"""
Data Ingestion Module
=====================
Handles ingestion of raw breeding trial CSV files from multiple
field sources, seasons, and sites into a unified DataFrame.
"""

import glob
import os
import pandas as pd
import yaml


def load_config(config_path: str = "config/pipeline_config.yaml") -> dict:
    """Load pipeline configuration."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def ingest_trial_files(data_dir: str = "data/raw", file_pattern: str = "*.csv") -> pd.DataFrame:
    """
    Ingest all raw trial CSV files from the specified directory.
    
    Parameters
    ----------
    data_dir : str
        Directory containing raw CSV files
    file_pattern : str
        Glob pattern for CSV files
        
    Returns
    -------
    pd.DataFrame
        Combined DataFrame from all source files with source tracking
    """
    search_path = os.path.join(data_dir, file_pattern)
    files = sorted(glob.glob(search_path))
    
    if not files:
        raise FileNotFoundError(f"No files found matching: {search_path}")
    
    frames = []
    for filepath in files:
        df = pd.read_csv(filepath)
        df["source_file"] = os.path.basename(filepath)
        df["ingestion_timestamp"] = pd.Timestamp.now().isoformat()
        frames.append(df)
        print(f"  Ingested: {os.path.basename(filepath)} ({len(df)} rows)")
    
    combined = pd.concat(frames, ignore_index=True)
    print(f"\nTotal records ingested: {len(combined)}")
    print(f"Crops: {combined['crop'].unique().tolist()}")
    print(f"Sites: {combined['site'].unique().tolist()}")
    print(f"Seasons: {combined['season'].unique().tolist()}")
    
    return combined


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names and data types for consistency.
    
    - Lowercase and strip whitespace from column names
    - Parse evaluation dates
    - Ensure genotype_id is string type
    """
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    if "evaluation_date" in df.columns:
        df["evaluation_date"] = pd.to_datetime(df["evaluation_date"], errors="coerce")
    
    if "genotype_id" in df.columns:
        df["genotype_id"] = df["genotype_id"].astype(str)
    
    return df


def deduplicate_records(df: pd.DataFrame) -> tuple:
    """
    Identify and remove duplicate records based on key fields.
    
    Returns
    -------
    tuple
        (deduplicated DataFrame, DataFrame of duplicates found)
    """
    key_cols = ["genotype_id", "crop", "site", "season", "rep", "evaluation_date"]
    available_keys = [c for c in key_cols if c in df.columns]
    
    duplicates = df[df.duplicated(subset=available_keys, keep=False)]
    deduped = df.drop_duplicates(subset=available_keys, keep="first")
    
    n_dupes = len(df) - len(deduped)
    if n_dupes > 0:
        print(f"  Removed {n_dupes} duplicate records")
    
    return deduped, duplicates


if __name__ == "__main__":
    print("Running data ingestion...")
    df = ingest_trial_files()
    df = standardize_columns(df)
    df, dupes = deduplicate_records(df)
    print(f"\nFinal dataset shape: {df.shape}")
