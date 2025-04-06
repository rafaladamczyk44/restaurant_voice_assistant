import os
import pyaudio
from openai import OpenAI

class TTS:
    def __init__(self, model="tts-1"):
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.model = model

    def generate_audio(self, text, voice='ash'):
        p = pyaudio.PyAudio()

        stream = p.open(format=8, channels=1, rate=24_000, output=True)

        with self.client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=voice,
                input=text,
                response_format="pcm"
        ) as response:
            for chunk in response.iter_bytes(1024):
                stream.write(chunk)



