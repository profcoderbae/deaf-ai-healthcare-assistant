"""
Visualization Module
====================
Publication-quality visualizations for genomic selection analyses:
- PCA population structure plots
- GRM heatmaps
- Prediction accuracy comparisons
- Marker effect Manhattan-style plots
- Trait distribution and heritability summaries
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def plot_pca_population_structure(pca_result: dict, pop_labels: pd.Series = None,
                                   output_dir: str = "results"):
    """Plot PCA scatter of first 3 PCs colored by population."""
    os.makedirs(output_dir, exist_ok=True)
    
    scores = pca_result["scores"]
    var_exp = pca_result["variance_explained"]
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # PC1 vs PC2
    ax = axes[0]
    if pop_labels is not None:
        for pop in pop_labels.unique():
            mask = pop_labels == pop
            ax.scatter(scores.loc[mask, "PC1"], scores.loc[mask, "PC2"],
                      label=pop, alpha=0.6, s=20)
        ax.legend(title="Population")
    else:
        ax.scatter(scores["PC1"], scores["PC2"], alpha=0.5, s=15)
    
    ax.set_xlabel(f"PC1 ({var_exp[0]:.1%} variance)")
    ax.set_ylabel(f"PC2 ({var_exp[1]:.1%} variance)")
    ax.set_title("Population Structure: PC1 vs PC2")
    ax.grid(True, alpha=0.3)
    
    # Scree plot
    ax = axes[1]
    n_pcs = len(var_exp)
    ax.bar(range(1, n_pcs + 1), var_exp * 100, color="steelblue", alpha=0.7)
    ax.plot(range(1, n_pcs + 1), pca_result["cumulative_variance"] * 100,
            "ro-", markersize=5)
    ax.set_xlabel("Principal Component")
    ax.set_ylabel("Variance Explained (%)")
    ax.set_title("Scree Plot")
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "pca_population_structure.png"), dpi=150)
    plt.close()
    print(f"  Saved PCA plot")


def plot_grm_heatmap(grm: np.ndarray, individual_ids: list = None,
                      pop_labels: pd.Series = None, output_dir: str = "results"):
    """Plot genomic relationship matrix as a heatmap."""
    os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Sort by population if available
    if pop_labels is not None:
        sort_idx = np.argsort(pop_labels.values)
        grm_sorted = grm[np.ix_(sort_idx, sort_idx)]
    else:
        grm_sorted = grm
    
    im = ax.imshow(grm_sorted, cmap="RdBu_r", vmin=-0.5, vmax=1.5, aspect="auto")
    plt.colorbar(im, ax=ax, label="Genomic Relationship")
    ax.set_title("Genomic Relationship Matrix (GRM)")
    ax.set_xlabel("Individuals")
    ax.set_ylabel("Individuals")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "grm_heatmap.png"), dpi=150)
    plt.close()
    print(f"  Saved GRM heatmap")


def plot_prediction_accuracy(cv_results: pd.DataFrame, output_dir: str = "results"):
    """Plot cross-validation prediction accuracy comparison."""
    os.makedirs(output_dir, exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Box plot of prediction correlations
    sns.boxplot(data=cv_results, x="model", y="correlation", ax=ax1, palette="Set2")
    ax1.set_title("Prediction Accuracy (CV)")
    ax1.set_ylabel("Pearson Correlation (r)")
    ax1.set_xlabel("Model")
    ax1.grid(True, alpha=0.3, axis="y")
    
    # RMSE comparison
    sns.boxplot(data=cv_results, x="model", y="rmse", ax=ax2, palette="Set2")
    ax2.set_title("Prediction Error (CV)")
    ax2.set_ylabel("RMSE")
    ax2.set_xlabel("Model")
    ax2.grid(True, alpha=0.3, axis="y")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "prediction_accuracy_comparison.png"), dpi=150)
    plt.close()
    print(f"  Saved prediction accuracy plot")


def plot_marker_effects(effects_df: pd.DataFrame, top_n: int = 50,
                         output_dir: str = "results"):
    """Manhattan-style plot of marker effects from GS model."""
    os.makedirs(output_dir, exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
    
    # All marker effects
    ax1.scatter(range(len(effects_df)), effects_df["abs_effect"].sort_index(),
               alpha=0.3, s=5, color="steelblue")
    ax1.set_xlabel("Marker Index")
    ax1.set_ylabel("Absolute Effect Size")
    ax1.set_title("Marker Effect Sizes Across Genome")
    ax1.grid(True, alpha=0.3)
    
    # Top markers
    top = effects_df.head(top_n)
    ax2.barh(range(min(top_n, len(top))), top["abs_effect"].values[:top_n],
            color="coral", alpha=0.7)
    ax2.set_yticks(range(min(top_n, len(top))))
    ax2.set_yticklabels([f"Marker {i}" for i in top["marker_index"].values[:top_n]],
                        fontsize=7)
    ax2.set_xlabel("Absolute Effect Size")
    ax2.set_title(f"Top {top_n} Markers by Effect Size")
    ax2.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "marker_effects.png"), dpi=150)
    plt.close()
    print(f"  Saved marker effects plot")


def plot_heritability_summary(heritability_results: dict, output_dir: str = "results"):
    """Bar chart of heritability estimates across traits."""
    os.makedirs(output_dir, exist_ok=True)
    
    traits = list(heritability_results.keys())
    h2_values = [heritability_results[t]["h2"] for t in traits]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ["#2ecc71" if h > 0.4 else "#f39c12" if h > 0.2 else "#e74c3c" 
              for h in h2_values]
    
    bars = ax.barh(range(len(traits)), h2_values, color=colors, alpha=0.8)
    ax.set_yticks(range(len(traits)))
    ax.set_yticklabels([t.replace("_", " ").title() for t in traits])
    ax.set_xlabel("Narrow-Sense Heritability (h²)")
    ax.set_title("Heritability Estimates by Trait")
    ax.set_xlim(0, 1)
    ax.axvline(x=0.3, color="gray", linestyle="--", alpha=0.5, label="h²=0.3")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="x")
    
    # Add value labels
    for bar, val in zip(bars, h2_values):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center", fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "heritability_summary.png"), dpi=150)
    plt.close()
    print(f"  Saved heritability summary plot")


def plot_breeding_value_distribution(bv: np.ndarray, trait_name: str,
                                      top_n: int = 20, output_dir: str = "results"):
    """Plot distribution of breeding values with top selections highlighted."""
    os.makedirs(output_dir, exist_ok=True)
    
    valid_bv = bv[~np.isnan(bv)]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Histogram
    ax1.hist(valid_bv, bins=40, color="steelblue", alpha=0.7, edgecolor="white")
    threshold = np.percentile(valid_bv, 100 - (top_n / len(valid_bv) * 100))
    ax1.axvline(threshold, color="red", linestyle="--", 
                label=f"Top {top_n} selection threshold")
    ax1.set_xlabel("Breeding Value (GEBV)")
    ax1.set_ylabel("Frequency")
    ax1.set_title(f"GEBV Distribution: {trait_name.replace('_', ' ').title()}")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Ranked breeding values
    sorted_bv = np.sort(valid_bv)[::-1]
    colors = ["coral" if i < top_n else "steelblue" for i in range(len(sorted_bv))]
    ax2.scatter(range(len(sorted_bv)), sorted_bv, c=colors, s=8, alpha=0.5)
    ax2.set_xlabel("Rank")
    ax2.set_ylabel("Breeding Value (GEBV)")
    ax2.set_title("Ranked Breeding Values")
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"gebv_distribution_{trait_name}.png"), dpi=150)
    plt.close()
    print(f"  Saved GEBV distribution for {trait_name}")
