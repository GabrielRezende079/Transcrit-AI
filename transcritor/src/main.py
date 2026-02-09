import argparse
import json

import pyaudio
from vosk import Model, KaldiRecognizer

# Seleciona o índice do dispositivo de entrada com base em uma dica de nome
def _pick_input_device_index(p: pyaudio.PyAudio, name_hint: str | None) -> int | None:
    if not name_hint:
        return None
    name_hint = name_hint.lower()
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if name_hint in info.get("name", "").lower():
            return i
    return None

# Função principal para configuração e execução da transcrição em tempo real 
def main() -> int:
    parser = argparse.ArgumentParser(description="Transcrição em tempo real com Vosk")
    parser.add_argument("--model", required=True, help="Caminho para o modelo Vosk")
    parser.add_argument("--samplerate", type=int, default=16000, help="Taxa de amostragem") # Padrão é 16000 Hz
    parser.add_argument("--device", help="Parte do nome do dispositivo de entrada") # Dispositivo de áudio
    parser.add_argument(
        "--out",
        default="transcricao.txt",
        help="Arquivo .txt para salvar a transcrição",
    )
    args = parser.parse_args()
# Configuração do modelo e reconhecedor Vosk
    model = Model(args.model)
    recognizer = KaldiRecognizer(model, args.samplerate)
    recognizer.SetWords(True)
# Configuração do PyAudio e fluxo de áudio 
    p = pyaudio.PyAudio()
    device_index = _pick_input_device_index(p, args.device)
# Abrindo o fluxo de áudio para captura de voz
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=args.samplerate,
        input=True,
        frames_per_buffer=8000,
        input_device_index=device_index,
    )
    stream.start_stream()
# Loop principal de transcrição e salvamento em arquivo 
    print("Escutando... (Ctrl+C para sair)")
    print(f"Salvando em: {args.out}")
# Abrindo o arquivo de saída em modo de anexação 
    out_file = open(args.out, "a", encoding="utf-8")
    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    print(text)
                    out_file.write(text + "\n")
                    out_file.flush()
            else:
                partial = json.loads(recognizer.PartialResult()).get("partial", "").strip()
                if partial:
                    print(f"... {partial}")
    except KeyboardInterrupt:
        print("\nEncerrado.")
    finally:
        out_file.close()
        stream.stop_stream()
        stream.close()
        p.terminate()

    return 0

# Ponto de entrada do script 
if __name__ == "__main__":
    raise SystemExit(main())
