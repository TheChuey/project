# Plan: Project Manager Interface

Python module + organized server CRUD + modular UI.

## Goal

Keep the application as a **Project Manager** while adding a proper interface that allows AI agents and other Python programs to communicate with the Project Manager.

The Project Manager remains responsible for:

- project files
- directories
- file editing
- project configuration
- filesystem safety
- project initialization
- web UI

The new interface becomes another way to interact with those existing Project Manager capabilities.

The interface must **not bypass `Project_files.py`**.

## Architecture

```text
                         PROJECT MANAGER
                               │
              ┌────────────────┴────────────────┐
              │                                 │
        Web Interface                    Python Interface
              │                                 │
        Browser / Monaco                 AI Agents / Scripts
              │                                 │
              └────────────────┬────────────────┘
                               │
                        Project Manager
                        operation layer
                               │
                        Project_files.py
                               │
                        Project filesystem
```

The important principle is:

> There is one Project Manager and multiple interfaces to it.

## Target Structure

```text
project/
├── documentation/
│   └── MASTER_COPY.md
│
├── editor/
│   ├── __init__.py
│   ├── events.py
│   ├── session.py
│   └── operations.py
│
├── routers/
│   ├── __init__.py
│   ├── project.py
│   ├── files.py
│   ├── directories.py
│   ├── paths.py
│   └── ws.py
│
├── projectConfiguration/
│   ├── __init__.py
│   ├── Project_files.py
│   └── project.json
│
├── static/
│   ├── index.html
│   ├── editor.html
│   └── js/
│       ├── api.js
│       ├── session.js
│       ├── tree.js
│       ├── editor.js
│       └── main.js
│
├── editor_client.py
├── server.py
├── requirements.txt
└── ...
```

## Components

### 1. `editor/` — Project Manager operation/interface layer

This is the internal layer between the HTTP API and the filesystem.

It is **not a replacement for the Project Manager**.

It provides a clean set of operations that multiple interfaces can use.

#### `operations.py`

Create a controller such as `EditorInterface`.

It provides operations such as:

```text
open()
save()
create_file()
create_directory()
rename()
delete()
tree()
sessions()
```

Every filesystem mutation eventually goes through `Project_files.py`.

The controller should not implement its own filesystem logic.

Conceptually:

```text
Router
   ↓
Project Manager Interface
   ↓
Project_files
   ↓
Filesystem
```

### 2. `events.py` — Project Manager event system

Create a small event bus for changes occurring inside the Project Manager.

Example events:

```text
saved
created
renamed
deleted
tree_changed
```

Example:

```json
{
    "type": "saved",
    "path": "app.py"
}
```

The event system allows the browser and future agents to receive information about changes without directly monitoring the filesystem.

### 3. `session.py` — Interface sessions

Create:

```text
EditorSession
EditorManager
```

`EditorSession` tracks a connected interface client.

Possible state:

```text
client_id
open_file
dirty
last_modified
```

`EditorManager` maintains the active in-memory sessions.

It should also provide:

```text
register()
unregister()
update()
snapshot()
```

This is initially an in-memory system. Do not introduce a database for sessions.

### 4. `routers/` — Project Manager HTTP API

Split the existing API into resource-oriented routers.

#### `project.py`

```text
GET /api/project
GET /api/health
GET /api/sessions
```

#### `files.py`

```text
GET    /api/file/read
PUT    /api/file/write
POST   /api/file/create
DELETE /api/file/delete
```

#### `directories.py`

```text
POST   /api/directory/create
DELETE /api/directory/delete
```

#### `paths.py`

```text
PUT /api/path/rename
```

#### `ws.py`

```text
WS /api/ws
```

The existing REST paths and contracts remain unchanged.

### 5. WebSocket Interface

Add:

```text
/api/ws
```

The WebSocket provides real-time Project Manager events.

On connection:

```text
register session
```

Client messages may include:

```text
open
dirty
tree
```

Server events may include:

```text
saved
created
renamed
deleted
tree_changed
```

Example:

```json
{
    "type": "created",
    "path": "config/settings.json"
}
```

The browser can then update itself without requiring a complete page reload.

### 6. `editor_client.py` — Python Project Manager Interface

Create a Python client that allows another Python program or AI agent to communicate with the running Project Manager.

```python
from editor_client import EditorClient

client = EditorClient("http://127.0.0.1:8000")

client.tree()

client.open("app.py")

client.save(
    "app.py",
    "print('Hello World')"
)
```

Supported operations:

```text
open()
save()
create_file()
create_directory()
rename()
delete()
tree()
health()
sessions()
```

The client communicates with the Project Manager API. It must **not directly access the Project Manager filesystem**. This is important because the Project Manager remains the authority over filesystem operations.

### 7. Async Client

Provide an asynchronous client for AI-agent workflows:

```text
AsyncEditorClient
```

with asynchronous versions of the Project Manager operations.

Also provide:

```text
subscribe()
```

for receiving Project Manager events through WebSockets. This allows future agents to react to changes.

Example concept:

```text
AI Agent
   │
   ├── save file
   │
   ▼
Project Manager
   │
   ├── filesystem change
   │
   └── event
          │
          ▼
       Agent
```

### 8. Frontend Organization

The Project Manager UI remains visually and functionally the same. The JavaScript is reorganized into vanilla ES modules.

```text
static/js/
├── api.js
├── session.js
├── tree.js
├── editor.js
└── main.js
```

#### `api.js`

Central location for API requests. Responsible for:

```text
health
project
file operations
directory operations
rename
delete
sessions
```

#### `tree.js`

Responsible for:

- rendering the project tree
- selecting files
- refreshing the tree
- responding to tree-change events

#### `editor.js`

Responsible for Monaco. Move the existing Monaco initialization and behavior here with the goal of preserving it verbatim where practical. Keep:

- Monaco configuration
- editor initialization
- syntax highlighting
- save behavior
- Ctrl+S
- dirty state
- theme
- sidebar behavior

#### `session.js`

Responsible for:

- WebSocket connection
- connection state
- sending session events
- receiving Project Manager events
- applying live changes

#### `main.js`

Responsible for application startup and wiring the modules together.

### 9. `server.py`

After the reorganization, `server.py` becomes the application entry point:

```text
create FastAPI application
        ↓
configure lifespan
        ↓
register routers
        ↓
serve static files
        ↓
start server
```

It should not become the location for Project Manager business logic.

## Requirements

Add:

```text
httpx
websockets
```

to `requirements.txt`. Keep the existing FastAPI and Uvicorn dependencies.

## What Does NOT Change

The following remain Project Manager responsibilities:

```text
Project_files.py
project.json
project initialization
filesystem safety
dashboard
Monaco editor
existing REST endpoints
project structure
Windows support
Linux/ChromeOS support
```

The interface adds capability; it does not replace these systems.

## Interface Principle

The interface must provide agents with a controlled Project Manager API. An agent should think in terms of:

```text
open project file
read project file
save project file
create project file
create directory
rename path
delete path
inspect project tree
```

rather than:

```text
open arbitrary filesystem path
write arbitrary filesystem path
delete arbitrary filesystem path
```

The Project Manager remains the authority.

## Verification

### 1. Application startup

```text
python server.py
```

Verify the server starts successfully.

### 2. Existing API

Verify all existing contracts continue working:

```text
/api/health
/api/project
/api/file/read
/api/file/write
/api/file/create
/api/file/delete
/api/directory/create
/api/directory/delete
/api/path/rename
```

### 3. Browser

Verify:

- dashboard loads
- project tree loads
- files open
- Monaco works
- editing works
- Ctrl+S works
- file creation works
- rename works
- deletion works

The UI should remain visually/functionally equivalent.

### 4. Real-Time Events

Open the Project Manager in a browser, then modify the project through another client. Verify the browser receives the appropriate event.

Examples:

```text
create → created
save → saved
rename → renamed
delete → deleted
```

### 5. Python Client

Run a test script:

```text
health
tree
create
open
save
rename
delete
```

Verify each operation goes through the Project Manager.

### 6. Filesystem Authority

Confirm that `editor_client.py`, `routers/`, `editor/` do not bypass `Project_files.py` for Project Manager filesystem operations.

## Final Architecture

```text
                    ┌─────────────────────┐
                    │   Project Manager   │
                    │       Server        │
                    └──────────┬──────────┘
                               │
                    Project Manager Core
                               │
                    ┌──────────▼──────────┐
                    │    Project_files    │
                    │  Filesystem Owner   │
                    └──────────┬──────────┘
                               │
                         Project Root
                               ▲
                               │
              ┌────────────────┴────────────────┐
              │                                 │
       Browser Interface                 Python Interface
              │                                 │
       Monaco / Dashboard                 editor_client.py
              │                                 │
              │                           AI Agents
              │                           Python Scripts
              │                                 │
              └──────────────┬──────────────────┘
                             │
                       Project Manager
                         HTTP / WS API
```

The central idea is:

> **Project Manager first. Interface second.**