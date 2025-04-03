from pathlib import Path
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

speech_file_path = Path(__file__).parent / "speech.wav"
response = client.audio.speech.create(
    model="tts-1",
    voice="ash",
    input="Today is a wonderful day to build something people love!",
)
response.stream_to_file(speech_file_path)