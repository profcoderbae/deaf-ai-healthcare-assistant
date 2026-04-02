"""
Data Validation & QA/QC Module
==============================
Implements comprehensive data quality checks for breeding trial data:
- Range validation
- Missing data analysis
- Outlier detection (IQR method)
- Cross-field consistency checks
- Evaluator bias detection
"""

import numpy as np
import pandas as pd
import yaml
from typing import Optional


class BreedingDataValidator:
    """Validates breeding trial phenotypic data against configurable rules."""
    
    def __init__(self, config_path: str = "config/pipeline_config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.validation_config = self.config.get("validation", {})
        self.issues = []
    
    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run all validation checks and return a flagged DataFrame.
        
        Adds columns:
        - _qc_flags: list of QC flag codes per record
        - _qc_status: PASS / WARNING / FAIL
        """
        df = df.copy()
        df["_qc_flags"] = [[] for _ in range(len(df))]
        
        self._check_missing_data(df)
        self._check_range_violations(df)
        self._check_outliers(df)
        self._check_date_consistency(df)
        self._check_evaluator_bias(df)
        self._check_site_season_completeness(df)
        
        # Assign overall QC status
        df["_qc_status"] = df["_qc_flags"].apply(self._compute_status)
        
        return df
    
    def _check_missing_data(self, df: pd.DataFrame):
        """Flag records and summarize missing data by trait and site."""
        threshold = self.validation_config.get("missing_threshold", 0.15)
        trait_cols = self._get_trait_columns(df)
        
        for trait in trait_cols:
            missing_rate = df[trait].isna().mean()
            if missing_rate > threshold:
                self.issues.append({
                    "check": "missing_data",
                    "severity": "WARNING",
                    "trait": trait,
                    "detail": f"Missing rate {missing_rate:.1%} exceeds threshold {threshold:.0%}",
                })
            
            # By site
            for site in df["site"].unique():
                site_mask = df["site"] == site
                site_missing = df.loc[site_mask, trait].isna().mean()
                if site_missing > threshold * 1.5:
                    self.issues.append({
                        "check": "missing_data_by_site",
                        "severity": "CRITICAL",
                        "trait": trait,
                        "site": site,
                        "detail": f"Site {site}: {trait} missing rate {site_missing:.1%}",
                    })
    
    def _check_range_violations(self, df: pd.DataFrame):
        """Check trait values against biologically plausible ranges."""
        range_checks = self.validation_config.get("range_checks", {})
        
        for trait, (low, high) in range_checks.items():
            if trait not in df.columns:
                continue
            
            mask = df[trait].notna()
            below = mask & (df[trait] < low)
            above = mask & (df[trait] > high)
            
            for idx in df[below | above].index:
                df.at[idx, "_qc_flags"].append(f"RANGE_{trait}")
            
            n_violations = below.sum() + above.sum()
            if n_violations > 0:
                self.issues.append({
                    "check": "range_violation",
                    "severity": "CRITICAL",
                    "trait": trait,
                    "detail": f"{n_violations} values outside [{low}, {high}]",
                })
    
    def _check_outliers(self, df: pd.DataFrame):
        """Detect outliers using IQR method within each site-season group."""
        multiplier = self.validation_config.get("outlier_multiplier", 2.5)
        trait_cols = self._get_trait_columns(df)
        
        for trait in trait_cols:
            if trait not in df.columns:
                continue
            
            for (site, season), group in df.groupby(["site", "season"]):
                values = group[trait].dropna()
                if len(values) < 10:
                    continue
                
                q1, q3 = values.quantile(0.25), values.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - multiplier * iqr
                upper = q3 + multiplier * iqr
                
                outlier_mask = group[trait].notna() & (
                    (group[trait] < lower) | (group[trait] > upper)
                )
                
                for idx in group[outlier_mask].index:
                    df.at[idx, "_qc_flags"].append(f"OUTLIER_{trait}")
                
                n_outliers = outlier_mask.sum()
                if n_outliers > 0:
                    self.issues.append({
                        "check": "outlier",
                        "severity": "WARNING",
                        "trait": trait,
                        "site": site,
                        "season": season,
                        "detail": f"{n_outliers} outliers detected (IQR x{multiplier})",
                    })
    
    def _check_date_consistency(self, df: pd.DataFrame):
        """Ensure evaluation dates fall within expected season windows."""
        if "evaluation_date" not in df.columns:
            return
        
        for season in df["season"].unique():
            season_mask = df["season"] == season
            dates = pd.to_datetime(df.loc[season_mask, "evaluation_date"], errors="coerce")
            
            year = int(season.split("-")[1])
            expected_start = pd.Timestamp(f"{year}-01-01")
            expected_end = pd.Timestamp(f"{year}-12-31")
            
            out_of_range = dates.notna() & ((dates < expected_start) | (dates > expected_end))
            n_bad = out_of_range.sum()
            
            if n_bad > 0:
                self.issues.append({
                    "check": "date_consistency",
                    "severity": "WARNING",
                    "detail": f"Season {season}: {n_bad} dates outside expected range",
                })
    
    def _check_evaluator_bias(self, df: pd.DataFrame):
        """Detect potential evaluator bias in subjective scoring traits."""
        score_traits = [c for c in df.columns if "score" in c]
        
        if "evaluator" not in df.columns or not score_traits:
            return
        
        for trait in score_traits:
            evaluator_means = df.groupby("evaluator")[trait].mean()
            overall_mean = df[trait].mean()
            overall_std = df[trait].std()
            
            if overall_std == 0:
                continue
            
            for evaluator, mean in evaluator_means.items():
                z_score = abs(mean - overall_mean) / overall_std
                if z_score > 1.5:
                    self.issues.append({
                        "check": "evaluator_bias",
                        "severity": "WARNING",
                        "trait": trait,
                        "evaluator": evaluator,
                        "detail": f"Evaluator {evaluator} mean={mean:.2f} vs overall={overall_mean:.2f} (z={z_score:.2f})",
                    })
    
    def _check_site_season_completeness(self, df: pd.DataFrame):
        """Check for sufficient replication across site-season combinations."""
        completeness = df.groupby(["crop", "site", "season"])["genotype_id"].nunique()
        
        for (crop, site, season), n_genotypes in completeness.items():
            if n_genotypes < 10:
                self.issues.append({
                    "check": "completeness",
                    "severity": "CRITICAL",
                    "detail": f"{crop} at {site} in {season}: only {n_genotypes} genotypes evaluated",
                })
    
    def _compute_status(self, flags: list) -> str:
        """Determine overall QC status from flag list."""
        if not flags:
            return "PASS"
        if any("RANGE" in f for f in flags):
            return "FAIL"
        return "WARNING"
    
    def _get_trait_columns(self, df: pd.DataFrame) -> list:
        """Identify numeric trait columns (exclude metadata)."""
        meta_cols = {
            "genotype_id", "crop", "site", "season", "rep", "block",
            "row", "tree_position", "evaluation_date", "evaluator",
            "source_file", "ingestion_timestamp", "_qc_flags", "_qc_status",
        }
        return [c for c in df.select_dtypes(include=[np.number]).columns 
                if c not in meta_cols]
    
    def get_issues_dataframe(self) -> pd.DataFrame:
        """Return all validation issues as a DataFrame."""
        if not self.issues:
            return pd.DataFrame(columns=["check", "severity", "detail"])
        return pd.DataFrame(self.issues)
    
    def summary(self) -> str:
        """Print a summary of validation results."""
        issues_df = self.get_issues_dataframe()
        if issues_df.empty:
            return "All validation checks passed."
        
        lines = ["\n=== QA/QC VALIDATION SUMMARY ==="]
        for severity in ["CRITICAL", "WARNING", "INFO"]:
            subset = issues_df[issues_df["severity"] == severity]
            if not subset.empty:
                lines.append(f"\n{severity} ({len(subset)} issues):")
                for _, row in subset.iterrows():
                    lines.append(f"  [{row['check']}] {row['detail']}")
        
        return "\n".join(lines)
