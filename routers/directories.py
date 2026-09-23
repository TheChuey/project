"""Project directory resource router (create / delete)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from .errors import project_manager_error


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# CREATE DIRECTORY
# ============================================================

@router.post("/api/directory/create")
def create_directory(
    request: Request,
    path: str,
):
    """
    Create a project directory.

    Query params:
        path:
            Project-relative directory path.
    """

    try:

        return request.app.state.editor.create_directory(
            path
        )

    except Exception as error:

        raise project_manager_error(
            error
        )


# ============================================================
# DELETE DIRECTORY
# ============================================================

@router.delete("/api/directory/delete")
def delete_directory(
    request: Request,
    path: str,
):
    """
    Delete a project directory.

    Query params:
        path:
            Project-relative directory path.
    """

    try:

        return request.app.state.editor.delete(
            path
        )

    except Exception as error:

        raise project_manager_error(
            error
        )
