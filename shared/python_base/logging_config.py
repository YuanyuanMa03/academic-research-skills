#!/usr/bin/env python3
"""Shared logging configuration for academic-research-skills scripts.

Replaces ad-hoc print() statements with structured logging.
Usage:
    from shared.python_base.logging_config import get_logger
    logger = get_logger("cnki-export")
    logger.info("Pushed %d items to Zotero", count)
"""

from __future__ import annotations

import logging
import sys


def get_logger(
    name: str,
    level: int = logging.INFO,
    json_format: bool = False,
) -> logging.Logger:
    """Create a configured logger for a skill script.

    Args:
        name: Logger name (typically the skill name)
        level: Logging level (default: INFO)
        json_format: If True, output JSON-formatted log lines

    Returns:
        Configured logging.Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers on re-initialization
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    if json_format:
        import json
        from datetime import datetime, timezone

        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                return json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "level": record.levelname,
                        "logger": record.name,
                        "message": record.getMessage(),
                    },
                    ensure_ascii=False,
                )

        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
                datefmt="%H:%M:%S",
            )
        )

    logger.addHandler(handler)
    return logger
