# Genomic Selection Pipeline

A complete genomic selection (GS) pipeline for subtropical fruit breeding, covering SNP quality control, population structure analysis, heritability estimation, BLUP breeding value prediction, and genomic prediction model training with cross-validation.

## Problem Addressed

Modern breeding programs increasingly rely on genomic information to accelerate genetic gain. This pipeline demonstrates the integration of genotypic (SNP marker) and phenotypic data to predict breeding values and identify superior genotypes before extensive field testing — reducing breeding cycle time and increasing selection accuracy.

## Key Features

- **SNP Quality Control** — MAF filtering, missing data rates, Hardy-Weinberg equilibrium testing
- **Population Structure** — PCA analysis, genomic relationship matrix (GRM) using VanRaden Method 1, Fst statistics
- **Genetic Diversity Analysis** — Observed/expected heterozygosity, inbreeding coefficients
- **Heritability Estimation** — Narrow-sense h² using Haseman-Elston regression approach
- **BLUP Breeding Values** — Henderson's Mixed Model Equations for genomic BLUP
- **Multi-Trait Selection Index** — Weighted index combining breeding values across traits
- **Genomic Prediction Models** — rrBLUP (Ridge), LASSO, Elastic Net with K-fold cross-validation
- **Publication-Quality Visualizations** — PCA plots, GRM heatmaps, prediction accuracy comparisons, marker effect Manhattan plots

## Architecture

```
SNP Data → QC → GRM/PCA → Heritability → BLUP → GS Models → Cross-Validation → Selection
```

## Technologies

- **Python** (numpy, pandas, scipy, scikit-learn)
- **Linear algebra** — Genomic relationship matrices, Henderson's MME
- **Machine learning** — Ridge regression, LASSO, Elastic Net
- **matplotlib / seaborn** for publication-quality plots

## Project Structure

```
genomic-selection-pipeline/
├── run_gs_pipeline.py          # Main entry point
├── src/
│   ├── data_simulator.py       # Realistic SNP & phenotype simulation
│   ├── snp_processor.py        # Genotyping QC (MAF, HWE, missingness)
│   ├── population_genetics.py  # GRM, PCA, diversity, Fst
│   ├── mixed_models.py         # Heritability, BLUP, selection indices
│   ├── genomic_selection.py    # GS model training & cross-validation
│   └── visualization.py        # All analysis visualizations
├── notebooks/
└── requirements.txt
```

## Quick Start

```bash
pip install -r requirements.txt
python run_gs_pipeline.py
```

## Output

- `results/` — Analysis outputs including:
  - PCA population structure scatter & scree plots
  - GRM heatmap sorted by sub-population
  - Heritability estimate bar chart across traits
  - GEBV distribution plots with selection thresholds
  - Prediction accuracy box plots (cross-validation)
  - Marker effect Manhattan-style plots
  - `cv_results.csv` — Detailed cross-validation results

## Key Quantitative Genetics Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| Genomic Relationship Matrix (GRM) | VanRaden Method 1 |
| BLUP Breeding Values | Henderson's Mixed Model Equations |
| Heritability (h²) | Haseman-Elston regression |
| Population Structure | PCA + Fst (Nei's) |
| Genomic Selection | rrBLUP, LASSO, Elastic Net |
| Model Validation | K-fold cross-validation |
| Multi-trait Selection | Weighted selection index on standardized GEBVs |

## Relevance to Breeding Operations

This pipeline demonstrates the ability to develop and apply molecular breeding tools — from processing SNP genotyping data through to building predictive models that support crossing decisions and early-stage selection. Directly relevant to genomic selection pipeline development in subtropical perennial crop breeding.
