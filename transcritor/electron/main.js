const { app, BrowserWindow, dialog, ipcMain } = require("electron");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const APP_ROOT = path.resolve(__dirname, "..");
const BUNDLED_PYTHON = path.join(APP_ROOT, "bundle", "python", "python.exe");
const PYTHON = fs.existsSync(BUNDLED_PYTHON) ? BUNDLED_PYTHON : (process.env.PYTHON || "python");
const BUNDLE_FFMPEG_DIR = path.join(APP_ROOT, "bundle", "ffmpeg", "bin");

let mainWindow = null;

function sendLog(message) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("log", message);
  }
}

function runPython(scriptPath, args, extraEnv = {}) {
  return new Promise((resolve, reject) => {
    const extraPath = fs.existsSync(BUNDLE_FFMPEG_DIR) ? BUNDLE_FFMPEG_DIR : "";
    const mergedPath = extraPath
      ? `${extraPath}${path.delimiter}${process.env.PATH || ""}`
      : process.env.PATH;
    const child = spawn(PYTHON, [scriptPath, ...args], {
      cwd: APP_ROOT,
      env: { ...process.env, ...extraEnv, PATH: mergedPath },
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (data) => {
      const text = data.toString();
      stdout += text;
      text.split(/\r?\n/).forEach((line) => {
        if (line.trim()) {
          sendLog(`[python] ${line}`);
        }
      });
    });
    child.stderr.on("data", (data) => {
      const text = data.toString();
      stderr += text;
      text.split(/\r?\n/).forEach((line) => {
        if (line.trim()) {
          sendLog(`[python][erro] ${line}`);
        }
      });
    });

    child.on("error", (err) => {
      reject(new Error(`Falha ao iniciar Python: ${err.message}`));
    });

    child.on("close", (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        const msg = stderr || stdout || `Python saiu com codigo ${code}`;
        reject(new Error(msg.trim()));
      }
    });
  });
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 750,
    webPreferences: {
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  win.loadFile(path.join(__dirname, "index.html"));
  mainWindow = win;
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

ipcMain.handle("choose-audio", async () => {
  const result = await dialog.showOpenDialog({
    title: "Selecionar audio",
    filters: [
      { name: "Audio", extensions: ["mp3", "wav", "webm", "m4a", "ogg"] },
    ],
    properties: ["openFile"],
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }
  return result.filePaths[0];
});

ipcMain.handle("save-recording", async (_event, payload) => {
  const { buffer, ext } = payload;
  const runDir = path.join(app.getPath("userData"), "runs");
  ensureDir(runDir);
  const filename = `gravacao_${Date.now()}.${ext || "webm"}`;
  const filePath = path.join(runDir, filename);
  fs.writeFileSync(filePath, Buffer.from(buffer));
  return filePath;
});

ipcMain.handle("transcribe-file", async (_event, payload) => {
  const { inputPath, modelPath, groqKey } = payload;

  if (!inputPath) {
    throw new Error("Nenhum arquivo de audio informado.");
  }
  if (!modelPath) {
    throw new Error("Informe o caminho do modelo Vosk.");
  }

  const absModel = path.isAbsolute(modelPath)
    ? modelPath
    : path.join(APP_ROOT, modelPath);

  if (!fs.existsSync(absModel)) {
    throw new Error(`Modelo nao encontrado: ${absModel}`);
  }

  if (!groqKey) {
    throw new Error("Informe sua GROQ_API_KEY para corrigir e resumir.");
  }

  const runDir = path.join(app.getPath("userData"), "runs", Date.now().toString());
  ensureDir(runDir);

  const transcriptPath = path.join(runDir, "transcricao.txt");
  const correctedPath = path.join(runDir, "transcricao_corrigida.txt");
  const summaryPath = path.join(runDir, "resumo.txt");

  const transcribeScript = path.join(APP_ROOT, "src", "transcribe_file.py");
  const agentScript = path.join(APP_ROOT, "src", "agent.py");

  sendLog("Iniciando transcricao...");
  await runPython(transcribeScript, [
    "--model",
    absModel,
    "--input",
    inputPath,
    "--out",
    transcriptPath,
  ]);

  sendLog("Iniciando correcao e resumo...");
  await runPython(
    agentScript,
    [
      "--input",
      transcriptPath,
      "--corrected",
      correctedPath,
      "--summary",
      summaryPath,
    ],
    { GROQ_API_KEY: groqKey }
  );

  const transcript = fs.readFileSync(transcriptPath, "utf-8");
  const corrected = fs.readFileSync(correctedPath, "utf-8");
  const summary = fs.readFileSync(summaryPath, "utf-8");

  return { transcript, corrected, summary };
});

ipcMain.handle("save-results", async (_event, payload) => {
  const { transcript, corrected, summary } = payload;
  const result = await dialog.showOpenDialog({
    title: "Escolher pasta para salvar",
    properties: ["openDirectory"],
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  const dir = result.filePaths[0];
  const transcriptPath = path.join(dir, "transcricao.txt");
  const correctedPath = path.join(dir, "transcricao_corrigida.txt");
  const summaryPath = path.join(dir, "resumo.txt");

  fs.writeFileSync(transcriptPath, transcript || "", "utf-8");
  fs.writeFileSync(correctedPath, corrected || "", "utf-8");
  fs.writeFileSync(summaryPath, summary || "", "utf-8");

  return { transcriptPath, correctedPath, summaryPath };
});
