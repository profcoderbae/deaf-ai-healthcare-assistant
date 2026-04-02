"""
QA/QC Reporting Module
======================
Generates QA/QC reports with visualizations for breeding trial data.
Produces summary dashboards highlighting data quality issues,
trait distributions, and site-season comparisons.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


class QAQCReporter:
    """Generates QA/QC reports and visualizations for breeder review."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate_full_report(self, df: pd.DataFrame, issues_df: pd.DataFrame,
                              crop: str = "all"):
        """Generate a complete QA/QC report with all visualizations."""
        print(f"\nGenerating QA/QC report for {crop}...")
        
        crop_df = df if crop == "all" else df[df["crop"] == crop]
        
        self._plot_missing_data_heatmap(crop_df, crop)
        self._plot_trait_distributions(crop_df, crop)
        self._plot_site_comparison(crop_df, crop)
        self._plot_qc_status_summary(crop_df, crop)
        self._plot_evaluator_comparison(crop_df, crop)
        self._generate_text_report(crop_df, issues_df, crop)
        
        print(f"  Reports saved to {self.output_dir}/")
    
    def _plot_missing_data_heatmap(self, df: pd.DataFrame, crop: str):
        """Heatmap of missing data rates by trait and site-season."""
        trait_cols = self._get_trait_columns(df)
        if not trait_cols:
            return
        
        # Missing rate by site-season
        groups = df.groupby(["site", "season"])
        missing_rates = groups[trait_cols].apply(lambda x: x.isna().mean())
        
        if missing_rates.empty:
            return
        
        fig, ax = plt.subplots(figsize=(14, max(6, len(missing_rates) * 0.5)))
        sns.heatmap(
            missing_rates, annot=True, fmt=".1%", cmap="YlOrRd",
            vmin=0, vmax=0.3, ax=ax, linewidths=0.5
        )
        ax.set_title(f"Missing Data Rate by Site-Season — {crop.title()}", fontsize=14)
        ax.set_ylabel("Site / Season")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"missing_data_{crop}_{self.timestamp}.png"), dpi=150)
        plt.close()
    
    def _plot_trait_distributions(self, df: pd.DataFrame, crop: str):
        """Box plots of key traits across sites."""
        trait_cols = self._get_trait_columns(df)[:8]  # Limit to first 8 traits
        if not trait_cols:
            return
        
        n_traits = len(trait_cols)
        n_cols = 4
        n_rows = (n_traits + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
        axes = axes.flatten() if n_rows * n_cols > 1 else [axes]
        
        for i, trait in enumerate(trait_cols):
            ax = axes[i]
            data = df[["site", trait]].dropna()
            if data.empty:
                continue
            sns.boxplot(data=data, x="site", y=trait, ax=ax, palette="Set2")
            ax.set_title(trait.replace("_", " ").title(), fontsize=11)
            ax.tick_params(axis="x", rotation=30)
        
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
        
        fig.suptitle(f"Trait Distributions by Site — {crop.title()}", fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"trait_distributions_{crop}_{self.timestamp}.png"), 
                     dpi=150, bbox_inches="tight")
        plt.close()
    
    def _plot_site_comparison(self, df: pd.DataFrame, crop: str):
        """Scatter plot comparing trait means across sites."""
        trait_cols = self._get_trait_columns(df)
        if len(df["site"].unique()) < 2 or not trait_cols:
            return
        
        # Compare first two sites
        sites = sorted(df["site"].unique())[:2]
        
        means = df.groupby(["genotype_id", "site"])[trait_cols].mean()
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for i, trait in enumerate(trait_cols[:6]):
            ax = axes[i]
            try:
                site1_vals = means.xs(sites[0], level="site")[trait]
                site2_vals = means.xs(sites[1], level="site")[trait]
                common = site1_vals.index.intersection(site2_vals.index)
                
                ax.scatter(site1_vals[common], site2_vals[common], alpha=0.4, s=15)
                
                # Add 1:1 line
                lims = [
                    min(site1_vals[common].min(), site2_vals[common].min()),
                    max(site1_vals[common].max(), site2_vals[common].max()),
                ]
                ax.plot(lims, lims, "r--", alpha=0.5)
                
                # Correlation
                corr = site1_vals[common].corr(site2_vals[common])
                ax.set_title(f"{trait.replace('_', ' ').title()} (r={corr:.2f})")
                ax.set_xlabel(sites[0])
                ax.set_ylabel(sites[1])
            except Exception:
                ax.set_visible(False)
        
        fig.suptitle(f"Genotype Performance: {sites[0]} vs {sites[1]} — {crop.title()}", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"site_comparison_{crop}_{self.timestamp}.png"), 
                     dpi=150, bbox_inches="tight")
        plt.close()
    
    def _plot_qc_status_summary(self, df: pd.DataFrame, crop: str):
        """Pie chart and bar chart of QC status distribution."""
        if "_qc_status" not in df.columns:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Pie chart
        status_counts = df["_qc_status"].value_counts()
        colors = {"PASS": "#2ecc71", "WARNING": "#f39c12", "FAIL": "#e74c3c"}
        ax1.pie(
            status_counts.values,
            labels=status_counts.index,
            autopct="%1.1f%%",
            colors=[colors.get(s, "#95a5a6") for s in status_counts.index],
            startangle=90
        )
        ax1.set_title("Overall QC Status Distribution")
        
        # Bar chart by site
        status_by_site = df.groupby(["site", "_qc_status"]).size().unstack(fill_value=0)
        status_by_site.plot(kind="bar", stacked=True, ax=ax2,
                           color=[colors.get(c, "#95a5a6") for c in status_by_site.columns])
        ax2.set_title("QC Status by Site")
        ax2.set_ylabel("Number of Records")
        ax2.tick_params(axis="x", rotation=30)
        ax2.legend(title="Status")
        
        fig.suptitle(f"Data Quality Summary — {crop.title()}", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"qc_summary_{crop}_{self.timestamp}.png"), dpi=150)
        plt.close()
    
    def _plot_evaluator_comparison(self, df: pd.DataFrame, crop: str):
        """Compare scoring patterns across evaluators."""
        if "evaluator" not in df.columns:
            return
        
        score_cols = [c for c in df.columns if "score" in c]
        if not score_cols:
            return
        
        fig, axes = plt.subplots(1, len(score_cols), figsize=(7 * len(score_cols), 5))
        if len(score_cols) == 1:
            axes = [axes]
        
        for ax, trait in zip(axes, score_cols):
            data = df[["evaluator", trait]].dropna()
            sns.violinplot(data=data, x="evaluator", y=trait, ax=ax, palette="muted")
            ax.set_title(trait.replace("_", " ").title())
        
        fig.suptitle(f"Evaluator Scoring Comparison — {crop.title()}", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"evaluator_comparison_{crop}_{self.timestamp}.png"), dpi=150)
        plt.close()
    
    def _generate_text_report(self, df: pd.DataFrame, issues_df: pd.DataFrame, crop: str):
        """Generate a text-based QA/QC summary report."""
        report_path = os.path.join(self.output_dir, f"qaqc_report_{crop}_{self.timestamp}.txt")
        
        with open(report_path, "w") as f:
            f.write("=" * 70 + "\n")
            f.write(f"  BREEDING DATA QA/QC REPORT — {crop.upper()}\n")
            f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("DATASET OVERVIEW\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total records:      {len(df):,}\n")
            f.write(f"Unique genotypes:   {df['genotype_id'].nunique():,}\n")
            f.write(f"Sites:              {', '.join(sorted(df['site'].unique()))}\n")
            f.write(f"Seasons:            {', '.join(sorted(df['season'].unique()))}\n")
            
            if "evaluator" in df.columns:
                f.write(f"Evaluators:         {', '.join(sorted(df['evaluator'].unique()))}\n")
            f.write("\n")
            
            if "_qc_status" in df.columns:
                f.write("QC STATUS SUMMARY\n")
                f.write("-" * 40 + "\n")
                for status, count in df["_qc_status"].value_counts().items():
                    pct = count / len(df) * 100
                    f.write(f"  {status:12s}: {count:6,} ({pct:.1f}%)\n")
                f.write("\n")
            
            if not issues_df.empty:
                f.write("VALIDATION ISSUES\n")
                f.write("-" * 40 + "\n")
                for severity in ["CRITICAL", "WARNING", "INFO"]:
                    subset = issues_df[issues_df["severity"] == severity]
                    if not subset.empty:
                        f.write(f"\n  [{severity}] — {len(subset)} issues\n")
                        for _, row in subset.iterrows():
                            f.write(f"    • [{row.get('check', '')}] {row.get('detail', '')}\n")
                f.write("\n")
            
            # Trait summary statistics
            trait_cols = self._get_trait_columns(df)
            if trait_cols:
                f.write("TRAIT SUMMARY STATISTICS\n")
                f.write("-" * 40 + "\n")
                stats = df[trait_cols].describe().T[["count", "mean", "std", "min", "max"]]
                stats["missing_%"] = (1 - stats["count"] / len(df)) * 100
                f.write(stats.to_string())
                f.write("\n")
        
        print(f"  Text report: {report_path}")
    
    def _get_trait_columns(self, df: pd.DataFrame) -> list:
        """Identify numeric trait columns."""
        meta_cols = {
            "genotype_id", "crop", "site", "season", "rep", "block",
            "row", "tree_position", "evaluation_date", "evaluator",
            "source_file", "ingestion_timestamp", "_qc_flags", "_qc_status",
        }
        return [c for c in df.select_dtypes(include=[np.number]).columns 
                if c not in meta_cols]
