/* Chat popup module */
import API from './api.js';
import Session from './session.js';

const log = document.getElementById('chatLog');
const form = document.getElementById('chatForm');
const input = document.getElementById('chatInput');
const sendBtn = document.getElementById('chatSend');
const status = document.getElementById('chatStatus');

function appendLine(role, text, meta = '') {
  const line = document.createElement('div');
  line.className = 'msg ' + role;
  const label = document.createElement('span');
  label.className = 'msg-label';
  label.textContent = role === 'user' ? 'You' : role === 'event' ? 'Event' : 'System';
  const body = document.createElement('span');
  body.className = 'msg-body';
  body.textContent = text;
  line.appendChild(label);
  line.appendChild(body);
  if (meta) {
    const ts = document.createElement('span');
    ts.className = 'msg-meta';
    ts.textContent = meta;
    line.appendChild(ts);
  }
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
}

function setStatus(text) {
  if (status) status.textContent = text;
}

async function loadHistory() {
  try {
    const data = await API.chatHistory();
    const entries = data.entries || [];
    if (!entries.length) {
      appendLine('system', 'No messages yet. Say hello!');
      return;
    }
    for (const entry of entries) {
      const ts = entry.ts ? new Date(entry.ts).toLocaleTimeString() : '';
      appendLine(entry.sender === 'user' ? 'user' : 'system', entry.message, ts);
    }
  } catch (error) {
    setStatus('Failed to load history: ' + error.message);
  }
}

async function sendMessage() {
  const message = input.value.trim();
  if (!message) return;
  input.value = '';
  appendLine('user', message, new Date().toLocaleTimeString());
  setStatus('Logging…');
  try {
    await API.chatSend(message);
    setStatus('Message logged.');
  } catch (error) {
    setStatus('Send failed: ' + error.message);
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  sendMessage();
});

sendBtn.addEventListener('click', sendMessage);

Session.onEvent = (msg) => {
  if (msg.type === 'event' && msg.event) {
    const ev = msg.event;
    const what = ev.type || 'event';
    const path = ev.path || '';
    appendLine('event', what + (path ? ': ' + path : ''));
  }
};

loadHistory();
Session.connect();