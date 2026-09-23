"""
Project Manager HTTP API helpers.
==================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import HTTPException

from projectConfiguration import Project_files
from editor.defaults import get_interface


# ============================================================
# SHARED CONTROLLER
# ============================================================

def controller() -> Any:
    """
    The single shared Project Manager interface instance.
    """

    return get_interface()
