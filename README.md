# Project Manager

A lightweight FastAPI workspace server. Browse and edit project files from a
web dashboard with a Monaco-powered code editor.

## Features

- Project tree browser (browse, open, create, rename, delete)
- In-browser code editor with syntax highlighting
- JSON REST API for filesystem operations
- Works on Windows and (Chromebook) Linux

## Requirements

- Python 3.9+
- Network access for the code editor CDN (Monaco, loaded from cdnjs)

## Setup

### Windows

```bat
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
run.bat
```

### Chromebook (ChromeOS with Linux/Crostini)

Open a Linux terminal and enable the Linux apps if you have not already:

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

Clone the repo, then:

```sh
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

| Method | Path                       | Description                |
| ------ | -------------------------- | -------------------------- |
| GET    | `/`                        | Dashboard UI               |
| GET    | `/editor`                  | Standalone editor UI       |
| GET    | `/api/health`              | Health + project info      |
| GET    | `/api/project`             | Project state + tree       |
| GET    | `/api/file/read?path=...`  | Read a file                |
| PUT    | `/api/file/write`          | Write a file               |
| POST   | `/api/file/create`         | Create a file              |
| POST   | `/api/directory/create`    | Create a directory         |
| PUT    | `/api/path/rename`         | Rename/move a path         |
| DELETE | `/api/file/delete?path=...`| Delete a file              |
| DELETE | `/api/directory/delete?path=...` | Delete a directory         |

Note: The `data/`, `config/`, `documentation/`, etc. folders are empty so git
does not track them; the server recreates them automatically on startup.