"""
Helper utilities for cryptographic checksums, file management, and string sanitization.
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Union


def generate_sha256(data: Union[str, bytes, dict, list]) -> str:
    """Generate SHA-256 hash string for input data (deterministic for dict/list)."""
    if isinstance(data, (dict, list)):
        serialized = json.dumps(data, sort_keys=True, default=str)
        content_bytes = serialized.encode("utf-8")
    elif isinstance(data, str):
        content_bytes = data.encode("utf-8")
    elif isinstance(data, bytes):
        content_bytes = data
    else:
        content_bytes = str(data).encode("utf-8")

    return hashlib.sha256(content_bytes).hexdigest()


def ensure_dir(dir_path: Union[str, Path]) -> Path:
    """Ensure directory exists, creating parents if necessary."""
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_filename(name: str) -> str:
    """Sanitize string for safe cross-platform file naming."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r"\s+", "_", name)
    return name.strip("_")
