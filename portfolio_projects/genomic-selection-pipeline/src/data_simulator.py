"""
SNP & Phenotype Data Simulator
===============================
Generates realistic synthetic genotypic (SNP marker) and phenotypic data
for demonstrating genomic selection pipelines in subtropical fruit breeding.

Simulates:
- Bi-allelic SNP markers with realistic MAF distributions
- Population structure (sub-populations)
- Correlated phenotypic traits with known heritabilities
- QTL effects (markers with true trait associations)
"""

import numpy as np
import pandas as pd
from typing import Tuple


def simulate_snp_data(
    n_individuals: int = 300,
    n_markers: int = 5000,
    n_qtl: int = 50,
    n_subpops: int = 3,
    seed: int = 42
) -> Tuple[pd.DataFrame, np.ndarray, dict]:
    """
    Simulate bi-allelic SNP marker data with population structure.
    
    Parameters
    ----------
    n_individuals : int
        Number of genotyped individuals (breeding lines)
    n_markers : int
        Number of SNP markers
    n_qtl : int
        Number of QTLs (markers with true trait effects)
    n_subpops : int
        Number of sub-populations to simulate
    seed : int
        Random seed
        
    Returns
    -------
    geno_df : pd.DataFrame
        Genotype matrix (individuals x markers), coded 0/1/2
    pheno_array : np.ndarray
        Not used here — phenotypes generated separately
    marker_info : dict
        Information about markers including QTL positions and effects
    """
    rng = np.random.default_rng(seed)
    
    # Generate individual IDs (subtropical breeding lines)
    individual_ids = [f"MNG-{2018 + i // 100}-{i % 100 + 1:04d}" 
                      for i in range(n_individuals)]
    
    # Assign sub-populations
    pop_assignments = rng.choice(n_subpops, n_individuals)
    
    # Generate allele frequencies per sub-population
    base_freq = rng.beta(2, 5, n_markers)  # Realistic MAF distribution
    pop_freqs = np.zeros((n_subpops, n_markers))
    
    for pop in range(n_subpops):
        # Drift from base frequencies
        drift = rng.normal(0, 0.05, n_markers)
        pop_freqs[pop] = np.clip(base_freq + drift, 0.01, 0.99)
    
    # Sample genotypes (0, 1, 2 coding) based on population freqs
    genotypes = np.zeros((n_individuals, n_markers), dtype=np.int8)
    for i in range(n_individuals):
        pop = pop_assignments[i]
        for allele in range(2):  # Two alleles per locus
            genotypes[i] += rng.binomial(1, pop_freqs[pop])
    
    # Marker names
    marker_names = [f"SNP_{chr_}_{pos}" 
                    for chr_ in range(1, 11) 
                    for pos in range(1, n_markers // 10 + 1)][:n_markers]
    
    # Select QTL markers and assign effects
    qtl_indices = rng.choice(n_markers, n_qtl, replace=False)
    qtl_effects = rng.normal(0, 1.0, n_qtl)
    # Most QTL have small effects, few have large effects
    qtl_effects *= rng.exponential(0.5, n_qtl)
    
    marker_info = {
        "marker_names": marker_names,
        "qtl_indices": qtl_indices,
        "qtl_effects": qtl_effects,
        "qtl_markers": [marker_names[i] for i in qtl_indices],
        "maf": np.minimum(genotypes.mean(axis=0) / 2, 1 - genotypes.mean(axis=0) / 2),
        "pop_assignments": pop_assignments,
        "individual_ids": individual_ids,
    }
    
    geno_df = pd.DataFrame(genotypes, index=individual_ids, columns=marker_names)
    
    return geno_df, genotypes, marker_info


def simulate_phenotypes(
    genotypes: np.ndarray,
    marker_info: dict,
    traits: dict = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Simulate phenotypic data from genotypes with known heritabilities.
    
    Parameters
    ----------
    genotypes : np.ndarray
        Genotype matrix (n x p), coded 0/1/2
    marker_info : dict
        Output from simulate_snp_data
    traits : dict
        Trait definitions {name: {"h2": heritability, "mean": population_mean}}
    seed : int
        Random seed
        
    Returns
    -------
    pd.DataFrame
        Phenotype data with individual IDs and trait values
    """
    rng = np.random.default_rng(seed)
    n = genotypes.shape[0]
    
    if traits is None:
        traits = {
            "fruit_weight_g": {"h2": 0.45, "mean": 350},
            "brix_content": {"h2": 0.60, "mean": 16},
            "yield_kg_per_tree": {"h2": 0.25, "mean": 80},
            "disease_resistance": {"h2": 0.35, "mean": 5.5},
            "days_to_maturity": {"h2": 0.55, "mean": 140},
        }
    
    qtl_idx = marker_info["qtl_indices"]
    qtl_effects = marker_info["qtl_effects"]
    
    pheno_data = {"individual_id": marker_info["individual_ids"]}
    pheno_data["population"] = [f"Pop_{p+1}" for p in marker_info["pop_assignments"]]
    
    for trait_name, params in traits.items():
        h2 = params["h2"]
        mean = params["mean"]
        
        # Genetic value from QTL effects (subset for each trait)
        n_qtl_trait = max(5, len(qtl_idx) // len(traits))
        trait_qtl = qtl_idx[:n_qtl_trait]
        trait_effects = qtl_effects[:n_qtl_trait] * rng.normal(1, 0.3, n_qtl_trait)
        
        genetic_values = genotypes[:, trait_qtl] @ trait_effects
        
        # Scale to desired heritability
        var_g = np.var(genetic_values)
        if var_g > 0:
            var_e = var_g * (1 - h2) / h2
        else:
            var_e = 1.0
        
        environmental = rng.normal(0, np.sqrt(var_e), n)
        phenotype = mean + genetic_values + environmental
        
        # Add ~3% missing phenotypes
        missing_mask = rng.random(n) < 0.03
        phenotype[missing_mask] = np.nan
        
        pheno_data[trait_name] = np.round(phenotype, 2)
    
    return pd.DataFrame(pheno_data)


def save_simulated_data(output_dir: str = "data"):
    """Generate and save all simulated data."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print("Simulating SNP genotype data...")
    geno_df, genotypes, marker_info = simulate_snp_data()
    
    print("Simulating phenotype data...")
    pheno_df = simulate_phenotypes(genotypes, marker_info)
    
    # Save genotype matrix
    geno_df.to_csv(os.path.join(output_dir, "genotype_matrix.csv"))
    print(f"  Genotype matrix: {geno_df.shape[0]} individuals x {geno_df.shape[1]} markers")
    
    # Save phenotype data
    pheno_df.to_csv(os.path.join(output_dir, "phenotype_data.csv"), index=False)
    print(f"  Phenotype data: {pheno_df.shape[0]} individuals, {len([c for c in pheno_df.columns if c not in ['individual_id', 'population']])} traits")
    
    # Save marker info
    marker_df = pd.DataFrame({
        "marker": marker_info["marker_names"],
        "maf": marker_info["maf"],
        "is_qtl": [m in marker_info["qtl_markers"] for m in marker_info["marker_names"]],
    })
    marker_df.to_csv(os.path.join(output_dir, "marker_info.csv"), index=False)
    
    return geno_df, pheno_df, marker_info


if __name__ == "__main__":
    save_simulated_data()
