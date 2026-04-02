#!/usr/bin/env python3
"""
Genomic Selection Pipeline - Main Entry Point
==============================================
End-to-end genomic selection pipeline for subtropical fruit breeding.

Pipeline stages:
1. Simulate (or load) SNP genotype and phenotype data
2. SNP quality control and filtering
3. Population structure analysis (PCA, GRM, diversity)
4. Heritability estimation for each trait
5. BLUP breeding value prediction
6. Genomic selection model training and cross-validation
7. Generate results and visualizations

Usage:
    python run_gs_pipeline.py [--simulate-data] [--n-individuals 300] [--n-markers 5000]
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_simulator import simulate_snp_data, simulate_phenotypes
from src.snp_processor import SNPProcessor
from src.population_genetics import (
    compute_genomic_relationship_matrix, pca_analysis,
    compute_genetic_diversity, population_differentiation
)
from src.mixed_models import (
    estimate_heritability, compute_blup, 
    multi_trait_correlations, selection_index
)
from src.genomic_selection import GenomicSelectionModel
from src.visualization import (
    plot_pca_population_structure, plot_grm_heatmap,
    plot_prediction_accuracy, plot_marker_effects,
    plot_heritability_summary, plot_breeding_value_distribution
)


def main():
    parser = argparse.ArgumentParser(description="Genomic Selection Pipeline")
    parser.add_argument("--n-individuals", type=int, default=300)
    parser.add_argument("--n-markers", type=int, default=5000)
    parser.add_argument("--n-folds", type=int, default=5)
    args = parser.parse_args()
    
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    print("=" * 60)
    print("  GENOMIC SELECTION PIPELINE")
    print("  Subtropical Fruit Breeding Program")
    print("=" * 60)
    
    # =========================================================
    # Stage 1: Data Generation
    # =========================================================
    print("\n[1/7] DATA SIMULATION")
    print("-" * 40)
    
    geno_df, genotypes, marker_info = simulate_snp_data(
        n_individuals=args.n_individuals,
        n_markers=args.n_markers
    )
    pheno_df = simulate_phenotypes(genotypes, marker_info)
    
    print(f"  Genotypes: {geno_df.shape[0]} individuals x {geno_df.shape[1]} markers")
    print(f"  Phenotypes: {pheno_df.shape[0]} individuals")
    
    # =========================================================
    # Stage 2: SNP Quality Control
    # =========================================================
    print("\n[2/7] SNP QUALITY CONTROL")
    print("-" * 40)
    
    processor = SNPProcessor(geno_df)
    geno_filtered = processor.run_qc(
        maf_threshold=0.05,
        marker_missing_rate=0.10,
        individual_missing_rate=0.20
    )
    print(processor.get_qc_summary())
    
    # =========================================================
    # Stage 3: Population Structure
    # =========================================================
    print("\n[3/7] POPULATION STRUCTURE ANALYSIS")
    print("-" * 40)
    
    # GRM
    geno_matrix = geno_filtered.values.astype(float)
    grm = compute_genomic_relationship_matrix(geno_matrix)
    print(f"  GRM computed: {grm.shape}")
    print(f"  Mean diagonal: {np.mean(np.diag(grm)):.4f}")
    print(f"  Mean off-diagonal: {np.mean(grm[np.triu_indices_from(grm, k=1)]):.4f}")
    
    # PCA
    pca_result = pca_analysis(geno_filtered, n_components=10)
    print(f"  Top 3 PCs explain: {pca_result['cumulative_variance'][2]:.1%} of variance")
    
    # Population labels from simulation
    pop_labels = pd.Series(
        [f"Pop_{p+1}" for p in marker_info["pop_assignments"]],
        index=marker_info["individual_ids"]
    )
    pop_labels_filtered = pop_labels[geno_filtered.index]
    
    # Genetic diversity
    diversity = compute_genetic_diversity(geno_filtered)
    print(f"\n  Genetic Diversity:")
    for key, val in diversity.items():
        print(f"    {key}: {val}")
    
    # Population differentiation
    fst = population_differentiation(geno_filtered, pop_labels_filtered)
    print(f"\n  Global Fst: {fst['global_fst']}")
    for pair, val in fst["pairwise_fst"].items():
        print(f"    {pair}: {val}")
    
    # Visualizations
    plot_pca_population_structure(pca_result, pop_labels_filtered, results_dir)
    plot_grm_heatmap(grm, output_dir=results_dir, pop_labels=pop_labels_filtered)
    
    # =========================================================
    # Stage 4: Heritability Estimation
    # =========================================================
    print("\n[4/7] HERITABILITY ESTIMATION")
    print("-" * 40)
    
    trait_cols = [c for c in pheno_df.columns if c not in ["individual_id", "population"]]
    
    # Align phenotypes with filtered genotype matrix
    common_ids = geno_filtered.index.intersection(pheno_df.set_index("individual_id").index)
    pheno_aligned = pheno_df.set_index("individual_id").loc[common_ids]
    grm_aligned = grm[:len(common_ids), :len(common_ids)]
    
    heritability_results = {}
    for trait in trait_cols:
        h2_result = estimate_heritability(
            pheno_aligned[trait].values,
            grm_aligned
        )
        heritability_results[trait] = h2_result
        print(f"  {trait}: h² = {h2_result['h2']:.4f}")
    
    plot_heritability_summary(heritability_results, results_dir)
    
    # =========================================================
    # Stage 5: BLUP Breeding Values
    # =========================================================
    print("\n[5/7] BLUP BREEDING VALUE ESTIMATION")
    print("-" * 40)
    
    breeding_values = {}
    for trait in trait_cols:
        h2 = heritability_results[trait]["h2"]
        blup_result = compute_blup(
            pheno_aligned[trait].values,
            grm_aligned,
            h2=max(h2, 0.1)  # Floor for numerical stability
        )
        breeding_values[trait] = blup_result["breeding_values"]
        print(f"  {trait}: mean reliability = {blup_result['mean_reliability']:.4f}")
        
        plot_breeding_value_distribution(
            blup_result["breeding_values"], trait, output_dir=results_dir
        )
    
    # Multi-trait selection index
    weights = {
        "fruit_weight_g": 1.0,
        "brix_content": 1.5,        # High priority for flavor
        "yield_kg_per_tree": 1.2,
        "disease_resistance": 1.3,
        "days_to_maturity": -0.8,    # Negative: prefer earlier maturity
    }
    
    sel_index = selection_index(breeding_values, weights)
    top_20_idx = np.argsort(sel_index[~np.isnan(sel_index)])[-20:][::-1]
    
    print(f"\n  Top 20 genotypes by multi-trait selection index:")
    for rank, idx in enumerate(top_20_idx[:10], 1):
        print(f"    {rank}. {common_ids[idx]}: index = {sel_index[idx]:.3f}")
    
    # =========================================================
    # Stage 6: Genomic Selection Models
    # =========================================================
    print("\n[6/7] GENOMIC SELECTION MODEL TRAINING")
    print("-" * 40)
    
    # Use the primary breeding trait for GS model comparison
    primary_trait = "brix_content"
    print(f"\n  Primary trait: {primary_trait}")
    
    geno_for_gs = geno_filtered.loc[common_ids].values.astype(float)
    pheno_for_gs = pheno_aligned[primary_trait].values
    
    gs_model = GenomicSelectionModel(
        geno_for_gs, pheno_for_gs, 
        individual_ids=list(common_ids)
    )
    
    print("\n  Training rrBLUP (Ridge Regression)...")
    rrblup_result = gs_model.train_rrblup(alpha=1.0)
    print(f"    Training R²: {rrblup_result['r2_training']}, r: {rrblup_result['correlation']}")
    
    print("\n  Training LASSO...")
    lasso_result = gs_model.train_lasso(alpha=0.1)
    print(f"    Training R²: {lasso_result['r2_training']}, r: {lasso_result['correlation']}")
    print(f"    Markers selected: {lasso_result['n_nonzero_markers']} ({lasso_result['pct_markers_selected']}%)")
    
    print("\n  Training Elastic Net...")
    enet_result = gs_model.train_elastic_net(alpha=0.1, l1_ratio=0.5)
    print(f"    Training R²: {enet_result['r2_training']}, r: {enet_result['correlation']}")
    
    print("\n  Model Comparison:")
    comparison = gs_model.compare_models()
    print(comparison.to_string(index=False))
    
    # =========================================================
    # Stage 7: Cross-Validation
    # =========================================================
    print(f"\n[7/7] {args.n_folds}-FOLD CROSS-VALIDATION")
    print("-" * 40)
    
    cv_results = gs_model.cross_validate(n_folds=args.n_folds)
    
    # Summary
    cv_summary = cv_results.groupby("model").agg({
        "correlation": ["mean", "std"],
        "rmse": ["mean", "std"]
    }).round(4)
    print("\n  Cross-Validation Summary:")
    print(cv_summary.to_string())
    
    # Save CV results
    cv_results.to_csv(os.path.join(results_dir, "cv_results.csv"), index=False)
    
    # Visualizations
    plot_prediction_accuracy(cv_results, results_dir)
    
    # Marker effects from rrBLUP
    effects = gs_model.get_marker_effects("rrBLUP")
    plot_marker_effects(effects, output_dir=results_dir)
    
    # =========================================================
    # Summary
    # =========================================================
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\n  Individuals analyzed:  {len(common_ids)}")
    print(f"  Markers after QC:      {geno_filtered.shape[1]}")
    print(f"  Traits analyzed:       {len(trait_cols)}")
    print(f"  Best GS model (CV r):  {cv_summary[('correlation', 'mean')].idxmax()}")
    print(f"  Results saved to:      {results_dir}/")


if __name__ == "__main__":
    main()
