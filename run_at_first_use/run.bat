@echo off
rem Project Manager - start the server from the virtual environment.

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Run: python -m venv .venv
    echo Then: .venv\Scripts\python -m pip install -r requirements.txt
    exit /b 1
)

echo Starting Project Manager at http://127.0.0.1:8000
echo To stop: press Ctrl+C
echo.

.venv\Scripts\python server.py