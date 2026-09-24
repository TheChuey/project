# Project Manager

A lightweight FastAPI workspace server. Browse, edit, and chat about your
project from a single web dashboard with a Monaco-powered code editor.

## Layout

The repository is split into three pillars plus scripts:

```
├── server.py                Application entry point (FastAPI host)
├── requirements.txt
│
├── interface/               EDITOR INTERFACE
│   ├── static/              Web UI (home.html, chat.html, editor.html, js/)
│   ├── routers/             HTTP API routers (files, dirs, paths, ws, chat)
│   ├── core/                Controller layer (sessions, events, operations)
│   └── clients/             Python client (EditorClient / AsyncEditorClient)
│
├── parameters/              PROJECT PARAMETERS
│   └── filesystem.py        Filesystem owner for the managed workspace
│
├── workspace/               THE MANAGED PROJECT
│   ├── project.json
│   ├── documentation/  project_scope/  to_do/  updates/  config/  data/
│
└── scripts/                 run.bat / run.sh / setup.sh
```

The dashboard and editor operate in two scopes:

- **Workspace** — the managed project (`workspace/`). Default.
- **Dev** — the application's own scripts (`server.py`, `interface/`, …). Reach
  them via the "Dev scripts" quick links in the sidebar or the Dev scope toggle,
  so app code only shows up when you need it.

## Features

- Unified home page: project tree + Monaco editor + scope toggle
- Collapsible folder tree (folders start collapsed, VS Code style)
- Per-file-type icons (Python, HTML, CSS, JS/TS, Markdown, config, …)
- Chat popup (`/chat`) — stub that logs messages to `workspace/data/chat.log`
- Dev-scripts quick links to the important application files
- JSON REST API for filesystem operations (scope-aware)
- Python client for AI agents / other programs
- Works on Windows and (Chromebook) Linux

## Requirements

- Python 3.9+
- Network access for the code editor CDN (Monaco, loaded from cdnjs)

## Setup

### Windows

```bat
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
scripts\run.bat
```

### Chromebook (ChromeOS with Linux/Crostini)

Open a Linux terminal and enable the Linux apps if you have not already:

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

Clone the repo, then:

```sh
cd scripts
./setup.sh
./run.sh
```

Then open `http://127.0.0.1:8000` in the Chrome browser. On ChromeOS the
browser can reach the Linux container through `127.0.0.1`.

## Configuration

The server binds to `127.0.0.1:8000` by default. Override with environment
variables:

```sh
PROJECT_MANAGER_HOST=0.0.0.0 PROJECT_MANAGER_PORT=8080 ./run.sh
```

## API overview

| Method | Path                          | Description                          |
| ------ | ----------------------------- | ------------------------------------ |
| GET    | `/`                           | Unified home UI (tree + editor)      |
| GET    | `/chat`                       | Chat popup UI                        |
| GET    | `/api/health`                 | Health + project info                |
| GET    | `/api/project?scope=`         | Project state + tree (ws/app)        |
| GET    | `/api/file/read?path=&scope=` | Read a file                          |
| PUT    | `/api/file/write`             | Write a file                         |
| POST   | `/api/file/create`            | Create a file                        |
| POST   | `/api/directory/create`       | Create a directory                   |
| PUT    | `/api/path/rename`            | Rename/move a path                   |
| DELETE | `/api/file/delete`            | Delete a file                        |
| DELETE | `/api/directory/delete`       | Delete a directory                   |
| POST   | `/api/chat`                   | Send a chat message (logged)         |
| GET    | `/api/chat`                   | Chat history                         |

Note: The `workspace/` content folders are empty so git does not track
them; the server recreates them automatically on startup.