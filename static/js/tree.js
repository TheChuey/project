/* Project tree rendering module */
import API from './api.js';

const Tree = {
  root: [],
  selectedPath: null,
  onFileSelect: null,

  async load() {
    const data = await API.project();
    this.root = data.filesystem || [];
    this.render();
  },

  render(containerId = 'tree') {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    this.renderItems(this.root, container);
  },

  renderItems(items, container) {
    for (const item of items) {
      const row = document.createElement('div');
      row.className = 'tree-item';
      if (item.type === 'directory') {
        row.classList.add('folder');
        row.textContent = '📁 ' + item.name;
        container.appendChild(row);
        const children = document.createElement('div');
        children.className = 'children';
        container.appendChild(children);
        this.renderItems(item.children || [], children);
      } else {
        row.textContent = '📄 ' + item.name;
        if (this.selectedPath === item.path) {
          row.classList.add('selected');
        }
        row.onclick = () => {
          this.selectedPath = item.path;
          if (this.onFileSelect) this.onFileSelect(item.path);
          this.render();
        };
        container.appendChild(row);
      }
    }
  },

  setSelected(path) {
    this.selectedPath = path;
    this.render();
  },

  refresh() {
    return this.load();
  }
};

export default Tree;
