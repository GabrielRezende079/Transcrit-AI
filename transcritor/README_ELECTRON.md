# App Desktop (Electron)

Interface desktop para:
1) Gravar pelo microfone ou selecionar um audio
2) Transcrever com Vosk
3) Corrigir e resumir com Groq + LangChain

## Requisitos
- Node.js 18+
- Python 3.9+
- ffmpeg no PATH
- Modelo Vosk em `models/`
- Dependencias Python instaladas

## Instalar dependencias do app

```powershell
npm install
```

## Rodar

```powershell
npm start
```

## Observacoes
- Informe sua `GROQ_API_KEY` dentro do app.
- Se o modelo Vosk nao estiver na pasta padrao, edite o caminho no campo "Modelo Vosk".
- O app chama os scripts Python `src/transcribe_file.py` e `src/agent.py`.
