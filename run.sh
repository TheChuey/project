#!/usr/bin/env bash
#
# Project Manager - start the server from the virtual environment.
#
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run ./setup.sh first." >&2
    exit 1
fi

echo "Starting Project Manager at http://127.0.0.1:8000"
echo "To stop: press Ctrl+C"
echo

.venv/bin/python server.py