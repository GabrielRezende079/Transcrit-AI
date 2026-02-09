import argparse
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

MODELS = {
    "pt-br-small": {
        "name": "vosk-model-small-pt-0.3",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip",
    }
}


def _download(url: str, dest: str) -> None:
    with urllib.request.urlopen(url) as response, open(dest, "wb") as f:
        total = response.headers.get("Content-Length")
        total_bytes = int(total) if total else None
        downloaded = 0
        chunk_size = 1024 * 256
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if total_bytes:
                percent = (downloaded / total_bytes) * 100
                print(f"Baixando... {percent:.1f}%", end="\r")
    print("Baixando... 100%")


def _extract(archive_path: str, dest_dir: str) -> str | None:
    root_dirs: set[str] = set()

    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path) as z:
            for name in z.namelist():
                parts = name.split("/")
                if parts and parts[0]:
                    root_dirs.add(parts[0])
            z.extractall(dest_dir)
    elif tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path, "r:*") as t:
            for member in t.getmembers():
                parts = member.name.split("/")
                if parts and parts[0]:
                    root_dirs.add(parts[0])
            t.extractall(dest_dir)
    else:
        raise ValueError("Arquivo não é zip nem tar.gz")

    if len(root_dirs) == 1:
        return next(iter(root_dirs))
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Baixa modelo Vosk para a pasta models/")
    parser.add_argument("--model", default="pt-br-small", help="Modelo pré-configurado")
    parser.add_argument("--url", help="URL direta do modelo (.zip ou .tar.gz)")
    parser.add_argument("--dir", default="models", help="Pasta de destino")
    args = parser.parse_args()

    models_dir = os.path.abspath(args.dir)
    os.makedirs(models_dir, exist_ok=True)

    if args.url:
        url = args.url
        expected_name = None
    else:
        if args.model not in MODELS:
            print("Modelo desconhecido. Use --url para informar o link.")
            return 2
        url = MODELS[args.model]["url"]
        expected_name = MODELS[args.model]["name"]

    filename = os.path.basename(url)
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = os.path.join(tmpdir, filename)
        print(f"Baixando {url}")
        _download(url, archive_path)
        root = _extract(archive_path, models_dir)

    if expected_name:
        target = os.path.join(models_dir, expected_name)
        if root:
            extracted = os.path.join(models_dir, root)
            if extracted != target and os.path.exists(extracted) and not os.path.exists(target):
                shutil.move(extracted, target)
        if os.path.isdir(target):
            print(f"Modelo pronto em: {target}")
        else:
            print("Extração concluída, mas o diretório esperado não foi encontrado.")
    else:
        print(f"Download concluído em: {models_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
