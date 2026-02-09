const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  chooseAudio: () => ipcRenderer.invoke("choose-audio"),
  saveRecording: (buffer, ext) => ipcRenderer.invoke("save-recording", { buffer, ext }),
  transcribeFile: (payload) => ipcRenderer.invoke("transcribe-file", payload),
  saveResults: (payload) => ipcRenderer.invoke("save-results", payload),
  onLog: (handler) => ipcRenderer.on("log", (_event, message) => handler(message)),
});
