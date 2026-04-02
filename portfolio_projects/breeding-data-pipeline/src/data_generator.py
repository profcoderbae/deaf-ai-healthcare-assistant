"""
Synthetic Data Generator for Subtropical Breeding Trials
========================================================
Generates realistic phenotypic and agronomic data for mango and citrus
breeding trials across multiple sites, seasons, and genotypes.
Used for pipeline development and demonstration purposes.
"""

import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta


def generate_genotype_ids(crop: str, n_genotypes: int) -> list:
    """Generate realistic breeding program genotype identifiers."""
    prefix = "MNG" if crop == "mango" else "CIT"
    crosses = [f"{prefix}-{yr}-{i:04d}" 
               for yr in range(2018, 2024) 
               for i in range(1, n_genotypes // 6 + 2)]
    return crosses[:n_genotypes]


def generate_mango_trial_data(
    n_genotypes: int = 150,
    sites: list = None,
    seasons: list = None,
    reps: int = 3,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic mango breeding trial data with realistic trait
    distributions, site effects, and seasonal variation.
    
    Parameters
    ----------
    n_genotypes : int
        Number of unique genotypes in the trial
    sites : list
        Trial site names
    seasons : list
        Growing seasons
    reps : int
        Number of replications per genotype per site
    seed : int
        Random seed for reproducibility
    """
    rng = np.random.default_rng(seed)
    sites = sites or ["Hoedspruit_A", "Hoedspruit_B", "Tzaneen_C"]
    seasons = seasons or ["2023-2024", "2024-2025", "2025-2026"]
    
    genotype_ids = generate_genotype_ids("mango", n_genotypes)
    
    # Genotype-level breeding values (genetic effects)
    genotype_effects = {
        gid: {
            "fruit_weight_g": rng.normal(0, 40),
            "brix_content": rng.normal(0, 2),
            "skin_color_score": rng.normal(0, 1.2),
            "flesh_firmness_kg": rng.normal(0, 1.5),
            "disease_resistance_score": rng.normal(0, 1.5),
            "tree_vigor_score": rng.normal(0, 1.0),
            "yield_kg_per_tree": rng.normal(0, 20),
            "days_to_maturity": rng.normal(0, 12),
            "fruit_length_mm": rng.normal(0, 15),
            "fruit_width_mm": rng.normal(0, 10),
        }
        for gid in genotype_ids
    }
    
    # Site effects
    site_effects = {
        "Hoedspruit_A": {"fruit_weight_g": 5, "yield_kg_per_tree": 10, "brix_content": 0.5},
        "Hoedspruit_B": {"fruit_weight_g": -3, "yield_kg_per_tree": -5, "brix_content": -0.3},
        "Tzaneen_C": {"fruit_weight_g": 10, "yield_kg_per_tree": 15, "brix_content": 1.0},
    }
    
    # Season effects
    season_effects = {
        "2023-2024": {"yield_kg_per_tree": -8, "brix_content": 0.3},
        "2024-2025": {"yield_kg_per_tree": 5, "brix_content": -0.2},
        "2025-2026": {"yield_kg_per_tree": 3, "brix_content": 0.1},
    }
    
    # Trait population means and residual SDs
    trait_means = {
        "fruit_weight_g": 350, "brix_content": 16, "skin_color_score": 5.5,
        "flesh_firmness_kg": 4.5, "disease_resistance_score": 5.0,
        "tree_vigor_score": 5.5, "yield_kg_per_tree": 80,
        "days_to_maturity": 140, "fruit_length_mm": 110, "fruit_width_mm": 80,
    }
    residual_sd = {
        "fruit_weight_g": 25, "brix_content": 1.0, "skin_color_score": 0.8,
        "flesh_firmness_kg": 0.8, "disease_resistance_score": 0.9,
        "tree_vigor_score": 0.7, "yield_kg_per_tree": 12,
        "days_to_maturity": 8, "fruit_length_mm": 8, "fruit_width_mm": 6,
    }
    
    records = []
    for season in seasons:
        # Simulate evaluation dates within season
        year = int(season.split("-")[1])
        base_date = datetime(year, 1, 15)
        
        for site in sites:
            for gid in genotype_ids:
                for rep in range(1, reps + 1):
                    # ~5% missing data (tree death, missed evaluation)
                    if rng.random() < 0.05:
                        continue
                    
                    eval_date = base_date + timedelta(days=int(rng.integers(0, 60)))
                    row = {
                        "genotype_id": gid,
                        "crop": "mango",
                        "site": site,
                        "season": season,
                        "rep": rep,
                        "block": f"B{rng.integers(1, 5)}",
                        "row": rng.integers(1, 20),
                        "tree_position": rng.integers(1, 30),
                        "evaluation_date": eval_date.strftime("%Y-%m-%d"),
                        "evaluator": rng.choice(["TM_01", "TM_02", "TM_03", "JN_01"]),
                    }
                    
                    for trait, mean in trait_means.items():
                        g_eff = genotype_effects[gid].get(trait, 0)
                        s_eff = site_effects.get(site, {}).get(trait, 0)
                        sn_eff = season_effects.get(season, {}).get(trait, 0)
                        residual = rng.normal(0, residual_sd[trait])
                        value = mean + g_eff + s_eff + sn_eff + residual
                        
                        # Introduce ~2% trait-level missing values
                        if rng.random() < 0.02:
                            value = np.nan
                        # Introduce ~0.5% outliers (data entry errors)
                        elif rng.random() < 0.005:
                            value = value * rng.choice([0.1, 3.0, -1])
                        
                        row[trait] = round(value, 2)
                    
                    # Integer traits
                    for trait in ["skin_color_score", "disease_resistance_score", "tree_vigor_score"]:
                        if not np.isnan(row[trait]):
                            row[trait] = int(np.clip(round(row[trait]), 1, 9))
                    
                    records.append(row)
    
    return pd.DataFrame(records)


def generate_citrus_trial_data(
    n_genotypes: int = 100,
    sites: list = None,
    seasons: list = None,
    reps: int = 3,
    seed: int = 123
) -> pd.DataFrame:
    """Generate synthetic citrus breeding trial data."""
    rng = np.random.default_rng(seed)
    sites = sites or ["Hoedspruit_A", "Letsitele_D"]
    seasons = seasons or ["2023-2024", "2024-2025", "2025-2026"]
    
    genotype_ids = generate_genotype_ids("citrus", n_genotypes)
    
    trait_means = {
        "fruit_weight_g": 180, "brix_content": 11.5, "acidity_percent": 1.2,
        "juice_content_ml": 85, "rind_thickness_mm": 4.5, "seed_count": 8,
        "yield_kg_per_tree": 120, "days_to_maturity": 240,
    }
    residual_sd = {
        "fruit_weight_g": 20, "brix_content": 1.2, "acidity_percent": 0.3,
        "juice_content_ml": 12, "rind_thickness_mm": 0.8, "seed_count": 3,
        "yield_kg_per_tree": 18, "days_to_maturity": 15,
    }
    
    genotype_effects = {
        gid: {trait: rng.normal(0, sd * 0.6) for trait, sd in residual_sd.items()}
        for gid in genotype_ids
    }
    
    records = []
    for season in seasons:
        year = int(season.split("-")[1])
        base_date = datetime(year, 5, 1)
        
        for site in sites:
            for gid in genotype_ids:
                for rep in range(1, reps + 1):
                    if rng.random() < 0.04:
                        continue
                    
                    eval_date = base_date + timedelta(days=int(rng.integers(0, 45)))
                    row = {
                        "genotype_id": gid,
                        "crop": "citrus",
                        "site": site,
                        "season": season,
                        "rep": rep,
                        "block": f"B{rng.integers(1, 4)}",
                        "row": rng.integers(1, 15),
                        "tree_position": rng.integers(1, 25),
                        "evaluation_date": eval_date.strftime("%Y-%m-%d"),
                        "evaluator": rng.choice(["TM_01", "TM_02", "KM_01"]),
                    }
                    
                    for trait, mean in trait_means.items():
                        g_eff = genotype_effects[gid].get(trait, 0)
                        residual = rng.normal(0, residual_sd[trait])
                        value = mean + g_eff + residual
                        
                        if rng.random() < 0.02:
                            value = np.nan
                        elif rng.random() < 0.005:
                            value = value * rng.choice([0.1, 2.5])
                        
                        row[trait] = round(value, 2)
                    
                    if not np.isnan(row.get("seed_count", np.nan)):
                        row["seed_count"] = max(0, int(round(row["seed_count"])))
                    
                    records.append(row)
    
    return pd.DataFrame(records)


def save_raw_data(output_dir: str = "data/raw"):
    """Generate and save raw trial CSV files simulating field data collection."""
    os.makedirs(output_dir, exist_ok=True)
    
    mango_df = generate_mango_trial_data()
    citrus_df = generate_citrus_trial_data()
    
    # Save by crop and season (as would come from field)
    for season in mango_df["season"].unique():
        subset = mango_df[mango_df["season"] == season]
        fname = f"mango_trials_{season.replace('-', '_')}.csv"
        subset.to_csv(os.path.join(output_dir, fname), index=False)
        print(f"  Saved {fname}: {len(subset)} records")
    
    for season in citrus_df["season"].unique():
        subset = citrus_df[citrus_df["season"] == season]
        fname = f"citrus_trials_{season.replace('-', '_')}.csv"
        subset.to_csv(os.path.join(output_dir, fname), index=False)
        print(f"  Saved {fname}: {len(subset)} records")
    
    return mango_df, citrus_df


if __name__ == "__main__":
    print("Generating synthetic breeding trial data...")
    save_raw_data()
    print("Done.")
