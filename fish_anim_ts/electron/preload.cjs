const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  onMousePosition: (callback) => {
    ipcRenderer.on('mouse-position', (_event, pos) => callback(pos));
  },
});
