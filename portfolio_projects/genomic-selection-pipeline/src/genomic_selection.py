"""
Genomic Selection Module
========================
Training and evaluation of genomic prediction models for subtropical
fruit breeding. Implements multiple GS methods:

- GBLUP (Genomic BLUP): Ridge regression equivalent using GRM
- Ridge Regression BLUP (rrBLUP): Shrinkage-based marker effect estimation
- LASSO: Sparse marker effect estimation
- Elastic Net: Combined L1/L2 regularization

Includes cross-validation framework for model comparison and
prediction accuracy assessment.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats


class GenomicSelectionModel:
    """Train and evaluate genomic prediction models."""
    
    def __init__(self, geno_matrix: np.ndarray, phenotypes: np.ndarray,
                 individual_ids: list = None):
        """
        Parameters
        ----------
        geno_matrix : np.ndarray
            Marker matrix (n x p), coded 0/1/2
        phenotypes : np.ndarray
            Phenotype vector (n,)
        individual_ids : list
            Individual identifiers
        """
        # Remove individuals with missing phenotypes
        valid = ~np.isnan(phenotypes)
        self.X = geno_matrix[valid]
        self.y = phenotypes[valid]
        self.ids = (np.array(individual_ids)[valid] if individual_ids 
                    else np.arange(valid.sum()))
        
        self.n, self.p = self.X.shape
        self.scaler = StandardScaler()
        self.X_scaled = self.scaler.fit_transform(self.X)
        
        self.models = {}
        self.results = {}
    
    def train_rrblup(self, alpha: float = 1.0) -> dict:
        """
        Train Ridge Regression BLUP (rrBLUP) model.
        
        Equivalent to GBLUP when alpha = sigma_e² / sigma_a².
        Estimates marker effects with uniform shrinkage.
        """
        model = Ridge(alpha=alpha, fit_intercept=True)
        model.fit(self.X_scaled, self.y)
        
        predictions = model.predict(self.X_scaled)
        
        self.models["rrBLUP"] = model
        result = {
            "method": "rrBLUP (Ridge Regression)",
            "alpha": alpha,
            "r2_training": round(r2_score(self.y, predictions), 4),
            "rmse_training": round(np.sqrt(mean_squared_error(self.y, predictions)), 4),
            "correlation": round(float(np.corrcoef(self.y, predictions)[0, 1]), 4),
        }
        self.results["rrBLUP"] = result
        return result
    
    def train_lasso(self, alpha: float = 0.1) -> dict:
        """
        Train LASSO model for sparse marker effect estimation.
        
        Assumes few markers have large effects (variable selection).
        """
        model = Lasso(alpha=alpha, fit_intercept=True, max_iter=5000)
        model.fit(self.X_scaled, self.y)
        
        predictions = model.predict(self.X_scaled)
        n_nonzero = np.sum(model.coef_ != 0)
        
        self.models["LASSO"] = model
        result = {
            "method": "LASSO",
            "alpha": alpha,
            "n_nonzero_markers": int(n_nonzero),
            "pct_markers_selected": round(n_nonzero / self.p * 100, 1),
            "r2_training": round(r2_score(self.y, predictions), 4),
            "rmse_training": round(np.sqrt(mean_squared_error(self.y, predictions)), 4),
            "correlation": round(float(np.corrcoef(self.y, predictions)[0, 1]), 4),
        }
        self.results["LASSO"] = result
        return result
    
    def train_elastic_net(self, alpha: float = 0.1, l1_ratio: float = 0.5) -> dict:
        """
        Train Elastic Net model (combined L1 + L2 regularization).
        
        Balances between ridge (uniform shrinkage) and LASSO (variable selection).
        """
        model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, 
                           fit_intercept=True, max_iter=5000)
        model.fit(self.X_scaled, self.y)
        
        predictions = model.predict(self.X_scaled)
        n_nonzero = np.sum(model.coef_ != 0)
        
        self.models["ElasticNet"] = model
        result = {
            "method": "Elastic Net",
            "alpha": alpha,
            "l1_ratio": l1_ratio,
            "n_nonzero_markers": int(n_nonzero),
            "r2_training": round(r2_score(self.y, predictions), 4),
            "rmse_training": round(np.sqrt(mean_squared_error(self.y, predictions)), 4),
            "correlation": round(float(np.corrcoef(self.y, predictions)[0, 1]), 4),
        }
        self.results["ElasticNet"] = result
        return result
    
    def cross_validate(self, n_folds: int = 5, seed: int = 42) -> pd.DataFrame:
        """
        K-fold cross-validation for all trained models.
        
        Reports prediction accuracy as Pearson correlation between
        predicted and observed values in held-out folds.
        
        Parameters
        ----------
        n_folds : int
            Number of CV folds
        seed : int
            Random seed for reproducibility
            
        Returns
        -------
        pd.DataFrame
            CV results per model and fold
        """
        kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
        
        cv_results = []
        
        for model_name, model_template in [
            ("rrBLUP", Ridge(alpha=1.0)),
            ("LASSO", Lasso(alpha=0.1, max_iter=5000)),
            ("ElasticNet", ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=5000)),
        ]:
            fold_correlations = []
            
            for fold, (train_idx, test_idx) in enumerate(kf.split(self.X_scaled)):
                X_train = self.X_scaled[train_idx]
                X_test = self.X_scaled[test_idx]
                y_train = self.y[train_idx]
                y_test = self.y[test_idx]
                
                model = type(model_template)(**model_template.get_params())
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                corr = np.corrcoef(y_test, y_pred)[0, 1] if len(y_test) > 1 else np.nan
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                
                cv_results.append({
                    "model": model_name,
                    "fold": fold + 1,
                    "correlation": round(float(corr), 4),
                    "rmse": round(float(rmse), 4),
                    "n_train": len(train_idx),
                    "n_test": len(test_idx),
                })
                fold_correlations.append(corr)
            
            mean_corr = np.mean(fold_correlations)
            print(f"  {model_name}: mean prediction accuracy (r) = {mean_corr:.4f}")
        
        return pd.DataFrame(cv_results)
    
    def get_marker_effects(self, model_name: str) -> pd.DataFrame:
        """
        Extract marker effect estimates from a trained model.
        
        Returns markers sorted by absolute effect size.
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not trained yet.")
        
        model = self.models[model_name]
        effects = model.coef_
        
        effects_df = pd.DataFrame({
            "marker_index": range(len(effects)),
            "effect": effects,
            "abs_effect": np.abs(effects),
        })
        
        return effects_df.sort_values("abs_effect", ascending=False).reset_index(drop=True)
    
    def compare_models(self) -> pd.DataFrame:
        """Compare all trained models side by side."""
        if not self.results:
            raise ValueError("No models trained yet.")
        
        comparison = []
        for name, result in self.results.items():
            comparison.append({
                "Model": result["method"],
                "R² (training)": result["r2_training"],
                "RMSE (training)": result["rmse_training"],
                "Correlation": result["correlation"],
            })
        
        return pd.DataFrame(comparison)
