"""
Command Line Interface (CLI) entry point for the ASD computational polymer screening framework.
Usage: python -m asd_mcda.cli --config config/workflow/workflow_config.yaml
"""

import argparse
import sys
from pathlib import Path

from asd_mcda.__version__ import __version__
from asd_mcda.configuration.loader import ConfigManager
from asd_mcda.orchestrator import WorkflowOrchestrator


def main() -> int:
    """CLI entry point for running the screening workflow."""
    parser = argparse.ArgumentParser(
        description=f"asd_mcda v{__version__}: Computational Polymer Screening Framework for SD-ASDs"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config/workflow/workflow_config.yaml",
        help="Path to workflow YAML configuration file",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s v{__version__}",
    )

    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        return 1

    try:
        config_mgr = ConfigManager(config_path)
        orchestrator = WorkflowOrchestrator(config_mgr)
        summary = orchestrator.run()

        print("\n" + "=" * 60)
        print("ASD COMPUTATIONAL SCREENING WORKFLOW COMPLETE")
        print("=" * 60)
        print(f"Top Selection : {summary.selected_polymer_name} ({summary.selected_polymer_id})")
        print(f"Closeness CL  : {summary.topsis_cl:.4f}")
        print(f"Confidence    : {summary.confidence_tier}")
        print(f"JSON Report   : {summary.reports_generated['json']}")
        print(f"Excel Report  : {summary.reports_generated['xlsx']}")
        print(f"Figures       : {len(summary.figures_generated)} publication PNGs generated")
        print("=" * 60 + "\n")
        return 0

    except Exception as e:
        print(f"\nPipeline Execution Failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
