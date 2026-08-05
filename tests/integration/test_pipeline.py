"""Integration tests for the full end-to-end computational pipeline."""

from pathlib import Path
import pytest

from asd_mcda.configuration.loader import ConfigManager
from asd_mcda.orchestrator import WorkflowOrchestrator


def test_full_pipeline_execution(tmp_path):
    """Test full execution of WorkflowOrchestrator from config file."""
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "config" / "workflow" / "workflow_config.yaml"

    assert config_path.exists(), f"Workflow config missing at {config_path}"

    config_mgr = ConfigManager(config_path, root_dir=project_root)
    orchestrator = WorkflowOrchestrator(config_mgr)
    summary = orchestrator.run()

    assert summary.success
    assert summary.selected_polymer_name is not None
    assert summary.topsis_cl > 0.0
    assert summary.gate1_passed
    assert summary.gate2_passed
    assert summary.reports_generated["json"].exists()
    assert len(summary.figures_generated) >= 5
