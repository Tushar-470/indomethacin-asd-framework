"""
Forensic Numerical Audit of Figure 12 / Failure Boundary Map
"""

import sys
import json
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from asd_mcda.prediction.fbm import FailureBoundaryMap

fbm = FailureBoundaryMap()
X, y, names = fbm.generate_synthetic_doe_dataset()
res = fbm.fit(X, y)

b0 = res.intercept
b1, b2, b3, b4 = res.beta_coefficients

print("=== FORENSIC MODEL FIT RESULTS ===")
print("Feature Names:", names)
print("Training N:", len(X))
print("Training y=0 (success):", int((y == 0).sum()))
print("Training y=1 (failure):", int((y == 1).sum()))
print("Fitted Intercept (b0):", b0)
print("Fitted Coefficients:")
print("  b1 (polymer_rank):", b1)
print("  b2 (inlet_temp_c):", b2)
print("  b3 (drug_loading_ww):", b3)
print("  b4 (feed_conc_wv):", b4)

print("\n=== RAW FEATURE FORMULA ===")
print("logit(P) = b0 + b1*r + b2*T + b3*L + b4*C")
print(f"logit(P) = {b0:.6f} + ({b1:.6f})*r + ({b2:.6f})*T + ({b3:.6f})*L + ({b4:.6f})*C")

print("\n=== CENTERED FEATURE FORMULA CONVERSION ===")
# Converting to centered form: logit = alpha0 + beta_r*r + beta_t*(T-100) + beta_l*(L-0.30) + beta_c*(C-0.10)
# logit = b0 + b1*r + b2*(T-100 + 100) + b3*(L-0.30 + 0.30) + b4*(C-0.10 + 0.10)
# logit = (b0 + b2*100 + b3*0.30 + b4*0.10) + b1*r + b2*(T-100) + b3*(L-0.30) + b4*(C-0.10)
alpha0 = b0 + b2 * 100.0 + b3 * 0.30 + b4 * 0.10
print(f"Centered Intercept alpha0 (at r=0, T=100, L=0.30, C=0.10): {alpha0:.6f}")
print(f"Centered Intercept for Rank 1 (r=1, T=100, L=0.30, C=0.10): {alpha0 + b1:.6f}")

print("\n=== POINT-BY-POINT PREDICTIONS (r=1, C=0.10) ===")
test_points = [
    (120.0, 0.10),
    (80.0, 0.50),
    (80.0, 0.40),
    (120.0, 0.20),
    (80.0, 0.20),
    (100.0, 0.30)
]

for t, l in test_points:
    pt = np.array([[1.0, t, l, 0.10]])
    p_model = float(res.model.predict_proba(pt)[0, 1])
    
    # Raw logit
    logit_raw = b0 + b1 * 1.0 + b2 * t + b3 * l + b4 * 0.10
    p_raw = 1.0 / (1.0 + np.exp(-logit_raw))

    # Centered logit
    logit_centered = (alpha0 + b1 * 1.0) + b2 * (t - 100.0) + b3 * (l - 0.30) + b4 * (0.10 - 0.10)
    p_centered = 1.0 / (1.0 + np.exp(-logit_centered))

    print(f"T={t:5.1f}°C, L={l:4.2f} w/w | Logit: {logit_raw:8.4f} | P(model): {p_model:.6f} | P(calc): {p_centered:.6f}")

print("\n=== 2D PREDICTION GRID EVALUATION ===")
temp_grid = np.linspace(80, 120, 50)
load_grid = np.linspace(0.10, 0.50, 50)
T, L = np.meshgrid(temp_grid, load_grid)

pts = np.c_[np.ones(T.size), T.ravel(), L.ravel(), np.full(T.size, 0.10)]
P = res.model.predict_proba(pts)[:, 1].reshape(T.shape)

min_idx = np.unravel_index(np.argmin(P), P.shape)
max_idx = np.unravel_index(np.argmax(P), P.shape)

min_val = float(P[min_idx])
min_T = float(T[min_idx])
min_L = float(L[min_idx])

max_val = float(P[max_idx])
max_T = float(T[max_idx])
max_L = float(L[max_idx])

print(f"Grid Domain: T in [{temp_grid.min():.1f}, {temp_grid.max():.1f}], L in [{load_grid.min():.2f}, {load_grid.max():.2f}]")
print(f"Minimum P(fail): {min_val:.6f} at T={min_T:.1f}°C, L={min_L:.2f} w/w")
print(f"Maximum P(fail): {max_val:.6f} at T={max_T:.1f}°C, L={max_L:.2f} w/w")
print("Does grid cross P(fail) >= 0.50?", bool((P >= 0.50).any()))

print("\n=== TRAINING DOMAIN vs EXTENSION DOMAIN ===")
print("Training Loading Range: [0.20, 0.40] w/w")
print("Prediction Domain Plotted: [0.10, 0.50] w/w")
print("Extrapolation Below Training: [0.10, 0.20) w/w")
print("Extrapolation Above Training: (0.40, 0.50] w/w")
