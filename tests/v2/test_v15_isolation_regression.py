"""Regression Tests Enforcing Absolute Isolation of Frozen v1.5 Baseline.

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2 / Phase 1.1 Hardening.
Asserts that the v2 package imports zero code from v1.5 modules, that v1.5
source files and historical outputs match Git commit 31eee4d byte-for-byte,
and that the golden hash manifest is cryptographically anchored to commit 31eee4d.
"""

import ast
import hashlib
import json
import os
import subprocess
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_V2_DIR = os.path.join(BASE_DIR, "src", "asd_mcda", "v2")
SRC_V15_DIR = os.path.join(BASE_DIR, "src", "asd_mcda")
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "v15_golden_hashes.json")
FROZEN_COMMIT = "31eee4d"


def _load_golden_manifest():
    assert os.path.exists(MANIFEST_PATH), f"Golden hash manifest missing: {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest.get("commit") == FROZEN_COMMIT, (
        f"Manifest referenced commit mismatch: expected {FROZEN_COMMIT}, got {manifest.get('commit')}"
    )
    files = manifest.get("files", {})
    assert len(files) > 0, "Golden hash manifest contains zero files."
    return manifest, files


def _compute_working_tree_hash(file_path: str, expected_hash: str) -> str:
    with open(file_path, "rb") as f:
        raw_bytes = f.read()
    actual_hash = hashlib.sha256(raw_bytes).hexdigest().lower()
    if actual_hash != expected_hash.lower():
        # Handle CRLF checkout conversion on Windows environments
        norm_bytes = raw_bytes.replace(b"\r\n", b"\n")
        norm_hash = hashlib.sha256(norm_bytes).hexdigest().lower()
        if norm_hash == expected_hash.lower():
            return norm_hash
    return actual_hash


def test_zero_v15_import_dependencies():
    """Regression Test 1: Assert AST of all v2 modules contains zero imports from v1.5 components."""
    banned_prefixes = (
        "asd_mcda.mcda",
        "asd_mcda.integration",
        "asd_mcda.compatibility",
        "asd_mcda.orchestrator",
    )

    if not os.path.exists(SRC_V2_DIR):
        pytest.skip("src/asd_mcda/v2 directory does not exist yet.")

    v2_files = [
        os.path.join(SRC_V2_DIR, f) for f in os.listdir(SRC_V2_DIR) if f.endswith(".py")
    ]

    for filepath in v2_files:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for prefix in banned_prefixes:
                        assert not alias.name.startswith(prefix), (
                            f"Illegal v1.5 import '{alias.name}' in {filepath}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for prefix in banned_prefixes:
                        assert not node.module.startswith(prefix), (
                            f"Illegal v1.5 import-from '{node.module}' in {filepath}"
                        )


def test_v15_baseline_files_unmodified():
    """Regression Test 2: Assert all protected working-tree files match golden SHA-256 digests from commit 31eee4d."""
    manifest, files = _load_golden_manifest()

    for rel_path, entry in files.items():
        expected_hash = entry["sha256"].lower()
        file_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        assert os.path.exists(file_path), f"Protected v1.5 baseline file missing: {rel_path}"

        actual_hash = _compute_working_tree_hash(file_path, expected_hash)
        assert actual_hash == expected_hash, (
            f"Cryptographic SHA-256 mismatch for protected file '{rel_path}'!\n"
            f"  Expected (commit {FROZEN_COMMIT}): {expected_hash}\n"
            f"  Actual (working tree):              {actual_hash}"
        )


def test_v15_golden_manifest_matches_commit():
    """Regression Test 3: Independently recompute every manifest hash directly from git show 31eee4d."""
    manifest, files = _load_golden_manifest()

    for rel_path, entry in files.items():
        expected_hash = entry["sha256"].lower()
        expected_len = entry.get("byte_length")

        git_show_arg = f"{FROZEN_COMMIT}:{rel_path}"
        res = subprocess.run(
            ["git", "show", git_show_arg],
            cwd=BASE_DIR,
            capture_output=True,
            check=True,
        )
        git_bytes = res.stdout
        git_hash = hashlib.sha256(git_bytes).hexdigest().lower()

        assert git_hash == expected_hash, (
            f"Manifest hash desynchronization for '{rel_path}'!\n"
            f"  Manifest stored digest:  {expected_hash}\n"
            f"  git show {FROZEN_COMMIT} digest: {git_hash}"
        )

        if expected_len is not None:
            assert len(git_bytes) == expected_len, (
                f"Byte length mismatch for '{rel_path}' in git show {FROZEN_COMMIT}: "
                f"expected {expected_len}, got {len(git_bytes)}"
            )


def test_v15_historical_results_byte_identical():
    """Regression Test 4: Assert all protected historical outputs under results/ match fixed golden digests."""
    manifest, files = _load_golden_manifest()

    historical_results = {
        path: entry
        for path, entry in files.items()
        if path.startswith("results/final/") or path.startswith("results/reports/")
    }

    assert len(historical_results) > 0, "No historical results found in golden manifest."

    for rel_path, entry in historical_results.items():
        expected_hash = entry["sha256"].lower()
        file_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
        assert os.path.exists(file_path), f"Protected historical result file missing: {rel_path}"

        actual_hash = _compute_working_tree_hash(file_path, expected_hash)
        assert actual_hash == expected_hash, (
            f"Historical result cryptographic digest mismatch for '{rel_path}'!\n"
            f"  Expected (commit {FROZEN_COMMIT}): {expected_hash}\n"
            f"  Actual (working tree):              {actual_hash}"
        )
