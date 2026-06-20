from pathlib import Path
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

import wave
import json
import tempfile
import os

model = Model(str(Path(__file__).resolve().parent.parent / "models" / "vosk-model-small-ru-0.22"))

def convert_ogg_to_wav(ogg_path: str, wav_path: str):
    audio = AudioSegment.from_ogg(ogg_path)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    audio = audio.set_sample_width(2)

    audio.export(wav_path, format="wav")

def recognize_voice(ogg_path: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
        wav_path = wav_file.name

    try:
        convert_ogg_to_wav(ogg_path, wav_path)
        with wave.open(wav_path, "rb") as wf:
            recognizer = KaldiRecognizer(model, wf.getframerate())

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break

                recognizer.AcceptWaveform(data)

            final_result = recognizer.FinalResult()
            # print(f"stt result: {final_result}")
            result = json.loads(final_result)

            # print("channels:", wf.getnchannels())
            # print("framerate:", wf.getframerate())
            # print("sampwidth:", wf.getsampwidth())
            return result.get("text", "")

    finally:
        print(wav_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)