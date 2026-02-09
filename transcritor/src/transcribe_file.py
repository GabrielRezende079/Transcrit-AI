import argparse
import json
import shutil
import subprocess
from pathlib import Path

from vosk import Model, KaldiRecognizer


def _ensure_ffmpeg() -> bool:
    if shutil.which("ffmpeg"):
        return True
    print("ffmpeg nao encontrado no PATH.")
    print("Instale o ffmpeg e tente novamente.")
    return False


def _iter_pcm_chunks(path: Path, samplerate: int, chunk_size: int = 4000):
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-ac",
        "1",
        "-ar",
        str(samplerate),
        "-f",
        "s16le",
        "-",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    assert proc.stdout is not None
    try:
        while True:
            data = proc.stdout.read(chunk_size)
            if not data:
                break
            yield data
    finally:
        proc.stdout.close()
        proc.wait()


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcricao de arquivo de audio com Vosk")
    parser.add_argument("--model", required=True, help="Caminho para o modelo Vosk")
    parser.add_argument("--input", required=True, help="Arquivo de audio (.mp3, .wav, etc.)")
    parser.add_argument("--out", help="Arquivo .txt de saida")
    parser.add_argument("--samplerate", type=int, default=16000, help="Taxa de amostragem")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Arquivo nao encontrado: {input_path}")
        return 2

    if not _ensure_ffmpeg():
        return 2

    out_path = Path(args.out) if args.out else Path(f"{input_path.stem}.txt")

    model = Model(args.model)
    recognizer = KaldiRecognizer(model, args.samplerate)
    recognizer.SetWords(True)

    with out_path.open("w", encoding="utf-8") as out_file:
        for chunk in _iter_pcm_chunks(input_path, args.samplerate):
            if recognizer.AcceptWaveform(chunk):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    out_file.write(text + "\n")

        final = json.loads(recognizer.FinalResult())
        final_text = final.get("text", "").strip()
        if final_text:
            out_file.write(final_text + "\n")

    print(f"Transcricao salva em: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
