const state = {
  audioPath: "",
  recording: null,
  chunks: [],
  outputs: { transcript: "", corrected: "", summary: "" },
};

const el = (id) => document.getElementById(id);

function setStatus(text, kind = "info") {
  const status = el("status");
  status.textContent = text;
  status.className = `status ${kind}`;
}

function setOutputs({ transcript, corrected, summary }) {
  const safe = {
    transcript: transcript || "",
    corrected: corrected || "",
    summary: summary || "",
  };
  state.outputs = safe;
  el("transcript").value = safe.transcript;
  el("corrected").value = safe.corrected;
  el("summary").value = safe.summary;
}

function appendLog(message) {
  const log = el("log");
  log.value += `${message}\n`;
  log.scrollTop = log.scrollHeight;
}

function clearLog() {
  el("log").value = "";
}

async function pickAudio() {
  const path = await window.api.chooseAudio();
  if (path) {
    state.audioPath = path;
    el("audioPath").textContent = path;
  }
}

async function startRecording() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    setStatus("Microfone nao suportado neste ambiente.", "error");
    return;
  }

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const recorder = new MediaRecorder(stream);
  state.chunks = [];

  recorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      state.chunks.push(event.data);
    }
  };

  recorder.onstop = async () => {
    const blob = new Blob(state.chunks, { type: recorder.mimeType });
    const buffer = await blob.arrayBuffer();
    const ext = recorder.mimeType.includes("ogg") ? "ogg" : "webm";
    const filePath = await window.api.saveRecording(buffer, ext);
    state.audioPath = filePath;
    el("audioPath").textContent = filePath;
    setStatus("Gravacao pronta. Clique em Transcrever.");
  };

  recorder.start();
  state.recording = recorder;
  document.body.classList.remove("record-stop");
  document.body.classList.add("recording");
  setStatus("Gravando... clique em Parar para finalizar.");
}

function stopRecording() {
  if (state.recording) {
    state.recording.stop();
    state.recording.stream.getTracks().forEach((t) => t.stop());
    state.recording = null;
  }
  document.body.classList.remove("recording");
  document.body.classList.add("record-stop");
  setTimeout(() => {
    document.body.classList.remove("record-stop");
  }, 1200);
}

async function transcribe() {
  const modelPath = el("modelPath").value.trim();
  const groqKey = el("groqKey").value.trim();

  if (!state.audioPath) {
    setStatus("Selecione um audio ou grave pelo microfone.", "error");
    return;
  }

  if (!modelPath) {
    setStatus("Informe o caminho do modelo Vosk.", "error");
    return;
  }

  if (!groqKey) {
    setStatus("Informe a GROQ_API_KEY.", "error");
    return;
  }

  setStatus("Processando: transcrevendo, corrigindo e resumindo...");
  clearLog();
  setOutputs({ transcript: "", corrected: "", summary: "" });

  try {
    const result = await window.api.transcribeFile({
      inputPath: state.audioPath,
      modelPath,
      groqKey,
    });
    setOutputs(result);
    setStatus("Finalizado com sucesso.", "success");
  } catch (err) {
    setStatus(err.message || "Falha ao processar.", "error");
  }
}

async function saveResults() {
  if (!state.outputs.transcript && !state.outputs.corrected && !state.outputs.summary) {
    setStatus("Nao ha resultados para salvar.", "error");
    return;
  }

  try {
    const saved = await window.api.saveResults(state.outputs);
    if (saved) {
      setStatus("Resultados salvos com sucesso.", "success");
      appendLog(`[app] Salvo em: ${saved.transcriptPath}`);
      appendLog(`[app] Salvo em: ${saved.correctedPath}`);
      appendLog(`[app] Salvo em: ${saved.summaryPath}`);
    }
  } catch (err) {
    setStatus(err.message || "Falha ao salvar resultados.", "error");
  }
}

el("pickAudio").addEventListener("click", pickAudio);
el("record").addEventListener("click", startRecording);
el("stop").addEventListener("click", stopRecording);
el("transcribe").addEventListener("click", transcribe);
el("saveResults").addEventListener("click", saveResults);

window.api.onLog((message) => {
  appendLog(message);
});

const settingsPanel = el("quickSettings");
const toggleSettings = el("toggleSettings");
toggleSettings.addEventListener("click", () => {
  settingsPanel.classList.toggle("hidden");
});

const groqInput = el("groqKey");
const savedGroqKey = localStorage.getItem("groqKey");
if (savedGroqKey) {
  groqInput.value = savedGroqKey;
}
groqInput.addEventListener("input", () => {
  localStorage.setItem("groqKey", groqInput.value.trim());
});
