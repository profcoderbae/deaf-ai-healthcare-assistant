"""Tests for the data validation module."""

import numpy as np
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.validation import BreedingDataValidator


@pytest.fixture
def sample_data():
    """Create a small sample dataset for testing."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "genotype_id": [f"MNG-2020-{i:04d}" for i in range(n)],
        "crop": "mango",
        "site": np.random.choice(["Hoedspruit_A", "Hoedspruit_B"], n),
        "season": "2024-2025",
        "rep": np.random.choice([1, 2, 3], n),
        "evaluator": np.random.choice(["TM_01", "TM_02"], n),
        "evaluation_date": "2025-02-15",
        "fruit_weight_g": np.random.normal(350, 40, n),
        "brix_content": np.random.normal(16, 2, n),
        "skin_color_score": np.random.choice(range(1, 10), n),
        "yield_kg_per_tree": np.random.normal(80, 15, n),
    })


@pytest.fixture
def validator(tmp_path):
    """Create a validator with a test config."""
    config_content = """
validation:
  missing_threshold: 0.15
  outlier_method: iqr
  outlier_multiplier: 2.5
  range_checks:
    fruit_weight_g: [50, 2000]
    brix_content: [5, 30]
    skin_color_score: [1, 9]
    yield_kg_per_tree: [0, 500]
"""
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(config_content)
    return BreedingDataValidator(config_path=str(config_path))


def test_validation_returns_qc_columns(validator, sample_data):
    """Validate that QC columns are added to the DataFrame."""
    result = validator.validate(sample_data)
    assert "_qc_flags" in result.columns
    assert "_qc_status" in result.columns


def test_valid_data_passes(validator, sample_data):
    """Clean data should mostly pass validation."""
    result = validator.validate(sample_data)
    pass_rate = (result["_qc_status"] == "PASS").mean()
    assert pass_rate > 0.8


def test_range_violations_detected(validator, sample_data):
    """Records with out-of-range values should be flagged."""
    sample_data.loc[0, "fruit_weight_g"] = -100  # Below range
    sample_data.loc[1, "fruit_weight_g"] = 5000  # Above range
    
    result = validator.validate(sample_data)
    
    assert result.loc[0, "_qc_status"] == "FAIL"
    assert result.loc[1, "_qc_status"] == "FAIL"


def test_missing_data_flagged(validator, sample_data):
    """High missing data rates should generate issues."""
    # Set 30% of brix values to NaN (exceeds 15% threshold)
    mask = np.random.choice(len(sample_data), size=30, replace=False)
    sample_data.loc[mask, "brix_content"] = np.nan
    
    validator.validate(sample_data)
    issues = validator.get_issues_dataframe()
    
    missing_issues = issues[issues["check"] == "missing_data"]
    assert len(missing_issues) > 0


def test_issues_dataframe_structure(validator, sample_data):
    """Issues DataFrame should have expected columns."""
    validator.validate(sample_data)
    issues = validator.get_issues_dataframe()
    
    assert "check" in issues.columns
    assert "severity" in issues.columns
    assert "detail" in issues.columns
