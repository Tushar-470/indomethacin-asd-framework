"""Command-Line Interface for PharmaPolySCOPE Variable-K Engine (v2).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Minimal CLI wrapper strictly orchestrating VariableKEngine.
Contains ZERO scientific mathematics.
Enforces strict input CSV/JSON validation, deterministic row preservation,
and canonical evaluation manifest generation.
"""

import argparse
import csv
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from asd_mcda.v2.engine import VariableKEngine
from asd_mcda.v2.models import CANONICAL_CRITERIA_ORDER
from asd_mcda.v2.provenance import to_canonical_json


def load_scores_csv(csv_path: str) -> Tuple[Tuple[str, ...], np.ndarray]:
    """Load and validate candidate decision scores from a CSV file.

    Strict schema enforcement:
    - Must contain 'polymer_id' column.
    - Must contain exactly the 4 canonical criteria columns ('s_HSP', 's_chi', 's_desc', 's_GT').
    - Candidate polymer_id values must be unique and non-empty.
    - Score values must be finite numbers in the range [0.0, 1.0].
    - No NaN, null, or missing values permitted.
    - Preserves file row ordering.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Scores CSV file not found: {csv_path}")

    polymer_ids: List[str] = []
    scores_list: List[List[float]] = []

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Scores CSV file is empty: {csv_path}")

        fields = [col.strip() for col in reader.fieldnames]

        if "polymer_id" not in fields:
            raise ValueError(f"Scores CSV must contain 'polymer_id' column. Found columns: {fields}")

        for crit in CANONICAL_CRITERIA_ORDER:
            if crit not in fields:
                raise ValueError(
                    f"Scores CSV missing required canonical criterion '{crit}'. "
                    f"Required: {CANONICAL_CRITERIA_ORDER}. Found: {fields}"
                )

        seen_ids = set()
        for row_idx, row in enumerate(reader, start=2):
            pid = row["polymer_id"].strip()
            if not pid:
                raise ValueError(f"Row {row_idx}: Empty 'polymer_id' is prohibited.")
            if pid in seen_ids:
                raise ValueError(f"Row {row_idx}: Duplicate 'polymer_id' '{pid}' detected.")
            seen_ids.add(pid)
            polymer_ids.append(pid)

            row_scores = []
            for crit in CANONICAL_CRITERIA_ORDER:
                val_str = row.get(crit, "").strip()
                if not val_str:
                    raise ValueError(f"Row {row_idx} ({pid}): Missing value for criterion '{crit}'.")
                try:
                    val = float(val_str)
                except ValueError:
                    raise ValueError(
                        f"Row {row_idx} ({pid}): Non-numeric value '{val_str}' for criterion '{crit}'."
                    )

                if not np.isfinite(val):
                    raise ValueError(
                        f"Row {row_idx} ({pid}): Non-finite value '{val}' for criterion '{crit}'."
                    )
                if val < 0.0 or val > 1.0:
                    raise ValueError(
                        f"Row {row_idx} ({pid}): Score {val} for '{crit}' out of allowed range [0.0, 1.0]."
                    )
                row_scores.append(val)
            scores_list.append(row_scores)

    if len(polymer_ids) < 2:
        raise ValueError(
            f"Cohort must contain at least 2 candidates for standardization, found {len(polymer_ids)}."
        )

    scores_matrix = np.asarray(scores_list, dtype=np.float64)
    return tuple(polymer_ids), scores_matrix


def load_ahp_json(json_path: str) -> np.ndarray:
    """Load and validate a 4x4 AHP comparison matrix from a JSON file."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"AHP JSON file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        if "matrix" in data:
            raw_matrix = data["matrix"]
        elif "pairwise_matrix" in data:
            raw_matrix = data["pairwise_matrix"]
        else:
            raise ValueError(f"AHP JSON must contain 'matrix' key. Found keys: {list(data.keys())}")
    elif isinstance(data, list):
        raw_matrix = data
    else:
        raise ValueError("AHP JSON must contain a dictionary with 'matrix' or a 2D list.")

    matrix = np.asarray(raw_matrix, dtype=np.float64)
    if matrix.shape != (4, 4):
        raise ValueError(f"AHP matrix must be 4x4, got shape {matrix.shape}.")

    return matrix


def format_results_table(result: Any) -> str:
    """Render a clean tabular representation of the SP-PRP-TOPSIS evaluation result."""
    lines = []
    lines.append("=" * 82)
    lines.append(" PHARMAPOLYSCOPE VARIABLE-K DECISION ENGINE (SP-PRP-TOPSIS v2)")
    lines.append("=" * 82)
    lines.append(f" Analysis ID:          {result.analysis_id}")
    lines.append(f" Analysis Fingerprint: {result.analysis_fingerprint}")
    lines.append(f" Retained Dimension K: {result.retained_k} (Cumulative Variance: {result.cumulative_variance * 100:.2f}%)")
    lines.append(f" Boundary Eigengap delta_K: {result.boundary_eigengap:.4f} (Stability: {result.stability_status})")
    lines.append(f" AHP Consistency (CR): {result.consistency_ratio:.4f} (Gate: ACCEPTED)")
    lines.append(f" Semantic Mode:        {result.weight_semantic_mode}")
    lines.append("-" * 82)
    lines.append(f" {'Rank':<5} {'Polymer ID':<16} {'C_L (Closeness)':<17} {'D+ (Ideal)':<12} {'D- (Anti)':<12} {'Rel Trunc'}")
    lines.append("-" * 82)

    # Sort display by rank ascending
    ranked_indices = np.argsort(result.ranks)
    for idx in ranked_indices:
        r = result.ranks[idx]
        pid = result.metrics.ranked_polymer_ids[idx]
        cl = result.closeness_coefficients[idx]
        dp = result.distance_to_ideal[idx]
        dm = result.distance_to_anti_ideal[idx]
        rel_trunc = result.truncation.records[idx].relative_discrepancy
        lines.append(f" {r:<5} {pid:<16} {cl:<17.4f} {dp:<12.4f} {dm:<12.4f} {rel_trunc * 100:.2f}%")

    lines.append("=" * 82)
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI execution entrypoint."""
    parser = argparse.ArgumentParser(
        prog="python -m asd_mcda.v2.cli",
        description="PharmaPolySCOPE v2 SP-PRP-TOPSIS Decision Engine CLI",
    )
    parser.add_argument(
        "--scores",
        required=True,
        help="Path to decision scores CSV containing polymer_id and criteria columns.",
    )
    parser.add_argument(
        "--ahp",
        required=True,
        help="Path to JSON file containing the 4x4 AHP pairwise comparison matrix.",
    )
    parser.add_argument(
        "--drug",
        default=None,
        help="Optional path to model drug JSON profile.",
    )
    parser.add_argument(
        "--semantic-mode",
        choices=["standardized_space", "raw_physical_space"],
        default="standardized_space",
        help="Weighting semantic mode (default: standardized_space).",
    )
    parser.add_argument(
        "--variance-threshold",
        type=float,
        default=0.95,
        help="Cumulative explained variance threshold for K selection (default: 0.95).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write the canonical evaluation JSON manifest.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress tabular stdout output.",
    )

    args = parser.parse_args(argv)

    try:
        polymer_ids, scores_matrix = load_scores_csv(args.scores)
        pairwise_matrix = load_ahp_json(args.ahp)

        drug_data = None
        if args.drug:
            with open(args.drug, "r", encoding="utf-8") as f:
                drug_data = json.load(f)

        engine = VariableKEngine()
        result = engine.evaluate(
            scores=scores_matrix,
            pairwise_matrix=pairwise_matrix,
            polymer_ids=polymer_ids,
            drug_data=drug_data,
            semantic_mode=args.semantic_mode,
            variance_threshold=args.variance_threshold,
        )

        if not args.quiet:
            print(format_results_table(result))

        if args.output:
            canonical_manifest_json = to_canonical_json(result.provenance)
            out_dir = os.path.dirname(os.path.abspath(args.output))
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(canonical_manifest_json)
            if not args.quiet:
                print(f"\n[OK] Canonical evaluation manifest written to: {args.output}")

        return 0

    except Exception as exc:
        sys.stderr.write(f"\n[ERROR] Variable-K Engine Failure [{exc.__class__.__name__}]: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
