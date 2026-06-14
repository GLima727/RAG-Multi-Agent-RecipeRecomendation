"""
logger.py — Shared logger for the recipe agent.

Set LOG_LEVEL=DEBUG in your environment to see full pipeline traces
including tool call arguments and retrieved recipe scores.
"""

import logging
import os

_level = os.environ.get("LOG_LEVEL", "WARNING").upper()

logging.basicConfig(
    format="%(levelname)s [%(name)s] %(message)s",
    level=getattr(logging, _level, logging.WARNING),
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"recipe_agent.{name}")
