/* Project Manager API client module */
const API = {
  async request(method, url, body = null) {
    const options = { method };
    if (body) {
      options.headers = { 'Content-Type': 'application/json' };
      options.body = JSON.stringify(body);
    }
    const res = await fetch(url, options);
    if (!res.ok) {
      let detail = '';
      try {
        const err = await res.json();
        detail = err.detail || '';
      } catch (e) {
        detail = '';
      }
      throw new Error(detail || `Request failed: ${res.status}`);
    }
    if (res.status === 204 || !res.headers.get('content-type')?.includes('application/json')) {
      return {};
    }
    return res.json();
  },

  health() {
    return this.request('GET', '/api/health');
  },

  project() {
    return this.request('GET', '/api/project');
  },

  fileRead(path) {
    return this.request('GET', `/api/file/read?path=${encodeURIComponent(path)}`);
  },

  fileWrite(path, content) {
    return this.request('PUT', '/api/file/write', { path, content });
  },

  fileCreate(path, content = '') {
    return this.request('POST', '/api/file/create', { path, content });
  },

  fileDelete(path) {
    return this.request('DELETE', `/api/file/delete?path=${encodeURIComponent(path)}`);
  },

  directoryCreate(path) {
    return this.request('POST', `/api/directory/create?path=${encodeURIComponent(path)}`);
  },

  directoryDelete(path) {
    return this.request('DELETE', `/api/directory/delete?path=${encodeURIComponent(path)}`);
  },

  pathRename(oldPath, newPath) {
    return this.request('PUT', '/api/path/rename', { old_path: oldPath, new_path: newPath });
  },

  sessions() {
    return this.request('GET', '/api/sessions');
  }
};

export default API;
