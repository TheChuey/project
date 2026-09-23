"""
Project Manager Server
======================

Lightweight FastAPI server for the Project Manager workspace.

Responsibilities:
    - Start the project.
    - Initialize the filesystem.
    - Serve the browser interface.
    - Provide project information.
    - Provide filesystem information.
    - Read files.
    - Write files.
    - Create files.
    - Create directories.
    - Rename files/directories.
    - Delete files/directories.

Filesystem operations are handled by project_files.py.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

import Project_files


# ============================================================
# CONFIGURATION
# ============================================================

HOST = os.environ.get(
    "PROJECT_MANAGER_HOST",
    "127.0.0.1",
)

PORT = int(
    os.environ.get(
        "PROJECT_MANAGER_PORT",
        "8000",
    )
)

PROJECT_ROOT = Path(__file__).resolve().parent

STATIC_DIR = PROJECT_ROOT / "static"

INDEX_HTML = STATIC_DIR / "index.html"

EDITOR_HTML = STATIC_DIR / "editor.html"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    Build the basic project filesystem when
    the server starts.
    """

    Project_files.build_project_filesystem()

    yield


app = FastAPI(
    title="Project Manager Server",
    description="Lightweight Project Manager workspace server.",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# REQUEST MODELS
# ============================================================

class FileWriteRequest(BaseModel):

    path: str

    content: str


class FileCreateRequest(BaseModel):

    path: str

    content: str = ""


class RenameRequest(BaseModel):

    old_path: str

    new_path: str


# ============================================================
# ERROR HELPER
# ============================================================

def filesystem_error(
    error: Exception,
) -> HTTPException:
    """
    Convert filesystem exceptions into HTTP errors.
    """

    if isinstance(
        error,
        FileNotFoundError,
    ):

        return HTTPException(
            status_code=404,
            detail=str(error),
        )

    if isinstance(
        error,
        FileExistsError,
    ):

        return HTTPException(
            status_code=409,
            detail=str(error),
        )

    if isinstance(
        error,
        ValueError,
    ):

        return HTTPException(
            status_code=400,
            detail=str(error),
        )

    return HTTPException(
        status_code=500,
        detail=str(error),
    )


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    """
    Display the main project interface.
    """

    if not INDEX_HTML.exists():

        raise HTTPException(
            status_code=404,
            detail="static/index.html was not found.",
        )

    return FileResponse(
        INDEX_HTML
    )


# ============================================================
# EDITOR
# ============================================================

@app.get("/editor")
def editor():
    """
    Display the standalone editor.
    """

    if not EDITOR_HTML.exists():

        raise HTTPException(
            status_code=404,
            detail="static/editor.html was not found.",
        )

    return FileResponse(
        EDITOR_HTML
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():
    """
    Check server health.
    """

    return {
        "status": "healthy",
        "project": Project_files.read_project_info(),
    }


# ============================================================
# PROJECT STATE
# ============================================================

@app.get("/api/project")
def get_project():
    """
    Return project information and filesystem tree.
    """

    return Project_files.get_project_state()


# ============================================================
# READ FILE
# ============================================================

@app.get("/api/file/read")
def read_file(path: str):
    """
    Read a project text file.
    """

    try:

        content = Project_files.read_file(
            path
        )

        return {
            "path": path,
            "content": content,
        }

    except Exception as error:

        raise filesystem_error(
            error
        )


# ============================================================
# WRITE FILE
# ============================================================

@app.put("/api/file/write")
def write_file(
    request: FileWriteRequest,
):
    """
    Create or overwrite a project text file.
    """

    try:

        Project_files.write_file(
            request.path,
            request.content,
        )

        return {
            "status": "saved",
            "path": request.path,
        }

    except Exception as error:

        raise filesystem_error(
            error
        )


# ============================================================
# CREATE FILE
# ============================================================

@app.post("/api/file/create")
def create_file(
    request: FileCreateRequest,
):
    """
    Create a new project file.
    """

    try:

        Project_files.create_file(
            request.path,
            request.content,
        )

        return {
            "status": "created",
            "path": request.path,
        }

    except Exception as error:

        raise filesystem_error(
            error
        )


# ============================================================
# CREATE DIRECTORY
# ============================================================

@app.post("/api/directory/create")
def create_directory(
    path: str,
):
    """
    Create a project directory.
    """

    try:

        Project_files.create_directory(
            path
        )

        return {
            "status": "created",
            "path": path,
        }

    except Exception as error:

        raise filesystem_error(
            error
        )


# ============================================================
# RENAME
# ============================================================

@app.put("/api/path/rename")
def rename_path(
    request: RenameRequest,
):
    """
    Rename or move a project file/directory.
    """

    try:

        Project_files.rename_path(
            request.old_path,
            request.new_path,
        )

        return {
            "status": "renamed",
            "old_path": request.old_path,
            "new_path": request.new_path,
        }

    except Exception as error:

        raise filesystem_error(
            error
        )


# ============================================================
# DELETE FILE
# ============================================================

@app.delete("/api/file/delete")
def delete_file(
    path: str,
):
    """
    Delete a project file.
    """

    try:

        target = Project_files.resolve_project_path(
            path
        )

        if not target.exists():

            raise FileNotFoundError(
                "File not found."
            )

        if not target.is_file():

            raise ValueError(
                "Path is not a file."
            )

        Project_files.delete_path(
            path
        )

        return {
            "status": "deleted",
            "path": path,
        }

    except Exception as error:

        raise filesystem_error(
            error
        )


# ============================================================
# DELETE DIRECTORY
# ============================================================

@app.delete("/api/directory/delete")
def delete_directory(
    path: str,
):
    """
    Delete a project directory.
    """

    try:

        target = Project_files.resolve_project_path(
            path
        )

        if not target.exists():

            raise FileNotFoundError(
                "Directory not found."
            )

        if not target.is_dir():

            raise ValueError(
                "Path is not a directory."
            )

        Project_files.delete_path(
            path
        )

        return {
            "status": "deleted",
            "path": path,
        }

    except Exception as error:

        raise filesystem_error(
            error
        )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
    )
