"""Tests for the data transformation module."""

import numpy as np
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.transformation import (
    cap_outliers, compute_derived_traits, 
    aggregate_to_genotype_means, normalize_traits
)


@pytest.fixture
def sample_data():
    """Create sample trial data."""
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "genotype_id": np.repeat([f"MNG-2020-{i:04d}" for i in range(50)], 4),
        "crop": "mango",
        "site": np.tile(["Hoedspruit_A", "Hoedspruit_B"], n // 2),
        "season": np.tile(["2024-2025", "2024-2025", "2025-2026", "2025-2026"], n // 4),
        "rep": np.random.choice([1, 2, 3], n),
        "fruit_weight_g": np.random.normal(350, 40, n),
        "brix_content": np.random.normal(16, 2, n),
        "fruit_length_mm": np.random.normal(110, 15, n),
        "fruit_width_mm": np.random.normal(80, 10, n),
        "yield_kg_per_tree": np.random.normal(80, 15, n),
        "tree_vigor_score": np.random.choice(range(3, 8), n).astype(float),
    })


def test_cap_outliers_reduces_extreme_values(sample_data):
    """Outlier capping should bring extreme values within bounds."""
    sample_data.loc[0, "fruit_weight_g"] = 800  # Extreme high
    sample_data.loc[1, "fruit_weight_g"] = 50   # Extreme low
    
    result = cap_outliers(sample_data, ["fruit_weight_g"], multiplier=2.5)
    
    assert result.loc[0, "fruit_weight_g"] < 800
    assert result.loc[1, "fruit_weight_g"] > 50


def test_derived_traits_computed(sample_data):
    """Derived traits should be calculated correctly."""
    result = compute_derived_traits(sample_data)
    
    assert "fruit_shape_index" in result.columns
    assert "yield_efficiency" in result.columns
    
    # Shape index = length / width
    expected = sample_data["fruit_length_mm"].iloc[0] / sample_data["fruit_width_mm"].iloc[0]
    assert abs(result["fruit_shape_index"].iloc[0] - expected) < 0.001


def test_aggregation_produces_genotype_means(sample_data):
    """Aggregation should produce one row per genotype-site-season."""
    traits = ["fruit_weight_g", "brix_content"]
    result = aggregate_to_genotype_means(sample_data, traits)
    
    assert len(result) <= len(sample_data)
    assert "genotype_id" in result.columns
    assert "fruit_weight_g_mean" in result.columns
    assert "fruit_weight_g_std" in result.columns


def test_normalization_zscore(sample_data):
    """Z-score normalization should produce mean ~0, std ~1."""
    result = normalize_traits(sample_data, ["fruit_weight_g"], method="zscore")
    
    assert "fruit_weight_g_normalized" in result.columns
    assert abs(result["fruit_weight_g_normalized"].mean()) < 0.1
    assert abs(result["fruit_weight_g_normalized"].std() - 1.0) < 0.1


def test_normalization_minmax(sample_data):
    """Min-max normalization should produce values in [0, 1]."""
    result = normalize_traits(sample_data, ["fruit_weight_g"], method="minmax")
    
    assert result["fruit_weight_g_normalized"].min() >= 0
    assert result["fruit_weight_g_normalized"].max() <= 1.0
