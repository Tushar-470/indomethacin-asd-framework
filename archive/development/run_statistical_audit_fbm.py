"""
Comprehensive Statistical Audit of FBM Model in fbm.py
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score, accuracy_score, confusion_matrix,
    brier_score_loss, precision_score, recall_score
)
from sklearn.model_selection import StratifiedKFold, LeaveOneOut

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from asd_mcda.prediction.fbm import FailureBoundaryMap

fbm = FailureBoundaryMap()
X, y, names = fbm.generate_synthetic_doe_dataset()
res = fbm.fit(X, y)

print("=== 1. DATASET DESIGN FORENSICS ===")
print("Factor 1 (polymer_rank):", sorted(list(set(X[:, 0]))))
print("Factor 2 (inlet_temp_c):", sorted(list(set(X[:, 1]))))
print("Factor 3 (drug_loading_ww):", sorted(list(set(X[:, 2]))))
print("Factor 4 (feed_conc_wv):", sorted(list(set(X[:, 3]))))
print("Total Combinations (2 x 3 x 3 x 3):", len(X))
print("Design Type: 2 x 3^3 Full Factorial Design (NOT Box-Behnken)")

print("\n=== 2. CLASS BALANCE & EPV ANALYSIS ===")
n_total = len(y)
n_success = int((y == 0).sum())
n_failure = int((y == 1).sum())
pct_failure = (n_failure / n_total) * 100
epv = n_failure / X.shape[1]
print(f"Total N: {n_total}")
print(f"Success (y=0): {n_success} ({n_success/n_total*100:.2f}%)")
print(f"Failure (y=1): {n_failure} ({pct_failure:.2f}%)")
print(f"Events Per Variable (EPV): {epv:.2f} (Peduzzi/Harrell Minimum Recommendation: >= 10-15)")

print("\n=== 3. APPARENT vs CROSS-VALIDATED AUC ===")
y_prob_apparent = res.model.predict_proba(X)[:, 1]
auc_apparent = roc_auc_score(y, y_prob_apparent)
brier_apparent = brier_score_loss(y, y_prob_apparent)
print(f"Apparent Training AUC (Resubstitution): {auc_apparent:.4f}")
print(f"Apparent Brier Score: {brier_apparent:.4f}")

# Stratified 4-Fold Cross Validation (4 folds because 4 failure events)
skf = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
y_prob_cv = np.zeros(len(y))
y_pred_cv = np.zeros(len(y))

for train_idx, test_idx in skf.split(X, y):
    m = LogisticRegression(C=1.0, solver="lbfgs")
    m.fit(X[train_idx], y[train_idx])
    y_prob_cv[test_idx] = m.predict_proba(X[test_idx])[:, 1]
    y_pred_cv[test_idx] = (y_prob_cv[test_idx] >= 0.5).astype(int)

auc_cv = roc_auc_score(y, y_prob_cv)
brier_cv = brier_score_loss(y, y_prob_cv)
tn, fp, fn, tp = confusion_matrix(y, (y_prob_cv >= 0.15).astype(int)).ravel()

sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
balanced_acc = (sensitivity + specificity) / 2
ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
npv = tn / (tn + fn) if (tn + fn) > 0 else 0

print(f"Cross-Validated AUC (Stratified 4-Fold): {auc_cv:.4f}")
print(f"Cross-Validated Brier Score: {brier_cv:.4f}")
print(f"CV Sensitivity (at p >= 0.15 threshold): {sensitivity:.4f}")
print(f"CV Specificity (at p >= 0.15 threshold): {specificity:.4f}")
print(f"CV Balanced Accuracy: {balanced_acc:.4f}")
print(f"CV Precision / PPV: {ppv:.4f}")
print(f"CV NPV: {npv:.4f}")

print("\n=== 5. LEAVE-ONE-FAILURE-OUT SENSITIVITY ANALYSIS ===")
fail_indices = np.where(y == 1)[0]
base_b0 = res.intercept
base_beta = res.beta_coefficients

print(f"Baseline Fitted Coeffs: b0={base_b0:.4f}, b_rank={base_beta[0]:.4f}, b_temp={base_beta[1]:.4f}, b_load={base_beta[2]:.4f}, b_conc={base_beta[3]:.4f}")

for idx in fail_indices:
    mask = np.ones(len(y), dtype=bool)
    mask[idx] = False
    X_drop, y_drop = X[mask], y[mask]
    
    m_drop = LogisticRegression(C=1.0, solver="lbfgs")
    m_drop.fit(X_drop, y_drop)
    
    b0_d = float(m_drop.intercept_[0])
    beta_d = m_drop.coef_[0]
    
    d_b0 = b0_d - base_b0
    d_beta = beta_d - base_beta
    
    print(f"Drop Failure Index {idx} (T={X[idx, 1]}, L={X[idx, 2]}, C={X[idx, 3]}):")
    print(f"  b0: {b0_d:.4f} (Shift: {d_b0:+.4f})")
    print(f"  b_rank: {beta_d[0]:.4f} (Shift: {d_beta[0]:+.4f})")
    print(f"  b_temp: {beta_d[1]:.4f} (Shift: {d_beta[1]:+.4f})")
    print(f"  b_load: {beta_d[2]:.4f} (Shift: {d_beta[2]:+.4f})")
    print(f"  b_conc: {beta_d[3]:.4f} (Shift: {d_beta[3]:+.4f})")
