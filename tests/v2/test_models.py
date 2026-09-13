"""Unit Tests for Phase 4A: Immutable Data Models and Deep Freezing.

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Verifies deep recursive immutability, caller buffer independence, read-only NumPy flags,
rejection of unsupported mutable types, and frozen dataclass contracts.
"""

from dataclasses import FrozenInstanceError
from types import MappingProxyType
import numpy as np
import pytest

from asd_mcda.v2.models import (
    CANONICAL_CRITERIA_ORDER,
    AHPResult,
    DecisionMetricResult,
    PCAResult,
    StandardizationResult,
    SubspaceStabilityRecord,
    TruncationAuditResult,
    TruncationDiagnosticRecord,
    VariableKDecisionSnapshot,
    deep_freeze,
    make_readonly,
)


def test_canonical_criteria_order_frozen():
    """Assert the canonical criteria order is exactly frozen as specified."""
    assert CANONICAL_CRITERIA_ORDER == ("s_HSP", "s_chi", "s_desc", "s_GT")


def test_deep_freeze_ndarray_defensive_copy():
    """Assert ndarray is defensively copied and marked read-only."""
    orig = np.array([[1.0, 2.0], [3.0, 4.0]])
    frozen = deep_freeze(orig)

    assert frozen is not orig
    assert frozen.flags.writeable is False
    assert np.array_equal(frozen, orig)

    # Caller buffer mutation does not affect frozen array
    orig[0, 0] = 99.0
    assert frozen[0, 0] == 1.0

    # Frozen buffer cannot be modified
    with pytest.raises(ValueError, match="read-only"):
        frozen[0, 0] = 99.0


def test_deep_freeze_nested_containers():
    """Assert nested mappings, lists, and sets are recursively converted to immutable types."""
    nested_structure = {
        "level1_list": [
            1,
            2,
            {"level2_dict": [3, 4, {"level3_set": {5, 6}}]},
        ],
        "arr": np.array([10.0, 20.0]),
    }

    frozen = deep_freeze(nested_structure)

    assert isinstance(frozen, MappingProxyType)
    assert isinstance(frozen["level1_list"], tuple)
    assert isinstance(frozen["level1_list"][2], MappingProxyType)
    assert isinstance(frozen["level1_list"][2]["level2_dict"], tuple)
    assert isinstance(frozen["level1_list"][2]["level2_dict"][2], MappingProxyType)
    assert isinstance(frozen["level1_list"][2]["level2_dict"][2]["level3_set"], frozenset)
    assert isinstance(frozen["arr"], np.ndarray)
    assert frozen["arr"].flags.writeable is False

    # Attempting mutation raises TypeError
    with pytest.raises(TypeError):
        frozen["level1_list"] = "mutate"

    with pytest.raises(TypeError):
        frozen["level1_list"][2]["level2_dict"] = "mutate"


def test_deep_freeze_caller_dict_independence():
    """Assert mutating caller dict after freezing does not mutate frozen mapping."""
    caller_dict = {"a": [1, 2, {"b": "initial"}]}
    frozen = deep_freeze(caller_dict)

    caller_dict["a"][2]["b"] = "tampered"
    caller_dict["a"].append(999)

    assert frozen["a"][2]["b"] == "initial"
    assert len(frozen["a"]) == 3


def test_deep_freeze_rejects_unsupported_mutable_types():
    """Assert arbitrary custom mutable objects without freeze rules are rejected with TypeError."""
    class CustomMutable:
        def __init__(self):
            self.value = 42

    custom_obj = CustomMutable()
    with pytest.raises(TypeError, match="Unsupported mutable type"):
        deep_freeze(custom_obj)


def test_make_readonly_defensive_behavior():
    """Assert make_readonly produces an independent read-only float64 array."""
    raw = [1, 2, 3]
    ro = make_readonly(raw)

    assert isinstance(ro, np.ndarray)
    assert ro.dtype == np.float64
    assert ro.flags.writeable is False
    assert np.array_equal(ro, [1.0, 2.0, 3.0])

    with pytest.raises(ValueError, match="Cannot make None"):
        make_readonly(None)


def test_standardization_result_dataclass_immutability():
    """Assert StandardizationResult enforces frozen attributes and read-only arrays."""
    mean_in = np.array([0.5, 0.5, 0.5, 0.5])
    std_in = np.array([0.2, 0.2, 0.2, 0.2])
    Z_in = np.zeros((3, 4))
    zp_in = np.ones(4)
    zm_in = -np.ones(4)

    res = StandardizationResult(
        cohort_mean=mean_in,
        cohort_std=std_in,
        standardized_scores=Z_in,
        z_plus=zp_in,
        z_minus=zm_in,
        ddof=0,
    )

    # Cannot reassign dataclass fields
    with pytest.raises(FrozenInstanceError):
        res.cohort_mean = np.zeros(4)

    # Caller arrays cannot mutate dataclass
    mean_in[0] = 999.0
    assert res.cohort_mean[0] == 0.5

    # Dataclass arrays cannot be mutated
    with pytest.raises(ValueError, match="read-only"):
        res.cohort_mean[0] = 999.0


def test_variable_k_decision_snapshot_deep_immutability():
    """Assert VariableKDecisionSnapshot guarantees full depth immutability."""
    mean = np.array([0.5, 0.5, 0.5, 0.5])
    std = np.array([0.2, 0.2, 0.2, 0.2])
    Z = np.zeros((3, 4))
    zp = np.ones(4)
    zm = -np.ones(4)

    std_res = StandardizationResult(mean, std, Z, zp, zm, ddof=0)
    pca_res = PCAResult(
        eigenvalues=(2.0, 1.0, 0.8, 0.2),
        eigenvectors=np.eye(4),
        retained_basis=np.eye(4)[:, :2],
        retained_k=2,
        cumulative_variance=0.75,
    )
    stab_res = SubspaceStabilityRecord(
        retained_k=2,
        ambient_p=4,
        eigenvalues=(2.0, 1.0, 0.8, 0.2),
        cumulative_variance=0.75,
        boundary_eigengap=0.2,
        stability_status="STABLE",
    )
    ahp_res = AHPResult(
        pairwise_matrix=np.eye(4),
        weights=np.array([0.25, 0.25, 0.25, 0.25]),
        consistency_ratio=0.01,
        lambda_max=4.03,
        consistency_index=0.01,
    )
    metric_res = DecisionMetricResult(
        projected_scores=np.zeros((3, 2)),
        t_plus=np.ones(2),
        t_minus=-np.ones(2),
        metric_tensor=np.eye(2),
        weight_matrix=np.eye(4),
        distance_to_ideal=np.ones(3),
        distance_to_anti_ideal=np.ones(3),
        closeness_coefficients=np.array([0.5, 0.5, 0.5]),
        ranks=(1, 2, 3),
        ranked_polymer_ids=("P1", "P2", "P3"),
    )
    trunc_rec = TruncationDiagnosticRecord(
        polymer_id="P1",
        d_full_sq=1.0,
        d_k_sq=0.9,
        signed_discrepancy=0.1,
        relative_discrepancy=0.1,
    )
    trunc_res = TruncationAuditResult(
        records=(trunc_rec,),
        max_relative_discrepancy=0.1,
        mean_relative_discrepancy=0.1,
    )

    caller_drug = {"id": "DRUG-01", "nested": [1, 2]}
    caller_polymers = [{"id": "P1"}, {"id": "P2"}, {"id": "P3"}]

    snapshot = VariableKDecisionSnapshot(
        analysis_id="test-analysis",
        analysis_fingerprint="dummy-fingerprint",
        drug_snapshot=caller_drug,
        polymer_cohort_snapshot=caller_polymers,
        criteria_names=CANONICAL_CRITERIA_ORDER,
        raw_scores=np.zeros((3, 4)),
        weights=np.array([0.25, 0.25, 0.25, 0.25]),
        standardization=std_res,
        pca=pca_res,
        stability=stab_res,
        ahp=ahp_res,
        metrics=metric_res,
        truncation=trunc_res,
        provenance={"meta": "info"},
        provenance_hashes={"full_manifest_sha256": "abc"},
    )

    # Test top-level property forwarding
    assert snapshot.retained_k == 2
    assert snapshot.stability_status == "STABLE"
    assert snapshot.boundary_eigengap == 0.2
    assert np.array_equal(snapshot.closeness_coefficients, [0.5, 0.5, 0.5])
    assert snapshot.ranks == (1, 2, 3)

    # Test caller mutation isolation
    caller_drug["nested"][0] = 999
    assert snapshot.drug_snapshot["nested"][0] == 1

    caller_polymers[0]["id"] = "MUTATED"
    assert snapshot.polymer_cohort_snapshot[0]["id"] == "P1"

    # Test buffer write-protection
    with pytest.raises(ValueError, match="read-only"):
        snapshot.raw_scores[0, 0] = 999.0
