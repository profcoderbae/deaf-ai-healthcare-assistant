"""
Data Transformation Module
==========================
Cleans and transforms validated breeding trial data for analysis:
- Outlier capping/removal
- Missing value imputation strategies
- Trait normalization and derived trait calculation
- Aggregation to genotype-level means (BLUEs approximation)
"""

import numpy as np
import pandas as pd
from typing import Optional


def cap_outliers(df: pd.DataFrame, trait_cols: list, method: str = "iqr", 
                 multiplier: float = 2.5) -> pd.DataFrame:
    """
    Cap extreme outliers to boundary values within each site-season group.
    
    Uses IQR method: values beyond Q1 - k*IQR or Q3 + k*IQR are capped.
    """
    df = df.copy()
    capped_count = 0
    
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
            
            mask = group.index
            below = df.loc[mask, trait] < lower
            above = df.loc[mask, trait] > upper
            
            df.loc[mask[below], trait] = lower
            df.loc[mask[above], trait] = upper
            capped_count += below.sum() + above.sum()
    
    print(f"  Capped {capped_count} outlier values")
    return df


def remove_failed_qc(df: pd.DataFrame) -> pd.DataFrame:
    """Remove records that failed QC (range violations)."""
    if "_qc_status" in df.columns:
        n_before = len(df)
        df = df[df["_qc_status"] != "FAIL"].copy()
        print(f"  Removed {n_before - len(df)} failed QC records")
    return df


def compute_derived_traits(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate derived traits commonly used in breeding evaluations.
    """
    df = df.copy()
    
    # Mango: fruit shape index (length / width ratio)
    if "fruit_length_mm" in df.columns and "fruit_width_mm" in df.columns:
        mask = df["fruit_length_mm"].notna() & df["fruit_width_mm"].notna()
        df.loc[mask, "fruit_shape_index"] = (
            df.loc[mask, "fruit_length_mm"] / df.loc[mask, "fruit_width_mm"]
        )
    
    # Citrus: Brix/Acid ratio (maturity/flavor index)
    if "brix_content" in df.columns and "acidity_percent" in df.columns:
        mask = df["brix_content"].notna() & df["acidity_percent"].notna()
        valid_acid = mask & (df["acidity_percent"] > 0)
        df.loc[valid_acid, "brix_acid_ratio"] = (
            df.loc[valid_acid, "brix_content"] / df.loc[valid_acid, "acidity_percent"]
        )
    
    # Yield efficiency (yield / tree vigor)
    if "yield_kg_per_tree" in df.columns and "tree_vigor_score" in df.columns:
        mask = (df["yield_kg_per_tree"].notna() & 
                df["tree_vigor_score"].notna() & 
                (df["tree_vigor_score"] > 0))
        df.loc[mask, "yield_efficiency"] = (
            df.loc[mask, "yield_kg_per_tree"] / df.loc[mask, "tree_vigor_score"]
        )
    
    return df


def aggregate_to_genotype_means(df: pd.DataFrame, trait_cols: list) -> pd.DataFrame:
    """
    Compute genotype-level least-squares means across reps.
    
    This is a simplified approach (arithmetic means across reps).
    For production use, mixed models (BLUP/BLUE) would be preferred
    to account for unbalanced designs.
    
    Returns
    -------
    pd.DataFrame
        Genotype-level means with columns: genotype_id, crop, site, season,
        n_reps, and trait means/stds.
    """
    meta_cols = ["genotype_id", "crop", "site", "season"]
    available_traits = [c for c in trait_cols if c in df.columns]
    
    agg_dict = {trait: ["mean", "std", "count"] for trait in available_traits}
    
    grouped = df.groupby(meta_cols).agg(agg_dict)
    grouped.columns = [f"{trait}_{stat}" for trait, stat in grouped.columns]
    grouped = grouped.reset_index()
    
    # Add n_reps (use first available trait's count)
    count_cols = [c for c in grouped.columns if c.endswith("_count")]
    if count_cols:
        grouped["n_reps"] = grouped[count_cols[0]].astype(int)
    
    return grouped


def aggregate_across_environments(df: pd.DataFrame, trait_cols: list) -> pd.DataFrame:
    """
    Compute genotype means across all site-season environments.
    Useful for identifying broadly adapted genotypes.
    """
    available_traits = [c for c in trait_cols if c in df.columns]
    
    agg_dict = {"site": "nunique", "season": "nunique"}
    for trait in available_traits:
        agg_dict[trait] = "mean"
    
    grouped = df.groupby(["genotype_id", "crop"]).agg(agg_dict).reset_index()
    grouped = grouped.rename(columns={"site": "n_sites", "season": "n_seasons"})
    
    return grouped


def normalize_traits(df: pd.DataFrame, trait_cols: list, 
                     method: str = "zscore") -> pd.DataFrame:
    """
    Normalize trait values for multi-trait selection indices.
    
    Parameters
    ----------
    method : str
        'zscore' for standardization, 'minmax' for 0-1 scaling
    """
    df = df.copy()
    
    for trait in trait_cols:
        if trait not in df.columns:
            continue
        values = df[trait]
        
        if method == "zscore":
            mean, std = values.mean(), values.std()
            if std > 0:
                df[f"{trait}_normalized"] = (values - mean) / std
        elif method == "minmax":
            vmin, vmax = values.min(), values.max()
            if vmax > vmin:
                df[f"{trait}_normalized"] = (values - vmin) / (vmax - vmin)
    
    return df
