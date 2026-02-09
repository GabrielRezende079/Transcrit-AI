# Instalador (Electron Builder)

Este projeto usa o **electron-builder** para gerar instalador do app.

## Pré-requisitos
- Node.js 18+
- Python 3.9+ instalado na máquina (para preparar o bundle)
- ffmpeg instalado ou o zip do ffmpeg para embutir

## Gerar instalador COM tudo embutido (Python + FFmpeg)

1) Baixe o Python embeddable (Windows x64) e o FFmpeg (.zip)
2) Coloque os zips em `bundle/_tmp/`
3) Rode:

```powershell
npm run bundle:setup
```

4) Gere o instalador:

```powershell
npm run dist
```

O instalador será criado em `dist/`.

## Observações
- O bundle será criado em `bundle/`.
- O app vai usar automaticamente `bundle/python/python.exe` e `bundle/ffmpeg/bin`.
- Para atualizar dependências, rode novamente `npm run bundle:setup`.
