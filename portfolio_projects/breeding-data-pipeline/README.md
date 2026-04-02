# Breeding Data Pipeline

An end-to-end ETL pipeline for managing phenotypic and agronomic data from subtropical fruit (mango & citrus) breeding trials across multiple sites and seasons.

## Problem Addressed

Breeding programs generate large volumes of field trial data across multiple sites, seasons, and evaluators. Ensuring data quality, consistency, and accessibility is critical for making informed selection decisions. This pipeline automates the ingestion, validation, transformation, and storage of breeding trial data.

## Key Features

- **Multi-source data ingestion** — Reads CSV files from field data collection across sites and seasons
- **Comprehensive QA/QC validation** — Range checks, outlier detection (IQR), missing data analysis, evaluator bias detection, and cross-field consistency checks
- **Data transformation** — Outlier capping, derived trait computation (shape index, yield efficiency, Brix/acid ratio), genotype-level aggregation
- **SQLite database** — Normalized relational schema for multi-year trial data with full audit trail
- **Automated reporting** — QA/QC reports with publication-quality visualizations: missing data heatmaps, trait distributions, site comparisons, evaluator scoring analysis

## Architecture

```
Raw CSVs → Ingestion → Standardization → QA/QC Validation → Transformation → SQLite DB → Reports
```

## Technologies

- **Python** (pandas, numpy, scipy)
- **SQLite** with SQLAlchemy-compatible schema
- **matplotlib / seaborn** for QA/QC visualizations
- **PyYAML** for configurable pipeline parameters
- **pytest** for unit testing

## Project Structure

```
breeding-data-pipeline/
├── run_pipeline.py           # Main entry point
├── config/
│   └── pipeline_config.yaml  # Configurable validation rules and thresholds
├── src/
│   ├── data_generator.py     # Synthetic data with realistic trait distributions
│   ├── ingestion.py          # Multi-file ingestion and deduplication
│   ├── validation.py         # Comprehensive QA/QC validation engine
│   ├── transformation.py     # Cleaning, derived traits, aggregation
│   ├── database.py           # SQLite schema and data management
│   └── reports.py            # QA/QC visualization and reporting
├── tests/
│   ├── test_validation.py    # Validation module tests
│   └── test_transformation.py # Transformation module tests
└── requirements.txt
```

## Quick Start

```bash
pip install -r requirements.txt
python run_pipeline.py --generate-data
```

## Output

- `data/breeding_trials.db` — SQLite database with all trial records
- `reports/` — QA/QC reports including:
  - Missing data heatmaps by site-season
  - Trait distribution box plots
  - Site-to-site genotype correlation scatter plots
  - QC status summaries (pass/warn/fail)
  - Evaluator scoring comparison violin plots

## Relevance to Breeding Operations

This pipeline demonstrates skills directly applicable to managing breeding database systems in a subtropical crops program — handling phenotypic data collection workflows, implementing standardized QA/QC protocols, and producing breeder-friendly reports that flag data quality issues before they impact selection decisions.
