"""
ConfigManager class providing unified loading, schema validation, and path resolution.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml

from asd_mcda.configuration.validator import validate_workflow_config, validate_drug_dict
from asd_mcda.utils.helpers import generate_sha256


class ConfigManager:
    """Configuration Manager responsible for loading, resolving, and validating workflow parameters."""

    def __init__(self, config_path: Union[str, Path], root_dir: Optional[Union[str, Path]] = None):
        self.config_path = Path(config_path)
        self.root_dir = Path(root_dir) if root_dir else self.config_path.parent.parent.parent
        self.raw_config: Dict[str, Any] = {}
        self.checksum: str = ""
        self._load_config()

    def _load_config(self) -> None:
        """Load YAML workflow configuration file and validate."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.raw_config = yaml.safe_load(f)

        errors = validate_workflow_config(self.raw_config)
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")

        self.checksum = generate_sha256(self.raw_config)

    def resolve_path(self, relative_path: str) -> Path:
        """Resolve a relative path against the project root directory."""
        path = Path(relative_path)
        if path.is_absolute():
            return path
        return (self.root_dir / path).resolve()

    def get_drug_profile_path(self) -> Path:
        return self.resolve_path(self.raw_config["paths"]["drug_profile"])

    def get_polymer_library_path(self) -> Path:
        return self.resolve_path(self.raw_config["paths"]["polymer_library"])

    def get_ahp_matrix_dir(self) -> Path:
        return self.resolve_path(self.raw_config["paths"]["ahp_matrix_dir"])

    def get_output_dir(self) -> Path:
        return self.resolve_path(self.raw_config["paths"]["output_dir"])

    def get_log_dir(self) -> Path:
        return self.resolve_path(self.raw_config["paths"]["log_dir"])

    def load_drug_json(self) -> Dict[str, Any]:
        """Load and validate canonical drug profile JSON."""
        drug_path = self.get_drug_profile_path()
        if not drug_path.exists():
            raise FileNotFoundError(f"Drug profile JSON not found: {drug_path}")

        with open(drug_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        errors = validate_drug_dict(data)
        if errors:
            raise ValueError(f"Drug JSON validation failed: {'; '.join(errors)}")

        return data
