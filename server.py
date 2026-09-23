"""Project Manager Server - application entry point.

Slim FastAPI host. The Project Manager remains the filesystem
authority (projectConfiguration.Project_files); this file only
assembles routers and the static workspace.

The controller is the single shared resource responsible for
turning Project Manager operations into HTTP contracts.

    routers/project.py        Project state, health, sessions
    routers/files.py          File CRUD / REST
    routers/directories.py    Directory CRUD
    routers/paths.py          Rename / move
    routers/ws.py             Real-time WebSocket interface
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from projectConfiguration import Project_files

from routers.project import router as project_router
from routers.files import router as files_router
from routers.directories import router as directories_router
from routers.paths import router as paths_router
from routers.ws import router as ws_router

from editor.defaults import get_interface, get_events, get_sessions


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
# APPLICATION FACTORY
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Build the basic project filesystem on startup.
    """

    Project_files.build_project_filesystem()

    yield


def create_app() -> FastAPI:
    """
    Assemble the Project Manager application.
    """

    app = FastAPI(
        title="Project Manager Server",
        description="Lightweight Project Manager workspace server.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # --------------------------------------------------------
    # Shared interface state
    # --------------------------------------------------------

    app.state.editor = get_interface()
    app.state.events = get_events()
    app.state.sessions = get_sessions()

    # --------------------------------------------------------
    # Routers
    # --------------------------------------------------------

    app.include_router(project_router)
    app.include_router(files_router)
    app.include_router(directories_router)
    app.include_router(paths_router)
    app.include_router(ws_router)

    # --------------------------------------------------------
    # Static workspace
    # --------------------------------------------------------

    if STATIC_DIR.is_dir():

        app.mount(
            "/static",
            StaticFiles(directory=STATIC_DIR),
            name="static",
        )

    @app.get("/")
    def home():
        return FileResponse(INDEX_HTML)

    @app.get("/editor")
    def editor():
        return FileResponse(EDITOR_HTML)

    return app


# ============================================================
# APPLICATION INSTANCE
# ============================================================

app = create_app()


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
