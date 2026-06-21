import os
import torch
import soundfile as sf
from pathlib import Path

MODEL, _ = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='ru',
    speaker='v4_ru'
)

SAMPLE_RATE = 48000


def text_to_speech(text: str) -> str: # Генерирует wav-файл и возвращает путь к нему.
    audio = MODEL.apply_tts(text=text, speaker='xenia', sample_rate=SAMPLE_RATE)
    output_path = Path("temp_answer.wav")

    sf.write(output_path, audio.numpy(), SAMPLE_RATE)
    return str(output_path)

async def send_voice_answer(update, answer: str):

    voice_path = text_to_speech(answer)

    try:
        with open(voice_path, "rb") as voice:
            await update.message.reply_voice(voice)

    finally:
        if os.path.exists(voice_path):
            os.remove(voice_path)