"""Project file resource router (read / write / create / delete)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

from .errors import project_manager_error


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# REQUEST MODELS
# ============================================================

class FileWriteRequest(BaseModel):

    path: str

    content: str


class FileCreateRequest(BaseModel):

    path: str

    content: str = ""


# ============================================================
# READ FILE
# ============================================================

@router.get("/api/file/read")
def read_file(
    request: Request,
    path: str,
):
    """
    Read a project text file.

    Query params:
        path:
            Project-relative file path.
    """

    try:

        content = request.app.state.editor.open(
            path
        )
        return {
            "path": path,
            "content": content,
        }

    except Exception as error:

        raise project_manager_error(
            error
        )


# ============================================================
# WRITE FILE
# ============================================================

@router.put("/api/file/write")
def write_file(
    request: Request,
    payload: FileWriteRequest,
):
    """
    Create or overwrite a project text file.
    """

    try:

        return request.app.state.editor.save(
            payload.path,
            payload.content,
        )

    except Exception as error:

        raise project_manager_error(
            error
        )


# ============================================================
# CREATE FILE
# ============================================================

@router.post("/api/file/create")
def create_file(
    request: Request,
    payload: FileCreateRequest,
):
    """
    Create a new project file.
    """

    try:

        return request.app.state.editor.create_file(
            payload.path,
            payload.content,
        )

    except Exception as error:

        raise project_manager_error(
            error
        )


# ============================================================
# DELETE FILE
# ============================================================

@router.delete("/api/file/delete")
def delete_file(
    request: Request,
    path: str,
):
    """
    Delete a project file.

    Query params:
        path:
            Project-relative file path.
    """

    try:

        return request.app.state.editor.delete(
            path
        )

    except Exception as error:

        raise project_manager_error(
            error
        )
