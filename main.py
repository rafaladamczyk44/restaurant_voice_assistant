import os
import openai

from speech_to_text import STT

API_KEY = os.environ.get('OPENAI_KEY')
LANG = 'en'

stt = STT(API_KEY, LANG)
result = stt.make_transcript('speech.wav')
print(result)