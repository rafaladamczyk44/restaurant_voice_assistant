import openai
import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

# TODO: Decide on which Whisper to use: currently open source, possibly through OpenAI Client API
# TODO: Decide which API to use - maybe Google Cloud STT?
class STT:
    def __init__(self, api_key, language:str, model:str='base'):
        """
        Speech to text class working in 3 steps:
            1. Record audio
            2. Save it as .wav file
            3. Make a transcription out of recorded file with Whisper
        :param api_key: OpenAI API key
        :param language: Provide Whisper model with language code of the audio file
        :param model: Whisper model size
        """
        openai.api_key = api_key
        self.model = whisper.load_model(model)
        self.language = language

    def record_audio(self, path:str, duration:int=5, sample_rate:int=44100, ):
        print('Start Recording...')
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()
        print('Finished Recording')
        wav.write(path, sample_rate, audio_data)

    def make_transcript(self, path_to_audio_file:str) -> str:
        transcript = self.model.transcribe(path_to_audio_file, language=self.language)
        return transcript['text'].strip()