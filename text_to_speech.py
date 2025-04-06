import os
import pyaudio
from openai import OpenAI

API_KEY = os.environ.get('OPENAI_KEY')

class TTS:
    def __init__(self, model="tts-1"):
        self.client = OpenAI(api_key=API_KEY)
        self.model = model

    def generate_audio(self, text, voice='ash'):
        """
        https://community.openai.com/t/streaming-from-text-to-speech-api/493784
        :param text: Query to be read by the model
        :param voice: Voice chosen to read the query, default 'ash'
        :return: Generated audio stream
        """
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
