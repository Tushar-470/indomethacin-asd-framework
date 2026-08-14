"""
Independent Five-Polymer Provenance & Hoftyzer-Van Krevelen (H-V-K) Calculation Verification Script
Calculates H-V-K HSP components for Soluplus, HPMC E5, PVP-VA 64, PVP K30, and Eudragit E PO step-by-step.
"""

import math
import pandas as pd
import numpy as np

# Hoftyzer-Van Krevelen (H-V-K) Group Contribution Table (Van Krevelen 2009, Table 7.8)
# Group: (F_di [(J*cm3)^0.5/mol], F_pi [(J*cm3)^0.5/mol], E_hi [J/mol], V_i [cm3/mol])
HVK_GROUPS = {
    "-CH3": (420, 0, 0, 33.5),
    "-CH2-": (270, 0, 0, 16.1),
    ">CH-": (80, 0, 0, -1.0),
    ">C<": (-70, 0, 0, -19.2),
    "-O- (ether)": (100, 400, 3000, 3.8),
    "-OH (alcohol)": (210, 500, 20000, 10.0),
    ">C=O (ketone/ester/amide)": (290, 770, 2000, 10.8),
    "-COO- (ester)": (390, 490, 7000, 18.0),
    "-N< (tertiary amine/lactam)": (20, 800, 5000, -9.0),
    "Lactam ring (5-ring)": (0, 0, 0, 0), # Handled via constituent groups (>C=O, -N<, 3x -CH2-, >CH-)
}

def calc_hvk_monomer(name, groups):
    """
    groups: list of (group_name, count)
    Returns: delta_D, delta_P, delta_H, V_molar
    """
    sum_Fdi = 0.0
    sum_Fpi2 = 0.0
    sum_Ehi = 0.0
    sum_V = 0.0

    for g_name, count in groups:
        f_d, f_p, e_h, v = HVK_GROUPS[g_name]
        sum_Fdi += count * f_d
        sum_Fpi2 += count * (f_p ** 2)
        sum_Ehi += count * e_h
        sum_V += count * v

    delta_D = sum_Fdi / sum_V
    delta_P = math.sqrt(sum_Fpi2) / sum_V
    delta_H = math.sqrt(sum_Ehi / sum_V)
    delta_T = math.sqrt(delta_D**2 + delta_P**2 + delta_H**2)

    return {
        "name": name,
        "sum_Fdi": sum_Fdi,
        "sum_Fpi2": sum_Fpi2,
        "sum_Ehi": sum_Ehi,
        "V_molar": sum_V,
        "delta_D": delta_D,
        "delta_P": delta_P,
        "delta_H": delta_H,
        "delta_T": delta_T,
    }

def run_hvk_audit():
    print("=== HOFTYZER-VAN KREVELEN (H-V-K) STEP-BY-STEP CALCULATION AUDIT ===")

    # 1. PVP K30 Monomer Unit: N-vinylpyrrolidone repeat unit (C6H9NO)
    # Backbone: >CH- (1), -CH2- (1); Ring: >N- (1), >C=O (1), -CH2- (3)
    # Total: >CH- (1), -CH2- (4), >N< (1), >C=O (1)
    pvp_groups = [
        (">CH-", 1),
        ("-CH2-", 4),
        ("-N< (tertiary amine/lactam)", 1),
        (">C=O (ketone/ester/amide)", 1),
    ]
    pvp_res = calc_hvk_monomer("PVP K30 Repeat Unit", pvp_groups)

    # 2. Vinyl Acetate Repeat Unit (C4H6O2)
    # Backbone: >CH- (1), -CH2- (1); Sidechain: -COO- (1), -CH3 (1)
    vac_groups = [
        (">CH-", 1),
        ("-CH2-", 1),
        ("-COO- (ester)", 1),
        ("-CH3", 1),
    ]
    vac_res = calc_hvk_monomer("Vinyl Acetate Repeat Unit", vac_groups)

    # 3. PVP-VA 64 Copolymer (60:40 mol% VP:VAc)
    # Weighted sums:
    v_pvpva = 0.60 * pvp_res["V_molar"] + 0.40 * vac_res["V_molar"]
    fdi_pvpva = 0.60 * pvp_res["sum_Fdi"] + 0.40 * vac_res["sum_Fdi"]
    fpi2_pvpva = 0.60 * pvp_res["sum_Fpi2"] + 0.40 * vac_res["sum_Fpi2"]
    ehi_pvpva = 0.60 * pvp_res["sum_Ehi"] + 0.40 * vac_res["sum_Ehi"]

    dD_pvpva = fdi_pvpva / v_pvpva
    dP_pvpva = math.sqrt(fpi2_pvpva) / v_pvpva
    dH_pvpva = math.sqrt(ehi_pvpva / v_pvpva)

    # 4. Soluplus (Caprolactam : Vinyl Acetate : PEG 57:30:13 wt%)
    # Vinyl Caprolactam monomer (C8H13NO): >CH- (1), -CH2- (6), >N< (1), >C=O (1)
    vcap_groups = [
        (">CH-", 1),
        ("-CH2-", 6),
        ("-N< (tertiary amine/lactam)", 1),
        (">C=O (ketone/ester/amide)", 1),
    ]
    vcap_res = calc_hvk_monomer("Vinyl Caprolactam Repeat Unit", vcap_groups)

    # PEG repeat unit (-CH2-CH2-O-): 2x -CH2-, 1x -O-
    peg_groups = [
        ("-CH2-", 2),
        ("-O- (ether)", 1),
    ]
    peg_res = calc_hvk_monomer("PEG Repeat Unit", peg_groups)

    # Convert Soluplus wt% to mol% (MWs: VCap=139.19, VAc=86.09, PEG=44.05)
    moles_vcap = 57.0 / 139.19
    moles_vac = 30.0 / 86.09
    moles_peg = 13.0 / 44.05
    total_moles = moles_vcap + moles_vac + moles_peg
    x_vcap = moles_vcap / total_moles
    x_vac = moles_vac / total_moles
    x_peg = moles_peg / total_moles

    v_solu = x_vcap * vcap_res["V_molar"] + x_vac * vac_res["V_molar"] + x_peg * peg_res["V_molar"]
    fdi_solu = x_vcap * vcap_res["sum_Fdi"] + x_vac * vac_res["sum_Fdi"] + x_peg * peg_res["sum_Fdi"]
    fpi2_solu = x_vcap * vcap_res["sum_Fpi2"] + x_vac * vac_res["sum_Fpi2"] + x_peg * peg_res["sum_Fpi2"]
    ehi_solu = x_vcap * vcap_res["sum_Ehi"] + x_vac * vac_res["sum_Ehi"] + x_peg * peg_res["sum_Ehi"]

    dD_solu = fdi_solu / v_solu
    dP_solu = math.sqrt(fpi2_solu) / v_solu
    dH_solu = math.sqrt(ehi_solu / v_solu)

    # 5. HPMC E5 Substituted Anhydroglucose Unit (AGU)
    # DS(methoxyl) = 1.9, MS(hydroxypropoxyl) = 0.23
    # Base AGU (C6H10O5): 1x C6 ring skeleton, 3x -OH.
    # Substituted AGU: C6H7O2(OH)0.87(OCH3)1.9(OCH2CH(OH)CH3)0.23
    # Constituent groups per AGU:
    # 1x Anhydroglucose ring: 5x >CH-, 1x -CH2-, 2x -O- (ring ether/linkages)
    # 1.9x -OCH3: 1.9x -O-, 1.9x -CH3
    # 0.23x -OCH2CH(OH)CH3: 0.23x -O-, 0.23x -CH2-, 0.23x >CH-, 0.23x -OH, 0.23x -CH3
    # 0.87x unsubstituted -OH
    hpmc_groups = [
        (">CH-", 5.0 + 0.23),
        ("-CH2-", 1.0 + 0.23),
        ("-O- (ether)", 2.0 + 1.9 + 0.23),
        ("-OH (alcohol)", 0.87 + 0.23),
        ("-CH3", 1.9 + 0.23),
    ]
    hpmc_res = calc_hvk_monomer("HPMC E5 Substituted AGU", hpmc_groups)

    # 6. Eudragit E PO Copolymer (Butyl Methacrylate : Dimethylaminoethyl Methacrylate : Methyl Methacrylate 1:2:1 mol%)
    # BMA (C8H14O2): >CH2 (1), >C< (1), -COO- (1), -CH2-CH2-CH2-CH3 -> -CH2- (3), -CH3 (2)
    bma_groups = [("-CH2-", 4), (">C<", 1), ("-COO- (ester)", 1), ("-CH3", 2)]
    bma_res = calc_hvk_monomer("Butyl Methacrylate", bma_groups)

    # DMAEMA (C9H17NO2): >CH2 (1), >C< (1), -COO- (1), -CH2-CH2-N(CH3)2 -> -CH2- (2), -N< (1), -CH3 (3)
    dmaema_groups = [("-CH2-", 3), (">C<", 1), ("-COO- (ester)", 1), ("-N< (tertiary amine/lactam)", 1), ("-CH3", 3)]
    dmaema_res = calc_hvk_monomer("DMAEMA", dmaema_groups)

    # MMA (C5H8O2): >CH2 (1), >C< (1), -COO- (1), -CH3 (2)
    mma_groups = [("-CH2-", 1), (">C<", 1), ("-COO- (ester)", 1), ("-CH3", 2)]
    mma_res = calc_hvk_monomer("Methyl Methacrylate", mma_groups)

    v_eud = 0.25 * bma_res["V_molar"] + 0.50 * dmaema_res["V_molar"] + 0.25 * mma_res["V_molar"]
    fdi_eud = 0.25 * bma_res["sum_Fdi"] + 0.50 * dmaema_res["sum_Fdi"] + 0.25 * mma_res["sum_Fdi"]
    fpi2_eud = 0.25 * bma_res["sum_Fpi2"] + 0.50 * dmaema_res["sum_Fpi2"] + 0.25 * mma_res["sum_Fpi2"]
    ehi_eud = 0.25 * bma_res["sum_Ehi"] + 0.50 * dmaema_res["sum_Ehi"] + 0.25 * mma_res["sum_Ehi"]

    dD_eud = fdi_eud / v_eud
    dP_eud = math.sqrt(fpi2_eud) / v_eud
    dH_eud = math.sqrt(ehi_eud / v_eud)

    results = [
        ("Soluplus", dD_solu, dP_solu, dH_solu, 17.2, 5.2, 6.5),
        ("HPMC E5", hpmc_res["delta_D"], hpmc_res["delta_P"], hpmc_res["delta_H"], 18.5, 8.8, 11.2),
        ("PVP-VA 64", dD_pvpva, dP_pvpva, dH_pvpva, 17.8, 7.2, 8.5),
        ("PVP K30", pvp_res["delta_D"], pvp_res["delta_P"], pvp_res["delta_H"], 17.5, 6.8, 9.2),
        ("Eudragit E PO", dD_eud, dP_eud, dH_eud, 16.8, 5.5, 6.2),
    ]

    df_audit = pd.DataFrame(results, columns=["Polymer", "Calc_dD", "Calc_dP", "Calc_dH", "Curr_dD", "Curr_dP", "Curr_dH"])
    df_audit["Euclidean_Diff"] = np.sqrt(
        (df_audit["Calc_dD"] - df_audit["Curr_dD"])**2 +
        (df_audit["Calc_dP"] - df_audit["Curr_dP"])**2 +
        (df_audit["Calc_dH"] - df_audit["Curr_dH"])**2
    )

    print(df_audit.to_string(index=False))

if __name__ == "__main__":
    run_hvk_audit()
