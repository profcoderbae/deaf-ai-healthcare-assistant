"""
Mixed Models Module (Simplified)
================================
Approximations of mixed model analyses for breeding value estimation:
- Heritability estimation
- BLUP-like breeding value prediction using genomic relationship matrix
- Multi-trait analysis support

Note: For production use, dedicated packages like ASReml-R, sommer, or
BGLR would be used. These implementations demonstrate the concepts
using numpy/scipy linear algebra.
"""

import numpy as np
import pandas as pd
from scipy import linalg


def estimate_heritability(phenotypes: np.ndarray, grm: np.ndarray,
                          method: str = "regression") -> dict:
    """
    Estimate narrow-sense heritability (h²) from phenotype and GRM.
    
    Parameters
    ----------
    phenotypes : np.ndarray
        Phenotype vector (n,)
    grm : np.ndarray
        Genomic relationship matrix (n x n)
    method : str
        'regression' for simple regression-based estimate
        
    Returns
    -------
    dict with h2 estimate and related statistics
    """
    # Remove missing phenotypes
    valid = ~np.isnan(phenotypes)
    y = phenotypes[valid]
    G = grm[np.ix_(valid, valid)]
    n = len(y)
    
    # Center phenotype
    y_centered = y - y.mean()
    
    if method == "regression":
        # REML-like estimation via variance components
        # Using Haseman-Elston regression: Cov(yi, yj) ~ h2 * Gij
        
        # Upper triangle of pairwise products and GRM values
        upper_idx = np.triu_indices(n, k=1)
        y_products = np.outer(y_centered, y_centered)[upper_idx]
        g_values = G[upper_idx]
        
        # Regression of phenotype covariance on genetic relatedness
        # slope = Var(A) / Var(P) ≈ h²
        var_p = np.var(y_centered)
        
        if var_p > 0 and np.std(g_values) > 0:
            beta = np.cov(y_products, g_values)[0, 1] / np.var(g_values)
            h2 = np.clip(beta / var_p, 0, 1)
        else:
            h2 = 0.0
        
        return {
            "h2": round(float(h2), 4),
            "var_phenotypic": round(float(var_p), 4),
            "var_additive_est": round(float(h2 * var_p), 4),
            "var_residual_est": round(float((1 - h2) * var_p), 4),
            "n_individuals": n,
            "method": method,
        }


def compute_blup(phenotypes: np.ndarray, grm: np.ndarray, 
                  h2: float, fixed_effects: np.ndarray = None) -> dict:
    """
    Compute BLUP (Best Linear Unbiased Prediction) breeding values.
    
    Mixed model: y = Xb + Zu + e
    where u ~ N(0, G * sigma_a²), e ~ N(0, I * sigma_e²)
    
    Henderson's mixed model equations:
    [X'X    X'Z  ] [b_hat] = [X'y ]
    [Z'X  Z'Z+λG⁻¹] [u_hat]   [Z'y ]
    
    where λ = sigma_e² / sigma_a²
    
    Parameters
    ----------
    phenotypes : np.ndarray
        Phenotype vector
    grm : np.ndarray
        Genomic relationship matrix
    h2 : float
        Heritability estimate
    fixed_effects : np.ndarray
        Fixed effects design matrix (default: intercept only)
        
    Returns
    -------
    dict with BLUP breeding values and reliability
    """
    valid = ~np.isnan(phenotypes)
    y = phenotypes[valid]
    G = grm[np.ix_(valid, valid)]
    n = len(y)
    
    # Variance ratio
    if h2 > 0 and h2 < 1:
        lambda_ratio = (1 - h2) / h2
    else:
        lambda_ratio = 10.0  # Default for extreme h2 values
    
    # Fixed effects (intercept only)
    if fixed_effects is None:
        X = np.ones((n, 1))
    else:
        X = fixed_effects[valid]
    
    Z = np.eye(n)
    
    # Regularize GRM for invertibility
    G_reg = G + np.eye(n) * 0.01
    
    try:
        G_inv = linalg.inv(G_reg)
    except linalg.LinAlgError:
        G_inv = linalg.pinv(G_reg)
    
    # Build Henderson's MME
    n_fixed = X.shape[1]
    mme_size = n_fixed + n
    
    LHS = np.zeros((mme_size, mme_size))
    RHS = np.zeros(mme_size)
    
    # X'X, X'Z, Z'X, Z'Z + lambda*G_inv
    LHS[:n_fixed, :n_fixed] = X.T @ X
    LHS[:n_fixed, n_fixed:] = X.T @ Z
    LHS[n_fixed:, :n_fixed] = Z.T @ X
    LHS[n_fixed:, n_fixed:] = Z.T @ Z + lambda_ratio * G_inv
    
    RHS[:n_fixed] = X.T @ y
    RHS[n_fixed:] = Z.T @ y
    
    # Solve MME
    try:
        solutions = linalg.solve(LHS, RHS)
    except linalg.LinAlgError:
        solutions = linalg.lstsq(LHS, RHS)[0]
    
    fixed_solutions = solutions[:n_fixed]
    breeding_values = solutions[n_fixed:]
    
    # Reliability (simplified: r² = 1 - PEV/var_a)
    try:
        C = linalg.inv(LHS)
        PEV = np.diag(C[n_fixed:, n_fixed:])
        var_a = h2 * np.var(y)
        reliability = np.clip(1 - PEV / max(var_a, 1e-6), 0, 1)
    except linalg.LinAlgError:
        reliability = np.full(n, np.nan)
    
    # Map back to full individual set
    full_bv = np.full(len(phenotypes), np.nan)
    full_rel = np.full(len(phenotypes), np.nan)
    full_bv[valid] = breeding_values
    full_rel[valid] = reliability
    
    return {
        "breeding_values": full_bv,
        "reliability": full_rel,
        "fixed_effects": fixed_solutions,
        "intercept": fixed_solutions[0],
        "mean_reliability": round(float(np.nanmean(reliability)), 4),
    }


def multi_trait_correlations(pheno_df: pd.DataFrame, trait_cols: list) -> pd.DataFrame:
    """
    Compute phenotypic correlation matrix between traits.
    
    Parameters
    ----------
    pheno_df : pd.DataFrame
        Phenotype data
    trait_cols : list
        Column names for traits
        
    Returns
    -------
    pd.DataFrame
        Correlation matrix
    """
    return pheno_df[trait_cols].corr()


def selection_index(breeding_values: dict, weights: dict) -> np.ndarray:
    """
    Compute a multi-trait selection index from BLUP breeding values.
    
    Parameters
    ----------
    breeding_values : dict
        {trait_name: np.ndarray of BVs}
    weights : dict
        {trait_name: economic weight}
        
    Returns
    -------
    np.ndarray
        Selection index values
    """
    index = None
    for trait, bv in breeding_values.items():
        w = weights.get(trait, 0)
        if w == 0:
            continue
        
        # Standardize BVs before weighting
        valid = ~np.isnan(bv)
        bv_std = np.full_like(bv, np.nan)
        if valid.any() and np.std(bv[valid]) > 0:
            bv_std[valid] = (bv[valid] - np.mean(bv[valid])) / np.std(bv[valid])
        
        if index is None:
            index = w * bv_std
        else:
            index = index + w * bv_std
    
    return index if index is not None else np.zeros(len(next(iter(breeding_values.values()))))
