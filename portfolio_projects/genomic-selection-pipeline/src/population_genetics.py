"""
Population Genetics Module
==========================
Analysis of population structure, genetic diversity, and relatedness
from SNP marker data. Essential for understanding breeding populations
and accounting for structure in genomic prediction models.
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from scipy.spatial.distance import pdist, squareform


def compute_genomic_relationship_matrix(geno_matrix: np.ndarray) -> np.ndarray:
    """
    Compute the genomic relationship matrix (GRM) using VanRaden Method 1.
    
    G = (Z * Z') / (2 * sum(pi * qi))
    
    Where Z = M - 2P (centered genotype matrix),
    M is the marker matrix coded 0/1/2,
    P is the matrix of allele frequencies.
    
    Parameters
    ----------
    geno_matrix : np.ndarray
        Genotype matrix (n individuals x p markers), coded 0/1/2
        
    Returns
    -------
    np.ndarray
        Genomic relationship matrix (n x n)
    """
    # Allele frequencies
    p = geno_matrix.mean(axis=0) / 2
    
    # Filter markers with zero variance
    valid = (p > 0) & (p < 1)
    M = geno_matrix[:, valid].astype(float)
    p = p[valid]
    
    # Center genotypes
    Z = M - 2 * p
    
    # Scaling factor
    scaling = 2 * np.sum(p * (1 - p))
    
    if scaling == 0:
        return np.eye(geno_matrix.shape[0])
    
    G = Z @ Z.T / scaling
    
    return G


def pca_analysis(geno_df: pd.DataFrame, n_components: int = 10) -> dict:
    """
    Principal Component Analysis of genotype data for population structure.
    
    Parameters
    ----------
    geno_df : pd.DataFrame
        Genotype matrix (individuals x markers)
    n_components : int
        Number of PCs to compute
        
    Returns
    -------
    dict with keys:
        'scores': PC scores DataFrame
        'variance_explained': variance explained per PC
        'loadings': PC loadings
    """
    # Impute missing with column means
    geno_imputed = geno_df.fillna(geno_df.mean())
    
    # Center and scale
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(geno_imputed.values)
    
    scores_df = pd.DataFrame(
        scores,
        index=geno_df.index,
        columns=[f"PC{i+1}" for i in range(n_components)]
    )
    
    return {
        "scores": scores_df,
        "variance_explained": pca.explained_variance_ratio_,
        "cumulative_variance": np.cumsum(pca.explained_variance_ratio_),
        "loadings": pca.components_,
    }


def compute_genetic_diversity(geno_df: pd.DataFrame) -> dict:
    """
    Compute genetic diversity statistics.
    
    Returns
    -------
    dict with diversity metrics:
        - observed_heterozygosity
        - expected_heterozygosity
        - nucleotide_diversity (pi)
        - inbreeding_coefficient (Fis)
    """
    geno = geno_df.values.astype(float)
    n_ind = geno.shape[0]
    
    # Allele frequencies
    p = np.nanmean(geno, axis=0) / 2
    q = 1 - p
    
    # Observed heterozygosity (proportion of heterozygotes per locus)
    het_obs = np.nanmean(geno == 1, axis=0)
    mean_ho = np.nanmean(het_obs)
    
    # Expected heterozygosity (2pq)
    het_exp = 2 * p * q
    mean_he = np.nanmean(het_exp)
    
    # Inbreeding coefficient F = 1 - Ho/He
    valid = het_exp > 0
    fis = 1 - np.nanmean(het_obs[valid] / het_exp[valid]) if valid.any() else 0
    
    return {
        "n_individuals": n_ind,
        "n_markers": geno.shape[1],
        "observed_heterozygosity": round(mean_ho, 4),
        "expected_heterozygosity": round(mean_he, 4),
        "inbreeding_coefficient_Fis": round(fis, 4),
        "mean_maf": round(np.nanmean(np.minimum(p, q)), 4),
    }


def population_differentiation(geno_df: pd.DataFrame, pop_labels: pd.Series) -> dict:
    """
    Compute Fst (population differentiation) between sub-populations.
    Uses Weir and Cockerham's estimator (simplified).
    
    Parameters
    ----------
    geno_df : pd.DataFrame
        Genotype matrix
    pop_labels : pd.Series  
        Population labels for each individual
        
    Returns
    -------
    dict with Fst values
    """
    populations = pop_labels.unique()
    n_pops = len(populations)
    
    geno = geno_df.values.astype(float)
    
    # Overall allele frequencies
    p_total = np.nanmean(geno, axis=0) / 2
    
    # Per-population allele frequencies
    p_pops = {}
    for pop in populations:
        mask = pop_labels == pop
        p_pops[pop] = np.nanmean(geno[mask], axis=0) / 2
    
    # Fst (simplified Nei's Fst)
    # Fst = (Ht - Hs) / Ht where Ht = total heterozygosity, Hs = mean within-pop het
    ht = 2 * p_total * (1 - p_total)
    
    hs_values = []
    for pop in populations:
        p = p_pops[pop]
        hs_values.append(2 * p * (1 - p))
    hs = np.mean(hs_values, axis=0)
    
    valid = ht > 0
    fst_per_locus = np.zeros(len(ht))
    fst_per_locus[valid] = (ht[valid] - hs[valid]) / ht[valid]
    
    # Pairwise Fst
    pairwise_fst = {}
    for i, pop1 in enumerate(populations):
        for pop2 in populations[i+1:]:
            p1 = p_pops[pop1]
            p2 = p_pops[pop2]
            pt = (p1 + p2) / 2
            ht_pair = 2 * pt * (1 - pt)
            hs_pair = (2 * p1 * (1 - p1) + 2 * p2 * (1 - p2)) / 2
            valid_pair = ht_pair > 0
            if valid_pair.any():
                fst_pair = np.mean((ht_pair[valid_pair] - hs_pair[valid_pair]) / ht_pair[valid_pair])
            else:
                fst_pair = 0
            pairwise_fst[f"{pop1}_vs_{pop2}"] = round(fst_pair, 4)
    
    return {
        "global_fst": round(np.mean(fst_per_locus[valid]), 4),
        "pairwise_fst": pairwise_fst,
        "n_populations": n_pops,
    }
