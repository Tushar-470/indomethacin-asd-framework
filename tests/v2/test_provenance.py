"""Unit Tests for Phase 4B: Cryptographic Provenance and Manifest Integrity.

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Verifies canonical JSON determinism, non-circular manifest hashing, analysis fingerprinting,
sensitivity to input perturbations, and Git commit provenance.
"""

import json
import numpy as np
import pytest

from asd_mcda.v2.engine import VariableKEngine
from asd_mcda.v2.models import CANONICAL_CRITERIA_ORDER
from asd_mcda.v2.provenance import (
    ENGINE_VERSION,
    FROZEN_V15_BASELINE_COMMIT,
    METHODOLOGY_VERSION,
    build_provenance_manifest,
    compute_analysis_fingerprint,
    compute_canonical_sha256,
    get_repository_head_commit,
    to_canonical_json,
)


def test_canonical_json_determinism():
    """Assert canonical JSON serialization produces sorted keys and compact separators."""
    data = {
        "z_key": 1,
        "a_key": [3, 2, 1],
        "m_key": {"inner_b": 20, "inner_a": 10},
    }
    canonical_str = to_canonical_json(data)
    expected_str = '{"a_key":[3,2,1],"m_key":{"inner_a":10,"inner_b":20},"z_key":1}'
    assert canonical_str == expected_str

    # Determinism across multiple serializations
    assert to_canonical_json(data) == to_canonical_json(data)
    assert compute_canonical_sha256(canonical_str) == compute_canonical_sha256(expected_str)


def test_analysis_fingerprint_determinism_and_sensitivity():
    """Assert analysis fingerprint is deterministic and sensitive to any scientific modification."""
    scores = np.array([
        [0.8, 0.7, 0.6, 0.5],
        [0.3, 0.4, 0.5, 0.6],
    ])
    ahp = np.array([
        [1.0, 2.0, 3.0, 4.0],
        [0.5, 1.0, 2.0, 3.0],
        [1/3, 0.5, 1.0, 2.0],
        [0.25, 1/3, 0.5, 1.0],
    ])

    base_fp = compute_analysis_fingerprint(
        raw_scores=scores,
        criteria_names=CANONICAL_CRITERIA_ORDER,
        ahp_matrix=ahp,
        semantic_mode="standardized_space",
        methodology_version=METHODOLOGY_VERSION,
    )

    # 1. Identical inputs produce exact identical fingerprint
    assert compute_analysis_fingerprint(
        raw_scores=scores.copy(),
        criteria_names=CANONICAL_CRITERIA_ORDER,
        ahp_matrix=ahp.copy(),
        semantic_mode="standardized_space",
        methodology_version=METHODOLOGY_VERSION,
    ) == base_fp

    # 2. Perturbed score alters fingerprint
    scores_mod = scores.copy()
    scores_mod[0, 0] = 0.81
    assert compute_analysis_fingerprint(
        raw_scores=scores_mod,
        criteria_names=CANONICAL_CRITERIA_ORDER,
        ahp_matrix=ahp,
    ) != base_fp

    # 3. Altered criteria order alters fingerprint
    assert compute_analysis_fingerprint(
        raw_scores=scores,
        criteria_names=("s_chi", "s_HSP", "s_desc", "s_GT"),
        ahp_matrix=ahp,
    ) != base_fp

    # 4. Altered AHP matrix alters fingerprint
    ahp_mod = ahp.copy()
    ahp_mod[0, 1] = 2.1
    ahp_mod[1, 0] = 1.0 / 2.1
    assert compute_analysis_fingerprint(
        raw_scores=scores,
        criteria_names=CANONICAL_CRITERIA_ORDER,
        ahp_matrix=ahp_mod,
    ) != base_fp

    # 5. Altered semantic mode alters fingerprint
    assert compute_analysis_fingerprint(
        raw_scores=scores,
        criteria_names=CANONICAL_CRITERIA_ORDER,
        ahp_matrix=ahp,
        semantic_mode="raw_physical_space",
    ) != base_fp

    # 6. Altered methodology version alters fingerprint
    assert compute_analysis_fingerprint(
        raw_scores=scores,
        criteria_names=CANONICAL_CRITERIA_ORDER,
        ahp_matrix=ahp,
        methodology_version="2.0.1-EXPERIMENTAL",
    ) != base_fp


def test_non_circular_manifest_hashing(k2_synthetic_cohort, ahp_reciprocal_matrix):
    """Assert provenance manifest resolves hash circularity via exact two-pass reconstruction."""
    engine = VariableKEngine()
    snapshot = engine.evaluate(
        scores=k2_synthetic_cohort["scores"],
        pairwise_matrix=ahp_reciprocal_matrix["matrix"],
        polymer_ids=k2_synthetic_cohort["polymer_ids"],
    )

    manifest = snapshot.provenance
    assert manifest is not None
    assert "provenance_hashes" in manifest

    full_hash = manifest["provenance_hashes"]["full_manifest_sha256"]
    assert isinstance(full_hash, str)
    assert len(full_hash) == 64

    # Reconstruct manifest without full_manifest_sha256 via canonical JSON deserialization
    manifest_data = json.loads(to_canonical_json(manifest))
    manifest_data["provenance_hashes"].pop("full_manifest_sha256", None)

    recomputed_hash = compute_canonical_sha256(to_canonical_json(manifest_data))
    assert recomputed_hash == full_hash


def test_git_provenance_metadata(k2_synthetic_cohort, ahp_reciprocal_matrix):
    """Assert Git provenance semantics distinguish baseline commit from uncommitted tree."""
    engine = VariableKEngine()
    snapshot = engine.evaluate(
        scores=k2_synthetic_cohort["scores"],
        pairwise_matrix=ahp_reciprocal_matrix["matrix"],
        polymer_ids=k2_synthetic_cohort["polymer_ids"],
    )

    engine_meta = snapshot.provenance["engine_metadata"]
    assert engine_meta["v1_5_baseline_commit"] == "31eee4d"
    assert engine_meta["engine_version"] == ENGINE_VERSION
    assert engine_meta["methodology_version"] == METHODOLOGY_VERSION
    assert engine_meta["implementation_commit"] is None

    expected_head = get_repository_head_commit()
    assert engine_meta["repository_head_commit"] == expected_head
