"""
Project Manager operation layer.
=================================

This is the single controller that HTTP routers, the browser, and
the Python client all funnel through.

The controller does NOT implement filesystem logic. Every filesystem
operation is delegated to projectConfiguration.Project_files, which
remains the sovereign owner of the Project Manager filesystem.

    Router / Client
        ↓
    EditorInterface
        ↓
    Project_files
        ↓
    Filesystem
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from projectConfiguration import Project_files
from .events import EventBus
from .session import EditorManager


# ============================================================
# EDITOR INTERFACE
# ============================================================

class EditorInterface:
    """
    The Project Manager operation/interface layer.

    Provides a narrow set of high-level operations agents and the
    web editor can use. All filesystem work goes through
    Project_files.
    """

    def __init__(
        self,
        filesystem: Any = None,
        events: EventBus | None = None,
        sessions: EditorManager | None = None,
    ) -> None:

        # The Project Manager remains the filesystem authority.
        self.filesystem = (
            filesystem
            if filesystem is not None
            else Project_files
        )

        self.events = (
            events
            if events is not None
            else EventBus()
        )

        self.sessions = (
            sessions
            if sessions is not None
            else EditorManager()
        )

    # ========================================================
    # HEALTH / STATE
    # ========================================================

    def health(self) -> dict[str, Any]:
        """
        Project Manager health and project information.
        """

        return {
            "status": "healthy",
            "project": self.filesystem.read_project_info(),
            "root": str(self.filesystem.PROJECT_ROOT),
        }

    def tree(self) -> dict[str, Any]:
        """
        Project state: project info, root and filesystem tree.
        """

        try:

            import json

            return {
                "project": self.filesystem.read_project_info(),
                "root": str(self.filesystem.PROJECT_ROOT),
                "filesystem": self.filesystem.read_filesystem(),
            }

        except Exception as error:

            raise self._to_error(
                error
            )

    def sessions(self) -> list[dict[str, Any]]:
        """
        Snapshot of all connected interface sessions.
        """

        return self.sessions.snapshot()

    # ========================================================
    # READ / WRITE
    # ========================================================

    def open(
        self,
        path: str,
    ) -> str:
        """
        Open a project file and return its contents.

        Args:
            path:
                Project-relative file path.

        Returns:
            The file contents.

        Raises:
            ValueError / FileNotFoundError:
                Propagated from Project_files.
        """

        return self.filesystem.read_file(
            path
        )

    def save(
        self,
        path: str,
        content: str,
    ) -> dict[str, Any]:
        """
        Write file contents back to the project filesystem.

        Publishes a ``saved`` event on success.
        """

        self.filesystem.write_file(
            path,
            content,
        )

        self.events.publish(
            "saved",
            path=path,
        )

        return {
            "status": "saved",
            "path": path,
        }

    # ========================================================
    # CREATE
    # ========================================================

    def create_file(
        self,
        path: str,
        content: str = "",
    ) -> dict[str, Any]:
        """
        Create a new project file.

        Publishes a ``created`` event on success.
        """

        self.filesystem.create_file(
            path,
            content,
        )

        self.events.publish(
            "created",
            path=path,
        )

        return {
            "status": "created",
            "path": path,
        }

    def create_directory(
        self,
        path: str,
    ) -> dict[str, Any]:
        """
        Create a new project directory.

        Publishes a ``created`` event on success.
        """

        self.filesystem.create_directory(
            path
        )

        self.events.publish(
            "created",
            path=path,
        )

        return {
            "status": "created",
            "path": path,
        }

    # ========================================================
    # RENAME
    # ========================================================

    def rename(
        self,
        old_path: str,
        new_path: str,
    ) -> dict[str, Any]:
        """
        Rename or move a project file/directory.

        Publishes a ``renamed`` event on success.
        """

        self.filesystem.rename_path(
            old_path,
            new_path,
        )

        self.events.publish(
            "renamed",
            path=new_path,
            old_path=old_path,
        )

        return {
            "status": "renamed",
            "old_path": old_path,
            "new_path": new_path,
        }

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        path: str,
    ) -> dict[str, Any]:
        """
        Delete a project file or directory.

        Publishes a ``deleted`` event on success.
        """

        self.filesystem.delete_path(
            path
        )

        self.events.publish(
            "deleted",
            path=path,
        )

        return {
            "status": "deleted",
            "path": path,
        }

    # ========================================================
    # ERROR MAPPING
    # ========================================================

    # Kept on the controller so every interface shares the same
    # error behaviour. See routers/error.py for the HTTP mapping.
    _to_error = staticmethod(
        lambda error: error
    )
