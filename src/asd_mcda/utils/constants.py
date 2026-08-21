"""
Constants and lookup tables for the ASD computational framework.
Aligned with Master Research Framework V2.0 (Frozen).
"""

# Physical and Mathematical Constants
GAS_CONSTANT_R = 8.314462618  # J/(mol*K)
DEFAULT_TEMPERATURE_K = 298.15  # K (25 °C)
BOYER_BEAMAN_FACTOR = 0.70  # Tg = 0.7 * Tm

# Random Index (RI) values for AHP consistency calculation (Saaty 1980)
AHP_RANDOM_INDEX = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
}

# Gate Threshold Defaults
DEFAULT_HSP_RED_MAX = 1.0
DEFAULT_AHP_CR_MAX = 0.08
DEFAULT_RMSE_MAX_K = 10.0
DEFAULT_SPEARMAN_RHO_MIN = 0.70
DEFAULT_BASELINE_DELTA_RHO_MIN = 0.10

# Default Descriptor Weights for s_desc
DEFAULT_DESC_SUBWEIGHTS = {
    "hbd": 0.30,
    "hba": 0.30,
    "tpsa": 0.20,
    "aromatic": 0.20,
}

# Lindvig Conversion Parameters (Lindvig et al. 2002, Fluid Phase Equilibria 203, 247-260)
# alpha is a GLOBAL multiplicative correction factor on the whole bracket,
# not a per-term weight. Dispersive term is unweighted (implicit coefficient 1);
# polar and H-bonding terms each carry the literature 0.25 sub-weight.
LINDVIG_ALPHA = 0.60
LINDVIG_SUBWEIGHTS = (1.0, 0.25, 0.25)  # (Dispersion, Polar, H-bonding)

