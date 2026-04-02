#!/usr/bin/env python3
"""
Breeding Data Pipeline - Main Entry Point
==========================================
End-to-end ETL pipeline for subtropical fruit breeding trial data.

Pipeline stages:
1. Generate synthetic trial data (for demo) or ingest from files
2. Standardize and deduplicate
3. Validate and flag QA/QC issues
4. Transform (cap outliers, compute derived traits)
5. Store in SQLite database
6. Generate QA/QC reports with visualizations

Usage:
    python run_pipeline.py [--generate-data] [--skip-reports]
"""

import argparse
import os
import sys
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_generator import save_raw_data
from src.ingestion import ingest_trial_files, standardize_columns, deduplicate_records
from src.validation import BreedingDataValidator
from src.transformation import (
    cap_outliers, remove_failed_qc, compute_derived_traits,
    aggregate_to_genotype_means, normalize_traits
)
from src.database import BreedingDatabase
from src.reports import QAQCReporter


def get_trait_columns(df):
    """Get numeric trait columns from DataFrame."""
    meta_cols = {
        "genotype_id", "crop", "site", "season", "rep", "block",
        "row", "tree_position", "evaluation_date", "evaluator",
        "source_file", "ingestion_timestamp", "_qc_flags", "_qc_status",
    }
    return [c for c in df.select_dtypes(include=[np.number]).columns 
            if c not in meta_cols]


def main():
    parser = argparse.ArgumentParser(description="Breeding Data Pipeline")
    parser.add_argument("--generate-data", action="store_true",
                       help="Generate synthetic trial data first")
    parser.add_argument("--skip-reports", action="store_true",
                       help="Skip QA/QC report generation")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  SUBTROPICAL BREEDING DATA PIPELINE")
    print("  Mango & Citrus Trial Data Management")
    print("=" * 60)
    
    # Stage 1: Data Generation / Ingestion
    print("\n[1/6] DATA INGESTION")
    print("-" * 40)
    
    if args.generate_data or not os.path.exists("data/raw"):
        print("Generating synthetic trial data...")
        save_raw_data()
    
    df = ingest_trial_files("data/raw")
    
    # Stage 2: Standardization
    print("\n[2/6] STANDARDIZATION")
    print("-" * 40)
    df = standardize_columns(df)
    df, duplicates = deduplicate_records(df)
    print(f"  Dataset shape after standardization: {df.shape}")
    
    # Stage 3: Validation
    print("\n[3/6] QA/QC VALIDATION")
    print("-" * 40)
    validator = BreedingDataValidator()
    df = validator.validate(df)
    print(validator.summary())
    
    issues_df = validator.get_issues_dataframe()
    
    # Stage 4: Transformation
    print("\n[4/6] DATA TRANSFORMATION")
    print("-" * 40)
    trait_cols = get_trait_columns(df)
    
    df = remove_failed_qc(df)
    df = cap_outliers(df, trait_cols)
    df = compute_derived_traits(df)
    
    # Update trait columns after adding derived traits
    trait_cols = get_trait_columns(df)
    print(f"  Traits available: {len(trait_cols)}")
    print(f"  Final dataset shape: {df.shape}")
    
    # Stage 5: Database Storage
    print("\n[5/6] DATABASE STORAGE")
    print("-" * 40)
    with BreedingDatabase() as db:
        db.create_schema()
        
        for crop in df["crop"].unique():
            crop_df = df[df["crop"] == crop]
            crop_traits = [c for c in trait_cols if c in crop_df.columns and crop_df[c].notna().any()]
            print(f"\n  Loading {crop} data ({len(crop_df)} records, {len(crop_traits)} traits)...")
            db.insert_trial_data(crop_df, crop_traits)
        
        db.insert_qc_log(issues_df)
        
        print("\n  Trial Database Summary:")
        summary = db.get_trial_summary()
        print(summary.to_string(index=False))
    
    # Stage 6: Reporting
    if not args.skip_reports:
        print("\n[6/6] QA/QC REPORTING")
        print("-" * 40)
        reporter = QAQCReporter()
        
        for crop in df["crop"].unique():
            reporter.generate_full_report(df, issues_df, crop)
        
        reporter.generate_full_report(df, issues_df, "all")
    
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\n  Records processed: {len(df):,}")
    print(f"  QC issues found:   {len(issues_df)}")
    print(f"  Database:           data/breeding_trials.db")
    if not args.skip_reports:
        print(f"  Reports:            reports/")


if __name__ == "__main__":
    main()
