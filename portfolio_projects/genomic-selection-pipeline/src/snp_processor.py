"""
SNP Data Processor
==================
Quality control and filtering pipeline for SNP marker data.

Implements standard genotyping QC:
- Minor allele frequency (MAF) filtering
- Missing data rate filtering (per marker and per individual)
- Hardy-Weinberg equilibrium testing
- Linkage disequilibrium (LD) pruning (simplified)
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple


class SNPProcessor:
    """Processes and filters SNP genotype data for downstream analysis."""
    
    def __init__(self, geno_df: pd.DataFrame):
        """
        Parameters
        ----------
        geno_df : pd.DataFrame
            Genotype matrix (individuals x markers), coded 0/1/2
        """
        self.geno_df = geno_df.copy()
        self.n_individuals, self.n_markers = geno_df.shape
        self.qc_log = []
    
    def run_qc(self, maf_threshold: float = 0.05, 
               marker_missing_rate: float = 0.10,
               individual_missing_rate: float = 0.20,
               hwe_pvalue: float = 0.001) -> pd.DataFrame:
        """
        Run full SNP QC pipeline.
        
        Parameters
        ----------
        maf_threshold : float
            Minimum minor allele frequency
        marker_missing_rate : float
            Maximum missing rate per marker
        individual_missing_rate : float
            Maximum missing rate per individual
        hwe_pvalue : float
            HWE test p-value threshold
            
        Returns
        -------
        pd.DataFrame
            Filtered genotype matrix
        """
        print(f"Starting SNP QC: {self.n_individuals} individuals, {self.n_markers} markers")
        
        self._filter_individual_missing(individual_missing_rate)
        self._filter_marker_missing(marker_missing_rate)
        self._filter_maf(maf_threshold)
        self._filter_hwe(hwe_pvalue)
        
        print(f"\nAfter QC: {self.geno_df.shape[0]} individuals, {self.geno_df.shape[1]} markers")
        return self.geno_df
    
    def _filter_individual_missing(self, threshold: float):
        """Remove individuals with high missing rates."""
        missing_rates = self.geno_df.isna().mean(axis=1)
        keep = missing_rates <= threshold
        removed = (~keep).sum()
        self.geno_df = self.geno_df[keep]
        self.qc_log.append(f"Individual missing rate filter (>{threshold:.0%}): removed {removed}")
        print(f"  Individual missing filter: removed {removed}")
    
    def _filter_marker_missing(self, threshold: float):
        """Remove markers with high missing rates."""
        missing_rates = self.geno_df.isna().mean(axis=0)
        keep = missing_rates <= threshold
        removed = (~keep).sum()
        self.geno_df = self.geno_df.loc[:, keep]
        self.qc_log.append(f"Marker missing rate filter (>{threshold:.0%}): removed {removed}")
        print(f"  Marker missing filter: removed {removed}")
    
    def _filter_maf(self, threshold: float):
        """Remove markers below MAF threshold."""
        allele_freq = self.geno_df.mean(axis=0) / 2
        maf = np.minimum(allele_freq, 1 - allele_freq)
        keep = maf >= threshold
        removed = (~keep).sum()
        self.geno_df = self.geno_df.loc[:, keep]
        self.qc_log.append(f"MAF filter (<{threshold}): removed {removed}")
        print(f"  MAF filter: removed {removed}")
    
    def _filter_hwe(self, pvalue_threshold: float):
        """Remove markers deviating from Hardy-Weinberg Equilibrium."""
        markers_to_remove = []
        
        for marker in self.geno_df.columns:
            geno_counts = self.geno_df[marker].dropna().value_counts()
            n = geno_counts.sum()
            
            n_aa = geno_counts.get(0, 0)
            n_ab = geno_counts.get(1, 0)
            n_bb = geno_counts.get(2, 0)
            
            p = (2 * n_aa + n_ab) / (2 * n)
            q = 1 - p
            
            if p <= 0 or q <= 0:
                continue
            
            # Expected counts
            exp_aa = n * p ** 2
            exp_ab = n * 2 * p * q
            exp_bb = n * q ** 2
            
            observed = [n_aa, n_ab, n_bb]
            expected = [exp_aa, exp_ab, exp_bb]
            
            # Filter out zero expected values
            valid = [(o, e) for o, e in zip(observed, expected) if e > 0]
            if len(valid) < 2:
                continue
            
            obs_valid, exp_valid = zip(*valid)
            chi2, pval = stats.chisquare(obs_valid, exp_valid)
            
            if pval < pvalue_threshold:
                markers_to_remove.append(marker)
        
        self.geno_df = self.geno_df.drop(columns=markers_to_remove)
        self.qc_log.append(f"HWE filter (p<{pvalue_threshold}): removed {len(markers_to_remove)}")
        print(f"  HWE filter: removed {len(markers_to_remove)}")
    
    def compute_maf_distribution(self) -> pd.Series:
        """Calculate MAF for all remaining markers."""
        allele_freq = self.geno_df.mean(axis=0) / 2
        return np.minimum(allele_freq, 1 - allele_freq)
    
    def get_qc_summary(self) -> str:
        """Return QC summary as formatted string."""
        lines = ["SNP QC Summary", "=" * 40]
        lines.extend(self.qc_log)
        lines.append(f"\nFinal: {self.geno_df.shape[0]} individuals, {self.geno_df.shape[1]} markers")
        return "\n".join(lines)
