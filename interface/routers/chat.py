"""
Project Manager chat router (stub).
====================================

Chat stub for the interface. Messages are appended to a plaintext
log file inside the managed workspace (``workspace/data/chat.log``)
so history survives reloads. This is a placeholder surface: a real
AI agent can replace the handler later without changing the API
shape (``POST /api/chat`` to send, ``GET /api/chat`` to fetch).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

from parameters import filesystem

from .errors import project_manager_error


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatMessage(BaseModel):

    message: str


# ============================================================
# CHAT LOG HELPERS
# ============================================================

MAX_MESSAGE_LENGTH = 2000

DEFAULT_LIMIT = 50

MAX_LIMIT = 500


def _log_path() -> Any:
    """
    Safe path to the chat log inside the managed workspace.
    """

    return filesystem.resolve_project_path(
        "data/chat.log"
    )


def _append_message(message: str) -> dict[str, Any]:
    """
    Append one timestamped message to the chat log.

    The data directory is created on demand.
    """

    log_path = _log_path()

    log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "sender": "user",
        "message": message,
    }

    with log_path.open(
        "a",
        encoding="utf-8",
    ) as handle:

        handle.write(
            json.dumps(entry) + "\n"
        )

    return entry


def _read_history(limit: int) -> list[dict[str, Any]]:
    """
    Read the most recent chat log entries in chronological order.
    """

    log_path = _log_path()

    if not log_path.exists():

        return []

    entries: list[dict[str, Any]] = []

    with log_path.open(
        "r",
        encoding="utf-8",
    ) as handle:

        for line in handle:

            line = line.strip()

            if not line:
                continue

            try:

                entries.append(
                    json.loads(line)
                )

            except json.JSONDecodeError:
                continue

    return entries[-limit:]


# ============================================================
# SEND MESSAGE
# ============================================================

@router.post("/api/chat")
def send_chat_message(
    request: Request,
    payload: ChatMessage,
):
    """
    Log a chat message.

    The stub currently records the message; a future agent
    provider can reply through the same endpoint.
    """

    message = payload.message.strip()

    if not message:

        raise project_manager_error(
            ValueError(
                "Chat message cannot be empty."
            )
        )

    if len(message) > MAX_MESSAGE_LENGTH:

        raise project_manager_error(
            ValueError(
                f"Chat message is too long "
                f"(max {MAX_MESSAGE_LENGTH} characters)."
            )
        )

    try:

        entry = _append_message(message)

        return {
            "status": "logged",
            "entry": entry,
        }

    except Exception as error:

        raise project_manager_error(
            error
        )


# ============================================================
# FETCH HISTORY
# ============================================================

@router.get("/api/chat")
def get_chat_history(
    request: Request,
    limit: int = DEFAULT_LIMIT,
):
    """
    Return the most recent chat entries.

    Query params:
        limit:
            Maximum number of entries to return.
    """

    limit = max(1, min(limit, MAX_LIMIT))

    try:

        return {
            "entries": _read_history(limit),
        }

    except Exception as error:

        raise project_manager_error(
            error
        )