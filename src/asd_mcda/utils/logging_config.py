"""
Logging configuration for asd_mcda.
Provides execution logging and immutable audit log streams aligned with SAS V1.0 Task 8.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from asd_mcda.utils.helpers import ensure_dir


def setup_logger(
    name: str = "asd_mcda",
    log_dir: Optional[Path] = None,
    level: int = logging.INFO,
    log_to_console: bool = True,
) -> logging.Logger:
    """Set up and return logger with console and file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_dir:
        ensure_dir(log_dir)
        file_handler = logging.FileHandler(log_dir / "execution.log", encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        audit_handler = logging.FileHandler(log_dir / "audit.log", encoding="utf-8")
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            "[AUDIT] [%(asctime)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ"
        )
        audit_handler.setFormatter(audit_formatter)
        logger.addHandler(audit_handler)

    return logger
