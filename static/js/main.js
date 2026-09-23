/* Main application wiring */
import API from './api.js';
import Session from './session.js';
import Tree from './tree.js';
import Editor from './editor.js';

let currentFile = null;
let currentLanguage = 'plaintext';
let isDirty = false;

function getLanguage(filePath) {
  if (!filePath) return 'plaintext';
  const ext = filePath.split('.').pop().toLowerCase();
  const map = {
    py: 'python',
    js: 'javascript',
    jsx: 'javascript',
    ts: 'typescript',
    tsx: 'typescript',
    html: 'html',
    htm: 'html',
    css: 'css',
    json: 'json',
    md: 'markdown',
    yaml: 'yaml',
    yml: 'yaml',
    sql: 'sql',
    xml: 'xml',
    sh: 'shell',
    env: 'shell',
    txt: 'plaintext'
  };
  return map[ext] || 'plaintext';
}

function setStatus(msg) {
  const el = document.getElementById('statusMessage');
  if (el) el.textContent = msg;
}

function updateFileDisplay() {
  const cf = document.getElementById('currentFile');
  if (cf) cf.textContent = currentFile ? currentFile : 'No file selected';
  const lang = document.getElementById('language');
  if (lang) lang.textContent = currentLanguage;
  const dirty = document.getElementById('unsavedIndicator');
  if (dirty) dirty.textContent = isDirty ? '● UNSAVED' : '';
}

async function openFile(filePath) {
  if (isDirty) {
    const proceed = confirm('You have unsaved changes. Open another file?');
    if (!proceed) return;
  }
  setStatus('Opening ' + filePath + '...');
  try {
    const data = await API.fileRead(filePath);
    currentFile = filePath;
    currentLanguage = getLanguage(filePath);
    Editor.setValue(data.content || '');
    Editor.setLanguage(currentLanguage);
    isDirty = false;
    updateFileDisplay();
    Tree.setSelected(filePath);
    setStatus('Opened ' + filePath);
  } catch (error) {
    setStatus('Error: ' + error.message);
    alert(error.message);
  }
}

async function saveFile() {
  if (!currentFile) {
    alert('No file is currently open.');
    return;
  }
  setStatus('Saving...');
  try {
    await API.fileWrite(currentFile, Editor.getValue());
    isDirty = false;
    updateFileDisplay();
    setStatus('Saved ' + currentFile);
    await Tree.refresh();
  } catch (error) {
    setStatus('Save error: ' + error.message);
    alert(error.message);
  }
}

async function newFile() {
  const fileName = prompt('Enter new file path/name:');
  if (!fileName) return;
  try {
    await API.fileCreate(fileName, '');
    await Tree.refresh();
    await openFile(fileName);
    setStatus('Created ' + fileName);
  } catch (error) {
    alert(error.message);
  }
}

async function newFolder() {
  const folderPath = prompt('Enter new folder path:');
  if (!folderPath) return;
  try {
    await API.directoryCreate(folderPath);
    await Tree.refresh();
    setStatus('Created folder ' + folderPath);
  } catch (error) {
    alert(error.message);
  }
}

async function renameSelected() {
  if (!currentFile) {
    alert('Select a file first.');
    return;
  }
  const newName = prompt('Enter the new file path:', currentFile);
  if (!newName || newName === currentFile) return;
  try {
    await API.pathRename(currentFile, newName);
    currentFile = newName;
    await Tree.refresh();
    await openFile(newName);
  } catch (error) {
    alert(error.message);
  }
}

async function deleteSelected() {
  if (!currentFile) {
    alert('Select a file first.');
    return;
  }
  const confirmed = confirm('Delete ' + currentFile + '?');
  if (!confirmed) return;
  try {
    await API.fileDelete(currentFile);
    currentFile = null;
    Editor.setValue('');
    isDirty = false;
    updateFileDisplay();
    await Tree.refresh();
    setStatus('File deleted.');
  } catch (error) {
    alert(error.message);
  }
}

async function refreshTree() {
  await Tree.refresh();
}

function goHome() {
  if (isDirty) {
    const proceed = confirm('You have unsaved changes. Return to home?');
    if (!proceed) return;
  }
  window.location.href = '/';
}

function init() {
  Editor.init().then(() => {
    Editor.onChange(() => {
      if (currentFile) {
        isDirty = true;
        updateFileDisplay();
      }
    });

    Tree.onFileSelect = openFile;

    document.getElementById('saveBtn')?.addEventListener('click', saveFile);
    document.getElementById('newFileBtn')?.addEventListener('click', newFile);
    document.getElementById('newFolderBtn')?.addEventListener('click', newFolder);
    document.getElementById('renameBtn')?.addEventListener('click', renameSelected);
    document.getElementById('deleteBtn')?.addEventListener('click', deleteSelected);
    document.getElementById('refreshBtn')?.addEventListener('click', refreshTree);
    document.getElementById('homeBtn')?.addEventListener('click', goHome);

    document.addEventListener('keydown', (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
        event.preventDefault();
        saveFile();
      }
    });

    const sidebar = document.getElementById('sidebar');
    const resizeHandle = document.getElementById('resizeHandle');
    if (resizeHandle && sidebar) {
      let resizing = false;
      resizeHandle.addEventListener('mousedown', () => { resizing = true; document.body.style.cursor = 'col-resize'; });
      document.addEventListener('mousemove', (e) => {
        if (!resizing) return;
        const width = e.clientX;
        if (width >= 180 && width <= 500) {
          sidebar.style.width = width + 'px';
          Editor.layout();
        }
      });
      document.addEventListener('mouseup', () => { resizing = false; document.body.style.cursor = ''; });
    }

    window.addEventListener('beforeunload', (event) => {
      if (!isDirty) return;
      event.preventDefault();
      event.returnValue = '';
    });

    setStatus('Ready');
    Tree.load().then(() => {
      const urlParams = new URLSearchParams(window.location.search);
      const initialPath = urlParams.get('path');
      if (initialPath) openFile(initialPath);
    });
  }).catch((e) => {
    setStatus('Error: ' + e.message);
  });

  Session.connect();
}

document.addEventListener('DOMContentLoaded', init);

export { openFile, saveFile, newFile, newFolder, renameSelected, deleteSelected, refreshTree, goHome, currentFile, isDirty };
