"""
Trial Analysis Module
=====================
Statistical analysis functions for breeding trial data.
Provides genotype ranking, selection indices, family performance,
and GxE interaction analysis for breeder decision support.
"""

import numpy as np
import pandas as pd
from scipy import stats


def compute_genotype_means(df: pd.DataFrame, trait_cols: list) -> pd.DataFrame:
    """
    Compute genotype-level means (across reps) per site-season.
    Approximation of BLUE (Best Linear Unbiased Estimator).
    """
    group_cols = ["genotype_id", "family", "stage", "site", "season"]
    available = [c for c in group_cols if c in df.columns]
    
    agg = {trait: ["mean", "std", "count"] for trait in trait_cols if trait in df.columns}
    result = df.groupby(available).agg(agg)
    result.columns = [f"{t}_{s}" for t, s in result.columns]
    return result.reset_index()


def compute_overall_means(df: pd.DataFrame, trait_cols: list) -> pd.DataFrame:
    """
    Compute genotype means across all environments.
    Used for broad adaptation ranking.
    """
    available_traits = [t for t in trait_cols if t in df.columns]
    
    agg = {"site": "nunique", "season": "nunique"}
    for t in available_traits:
        agg[t] = "mean"
    
    result = df.groupby(["genotype_id", "family", "stage"]).agg(agg).reset_index()
    result = result.rename(columns={"site": "n_sites", "season": "n_seasons"})
    return result


def compute_selection_index(df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """
    Multi-trait selection index for ranking genotypes.
    
    Parameters
    ----------
    df : pd.DataFrame
        Genotype-level means
    weights : dict
        {trait_name: weight} — positive for "more is better", negative for "less is better"
    """
    df = df.copy()
    
    index = np.zeros(len(df))
    for trait, weight in weights.items():
        if trait not in df.columns:
            continue
        values = df[trait].values
        valid = ~np.isnan(values)
        if not valid.any():
            continue
        
        # Standardize
        z = np.full_like(values, np.nan)
        z[valid] = (values[valid] - np.nanmean(values)) / max(np.nanstd(values), 1e-6)
        index += weight * np.nan_to_num(z, 0)
    
    df["selection_index"] = np.round(index, 4)
    return df.sort_values("selection_index", ascending=False)


def family_performance(df: pd.DataFrame, trait_cols: list) -> pd.DataFrame:
    """
    Summarize performance by cross/family.
    Helps breeders identify the best crosses for future breeding.
    """
    if "family" not in df.columns:
        return pd.DataFrame()
    
    available = [t for t in trait_cols if t in df.columns]
    
    agg = {"genotype_id": "nunique"}
    for t in available:
        agg[t] = ["mean", "std"]
    
    result = df.groupby("family").agg(agg)
    result.columns = ["_".join(c).strip("_") for c in result.columns]
    result = result.rename(columns={"genotype_id_nunique": "n_genotypes"})
    return result.reset_index().sort_values("n_genotypes", ascending=False)


def stage_advancement_summary(df: pd.DataFrame, trait_cols: list) -> pd.DataFrame:
    """
    Performance summary by advancement stage.
    Shows trait improvement through selection stages.
    """
    if "stage" not in df.columns:
        return pd.DataFrame()
    
    available = [t for t in trait_cols if t in df.columns]
    agg = {"genotype_id": "nunique"}
    for t in available:
        agg[t] = "mean"
    
    result = df.groupby("stage").agg(agg).reset_index()
    result = result.rename(columns={"genotype_id": "n_genotypes"})
    
    stage_order = ["Seedling", "Phase_1", "Phase_2", "Advanced", "Elite"]
    result["stage"] = pd.Categorical(result["stage"], categories=stage_order, ordered=True)
    return result.sort_values("stage")


def gxe_stability(df: pd.DataFrame, trait: str) -> pd.DataFrame:
    """
    Compute GxE stability metrics for genotypes across environments.
    
    Returns Finlay-Wilkinson regression coefficients:
    - b ≈ 1: average stability
    - b < 1: adapted to poor environments
    - b > 1: adapted to good environments
    - Low MSE: high stability
    """
    env_means = df.groupby(["site", "season"])[trait].mean()
    
    results = []
    for gid, group in df.groupby("genotype_id"):
        geno_env_means = group.groupby(["site", "season"])[trait].mean()
        
        common_envs = geno_env_means.index.intersection(env_means.index)
        if len(common_envs) < 3:
            continue
        
        x = env_means[common_envs].values
        y = geno_env_means[common_envs].values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        residuals = y - (slope * x + intercept)
        mse = np.mean(residuals ** 2)
        
        results.append({
            "genotype_id": gid,
            "fw_slope": round(slope, 4),
            "fw_intercept": round(intercept, 4),
            "fw_r2": round(r_value ** 2, 4),
            "stability_mse": round(mse, 4),
            "mean_performance": round(np.mean(y), 2),
            "n_environments": len(common_envs),
        })
    
    return pd.DataFrame(results).sort_values("mean_performance", ascending=False)
