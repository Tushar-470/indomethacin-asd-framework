"""Integration Tests for Phase 4D: CLI Execution and Schema Enforcement.

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Tests command-line interface execution, strict CSV schema validation,
AHP JSON loading, table rendering, output manifest generation, and error propagation.
"""

import csv
import json
import os
import subprocess
import sys
import numpy as np
import pytest


@pytest.fixture
def valid_cli_files(tmp_path):
    """Generate temporary valid input files for CLI tests."""
    scores_path = tmp_path / "valid_scores.csv"
    ahp_path = tmp_path / "valid_ahp.json"

    # Write valid scores CSV with canonical criteria order
    with open(scores_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["polymer_id", "s_HSP", "s_chi", "s_desc", "s_GT"])
        writer.writerow(["POL-001", 0.9, 0.8, 0.7, 0.6])
        writer.writerow(["POL-002", 0.4, 0.5, 0.6, 0.7])
        writer.writerow(["POL-003", 0.7, 0.6, 0.5, 0.4])

    # Write valid consistent AHP JSON
    ahp_data = {
        "matrix": [
            [1.0, 2.0, 3.0, 4.0],
            [0.5, 1.0, 2.0, 3.0],
            [1/3, 0.5, 1.0, 2.0],
            [0.25, 1/3, 0.5, 1.0],
        ]
    }
    with open(ahp_path, "w", encoding="utf-8") as f:
        json.dump(ahp_data, f)

    return str(scores_path), str(ahp_path)


def test_cli_basic_execution(valid_cli_files):
    """Assert CLI completes with exit code 0 and renders formatted table."""
    scores_file, ahp_file = valid_cli_files
    cmd = [
        sys.executable,
        "-m",
        "asd_mcda.v2.cli",
        "--scores",
        scores_file,
        "--ahp",
        ahp_file,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    assert res.returncode == 0, f"CLI stderr: {res.stderr}"
    assert "PHARMAPOLYSCOPE VARIABLE-K DECISION ENGINE" in res.stdout
    assert "POL-001" in res.stdout
    assert "POL-002" in res.stdout
    assert "POL-003" in res.stdout
    assert "C_L (Closeness)" in res.stdout


def test_cli_output_manifest_generation(valid_cli_files, tmp_path):
    """Assert CLI writes valid canonical JSON manifest when --output is provided."""
    scores_file, ahp_file = valid_cli_files
    out_file = str(tmp_path / "eval_manifest.json")

    cmd = [
        sys.executable,
        "-m",
        "asd_mcda.v2.cli",
        "--scores",
        scores_file,
        "--ahp",
        ahp_file,
        "--output",
        out_file,
        "--quiet",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    assert res.returncode == 0, f"CLI stderr: {res.stderr}"
    assert res.stdout.strip() == ""  # Suppressed by --quiet
    assert os.path.exists(out_file)

    with open(out_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert "analysis_id" in manifest
    assert "analysis_fingerprint" in manifest
    assert "provenance_hashes" in manifest
    assert "full_manifest_sha256" in manifest["provenance_hashes"]


def test_cli_missing_criterion_column_error(tmp_path, valid_cli_files):
    """Assert CSV missing a canonical criterion column exits with code 1 and descriptive error."""
    _, ahp_file = valid_cli_files
    bad_scores = tmp_path / "missing_crit.csv"

    # Missing s_GT column
    with open(bad_scores, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["polymer_id", "s_HSP", "s_chi", "s_desc"])
        writer.writerow(["POL-001", 0.9, 0.8, 0.7])
        writer.writerow(["POL-002", 0.4, 0.5, 0.6])

    cmd = [
        sys.executable,
        "-m",
        "asd_mcda.v2.cli",
        "--scores",
        str(bad_scores),
        "--ahp",
        ahp_file,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    assert res.returncode == 1
    assert "missing required canonical criterion 's_GT'" in res.stderr


def test_cli_score_out_of_range_error(tmp_path, valid_cli_files):
    """Assert score outside [0, 1] range exits with code 1 and error."""
    _, ahp_file = valid_cli_files
    out_of_range = tmp_path / "out_of_range.csv"

    with open(out_of_range, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["polymer_id", "s_HSP", "s_chi", "s_desc", "s_GT"])
        writer.writerow(["POL-001", 1.5, 0.8, 0.7, 0.6])  # 1.5 > 1.0
        writer.writerow(["POL-002", 0.4, 0.5, 0.6, 0.7])

    cmd = [
        sys.executable,
        "-m",
        "asd_mcda.v2.cli",
        "--scores",
        str(out_of_range),
        "--ahp",
        ahp_file,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    assert res.returncode == 1
    assert "out of allowed range [0.0, 1.0]" in res.stderr


def test_cli_inconsistent_ahp_error(tmp_path, valid_cli_files):
    """Assert inconsistent AHP matrix (CR >= 0.08) exits with code 1."""
    scores_file, _ = valid_cli_files
    bad_ahp = tmp_path / "bad_ahp.json"

    with open(bad_ahp, "w", encoding="utf-8") as f:
        json.dump(
            {
                "matrix": [
                    [1.0, 5.0, 9.0, 7.0],
                    [0.2, 1.0, 0.2, 3.0],
                    [1/9, 5.0, 1.0, 0.2],
                    [1/7, 1/3, 5.0, 1.0],
                ]
            },
            f,
        )

    cmd = [
        sys.executable,
        "-m",
        "asd_mcda.v2.cli",
        "--scores",
        scores_file,
        "--ahp",
        str(bad_ahp),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    assert res.returncode == 1
    assert "AHPConsistencyViolationError" in res.stderr
