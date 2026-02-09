# Transcritor em tempo real (Vosk)

Transcrição de áudio do microfone para texto em PT-BR, rodando localmente com Vosk.

## Requisitos
- Python 3.9+

## Instalação
1) Crie e ative um venv (opcional, recomendado)
2) Instale as dependências:

```powershell
pip install -r requirements.txt
```

## Baixar modelo automaticamente

```powershell
python scripts/download_vosk_model.py --model pt-br-small
```

Isso baixa o modelo para `models/vosk-model-small-pt-0.3`.

Se quiser usar outro modelo, passe `--url` com o link do modelo Vosk e o script vai baixar e extrair:

```powershell
python scripts/download_vosk_model.py --url "<LINK_DO_MODELO>"
```

## Rodar

```powershell
python src/main.py --model models/vosk-model-small-pt-0.3
```

## Transcrever arquivo .mp3

Requer `ffmpeg` instalado e no PATH.

```powershell
python src/transcribe_file.py --model models/vosk-model-small-pt-0.3 --input "meu_audio.mp3"
```

Isso gera `meu_audio.txt` no diretório atual. Para escolher outro nome:

```powershell
python src/transcribe_file.py --model models/vosk-model-small-pt-0.3 --input "meu_audio.mp3" --out "saida.txt"
```

## Notas
- Pressione Ctrl+C para parar.
- Se quiser transcrever outro idioma, baixe o modelo correspondente e passe o caminho pelo `--model`.


## Gerar Instalador
-npx electron-builder
