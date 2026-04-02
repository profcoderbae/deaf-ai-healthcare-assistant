# Field Trial Analytics Dashboard

An interactive Streamlit dashboard for subtropical mango breeding trial analytics, providing breeder-friendly visualizations, multi-trait selection tools, and GxE stability analysis.

## Problem Addressed

Breeders need intuitive, interactive tools to explore multi-year, multi-site trial data and make selection decisions. Static reports and spreadsheets don't scale to the complexity of modern breeding programs with hundreds of genotypes evaluated across environments. This dashboard translates analytics into actionable, breeder-friendly insights.

## Key Features

- **Trial Overview** — Dataset completeness, missing data heatmaps, stage distribution
- **Genotype Performance** — Ranking, trait distributions by site, phenotypic correlations, site-vs-site scatter plots
- **Family Analysis** — Cross/family performance summaries, advancement stage trait progression
- **GxE Stability** — Finlay-Wilkinson regression for genotype stability across environments
- **Interactive Selection Tool** — Customizable multi-trait selection index with adjustable weights, selection gain visualization, and CSV export

## Dashboard Pages

### 1. Overview
High-level summary: record counts, genotype/site/season breakdowns, missing data rates, pipeline stage distributions.

### 2. Genotype Performance  
Rank genotypes by any trait, view distributions by site, explore trait correlations, and compare site performance with scatter plots.

### 3. Family Analysis
Evaluate which crosses produced the best offspring, track trait improvement through advancement stages (Seedling → Elite).

### 4. GxE Stability
Finlay-Wilkinson regression plots showing mean performance vs. stability — identify genotypes that perform well AND consistently.

### 5. Selection Tool
Interactive multi-trait selection with sliders for weights on each trait. Visualize selection gain over population mean and download selection lists.

## Technologies

- **Streamlit** for interactive web dashboard
- **Plotly** for interactive visualizations
- **Python** (pandas, numpy, scipy)

## Project Structure

```
field-trial-dashboard/
├── run_dashboard.py        # Launcher (generate data + start Streamlit)
├── src/
│   ├── data_loader.py      # Data generation and loading
│   ├── trial_analysis.py   # Statistical analysis functions
│   └── dashboard.py        # Streamlit dashboard application
└── requirements.txt
```

## Quick Start

```bash
pip install -r requirements.txt
python run_dashboard.py
# Opens at http://localhost:8501
```

Or generate data only:
```bash
python run_dashboard.py --data-only
```

## Relevance to Breeding Operations

This dashboard demonstrates the ability to produce regular summaries, reports, and interactive visualizations that help breeders understand trial performance and make advancement/selection decisions. The multi-trait selection tool with customizable weights directly supports the kind of breeder-analytics collaboration required in a subtropical breeding program.
