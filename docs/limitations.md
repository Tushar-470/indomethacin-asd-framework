# Known Methodological Limitations

**Release**: v1.3.1-FREEZE  
**Classification**: Pre-Laboratory Computational Prediction  

---

## 1. Group Contribution Hansen Solubility Parameters

All polymer Hansen Solubility Parameter (HSP) components ($\delta_D, \delta_P, \delta_H$) in the active candidate library are **derived via the Hoftyzer–Van Krevelen (H-V-K) group contribution method**, not through direct experimental multi-solvent dissolution titration spheres.

An external calibration analysis against published experimental polymer solubility spheres ($n=10$ pharmaceutical polymers; Osakwe & Le, *ACS Omega* 2026;11(26):39417–39428) characterized the following structural group-contribution errors:
- $\delta_D$ Mean Bias: $+2.37\text{ MPa}^{0.5}$
- $\delta_P$ Mean Bias: $+0.55\text{ MPa}^{0.5}$
- $\delta_H$ Mean Bias: $+3.98\text{ MPa}^{0.5}$
- Mean Euclidean Error: $6.32\text{ MPa}^{0.5}$

**Impact**: H-V-K calculations exhibit systematic polar overestimation, particularly for highly hydroxylated and hydrogen-bonding polymer repeat units. While stochastic Monte Carlo uncertainty quantification ($\pm 1.5\text{ MPa}^{0.5}$) captures ranking sensitivity, empirical multi-solvent testing remains necessary during experimental formulation.

---

## 2. Flory–Huggins $\chi$ Estimation Assumptions

The Flory–Huggins interaction parameter $\chi$ is approximated using the **Lindvig solubility parameter conversion** ($0.60\,\Delta\delta_D^2 + 0.25\,\Delta\delta_P^2 + 0.25\,\Delta\delta_H^2$) at $T = 298.15\text{ K}$, rather than from direct melting point depression DSC thermograms across drug–polymer blends.

---

## 3. Gordon–Taylor Anti-Plasticization Predictor

Gordon–Taylor composite $T_{g,\text{mix}}$ predictions employ the classical **Simha–Boyer constant ($K$)** under idealized volume-additivity assumptions. Specific non-covalent interactions (e.g. drug–polymer hydrogen bonding or charge transfer complexes) may cause positive or negative deviations from Gordon–Taylor ideality that require Kwei-parameter or experimental mDSC validation.

---

## 4. Monte Carlo Uncertainty Sampling Boundaries

The 7 joint parameter uncertainties sampled during Monte Carlo UQ ($N=10{,}000$) represent uniform and relative uniform heuristic ranges based on literature consensus. The resulting $P(\text{top-1})$ probability quantifies **computational model stability under input perturbation**, and must not be conflated with clinical or physical manufacturing success rates.

---

## 5. Excipient Scope and Specificity

The frozen computational baseline is parameterized specifically for **indomethacin (BCS Class II)** as a model drug. Extrapolation of rankings to other drug molecules requires updating the drug profile and re-eliciting AHP criteria weights.
