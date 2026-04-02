"""
Trial Data Generator & Loader
==============================
Generates sample subtropical breeding trial data and provides
loading utilities for the Streamlit dashboard.
"""

import numpy as np
import pandas as pd
import os


def generate_dashboard_data(output_dir: str = "data") -> pd.DataFrame:
    """
    Generate comprehensive mango breeding trial data for dashboard demo.
    Includes multi-year, multi-site data with realistic trait distributions.
    """
    rng = np.random.default_rng(42)
    os.makedirs(output_dir, exist_ok=True)
    
    n_genotypes = 200
    genotype_ids = [f"MNG-{2018 + i // 40}-{i % 40 + 1:04d}" for i in range(n_genotypes)]
    sites = ["Hoedspruit_A", "Hoedspruit_B", "Tzaneen_C"]
    seasons = ["2022-2023", "2023-2024", "2024-2025", "2025-2026"]
    
    # Cross/pedigree info
    families = [f"Cross_{i:02d}" for i in range(1, 21)]
    genotype_family = {gid: rng.choice(families) for gid in genotype_ids}
    
    # Advancement stage
    stages = ["Seedling", "Phase_1", "Phase_2", "Advanced", "Elite"]
    stage_weights = [0.3, 0.3, 0.2, 0.15, 0.05]
    genotype_stage = {gid: rng.choice(stages, p=stage_weights) for gid in genotype_ids}
    
    # Genotype breeding values
    genotype_effects = {
        gid: {
            "fruit_weight_g": rng.normal(0, 35),
            "brix_content": rng.normal(0, 1.8),
            "skin_color_score": rng.normal(0, 1.0),
            "flesh_firmness_kg": rng.normal(0, 1.2),
            "disease_resistance": rng.normal(0, 1.3),
            "tree_vigor": rng.normal(0, 0.9),
            "yield_kg": rng.normal(0, 18),
            "fruit_length_mm": rng.normal(0, 12),
            "fruit_width_mm": rng.normal(0, 8),
            "shelf_life_days": rng.normal(0, 2),
        }
        for gid in genotype_ids
    }
    
    trait_means = {
        "fruit_weight_g": 340, "brix_content": 15.5, "skin_color_score": 5.5,
        "flesh_firmness_kg": 4.2, "disease_resistance": 5.0, "tree_vigor": 5.5,
        "yield_kg": 75, "fruit_length_mm": 108, "fruit_width_mm": 78,
        "shelf_life_days": 14,
    }
    trait_sd = {
        "fruit_weight_g": 22, "brix_content": 0.9, "skin_color_score": 0.7,
        "flesh_firmness_kg": 0.7, "disease_resistance": 0.8, "tree_vigor": 0.6,
        "yield_kg": 10, "fruit_length_mm": 7, "fruit_width_mm": 5,
        "shelf_life_days": 1.5,
    }
    
    records = []
    for season in seasons:
        # Not all genotypes evaluated every season
        season_genotypes = rng.choice(genotype_ids, 
                                       size=int(n_genotypes * rng.uniform(0.7, 0.95)),
                                       replace=False)
        for site in sites:
            for gid in season_genotypes:
                for rep in range(1, rng.integers(2, 4) + 1):
                    if rng.random() < 0.03:
                        continue
                    
                    row = {
                        "genotype_id": gid,
                        "family": genotype_family[gid],
                        "stage": genotype_stage[gid],
                        "site": site,
                        "season": season,
                        "rep": rep,
                    }
                    
                    for trait, mean in trait_means.items():
                        g_eff = genotype_effects[gid][trait]
                        residual = rng.normal(0, trait_sd[trait])
                        value = mean + g_eff + residual
                        
                        if rng.random() < 0.02:
                            value = np.nan
                        
                        row[trait] = round(value, 2)
                    
                    # Integer scores
                    for score_trait in ["skin_color_score", "disease_resistance", "tree_vigor"]:
                        if pd.notna(row[score_trait]):
                            row[score_trait] = int(np.clip(round(row[score_trait]), 1, 9))
                    
                    records.append(row)
    
    df = pd.DataFrame(records)
    
    # Add derived traits
    mask = df["fruit_length_mm"].notna() & df["fruit_width_mm"].notna()
    df.loc[mask, "shape_index"] = round(
        df.loc[mask, "fruit_length_mm"] / df.loc[mask, "fruit_width_mm"], 2
    )
    
    # Save
    df.to_csv(os.path.join(output_dir, "mango_trial_data.csv"), index=False)
    print(f"Generated {len(df)} records for {df['genotype_id'].nunique()} genotypes")
    
    return df


def load_trial_data(data_path: str = "data/mango_trial_data.csv") -> pd.DataFrame:
    """Load trial data, generating it if it doesn't exist."""
    if not os.path.exists(data_path):
        print("Generating sample data...")
        return generate_dashboard_data()
    return pd.read_csv(data_path)


if __name__ == "__main__":
    generate_dashboard_data()
