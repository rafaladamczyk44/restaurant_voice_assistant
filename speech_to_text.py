import time
import torch
import sounddevice as sd
import numpy as np
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

class STT:
    def __init__(self,  model_id="openai/whisper-large-v3-turbo"):
        """
        https://huggingface.co/openai/whisper-large-v3-turbo
        :param model_id: Whisper model, default: openai/whisper-large-v3-turbo
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_id = model_id
        self.pipe = self._create_pipeline()
        self.whisper_kwargs = {"language": "english"}

    def _create_pipeline(self):

        processor = AutoProcessor.from_pretrained(self.model_id)

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )

        return pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch.float32,
            device=self.device,
        )

    def record_audio(self, max_record_duration=10):
        """
        Method for dynamic audio recording - waits for a signal to break silence threshold and then records for the max of 5 sec silence
        https://python-sounddevice.readthedocs.io/en/0.5.1/api/streams.html#sounddevice.InputStream
        :param max_record_duration: Max record duration in seconds, default 10
        :return: Models' transcript of the recorded audio
        """
        block_size = 4000 # Number of frames => 0.25s audio
        sample_rate = 16000
        silence_duration = 5.0
        audio_buffer = []
        chunks_per_second = sample_rate // block_size
        silent_threshold_chunks = int(silence_duration * chunks_per_second)
        max_chunks = int(max_record_duration * chunks_per_second)

        # For callback
        is_recording = False
        should_stop = False
        silent_chunks = 0
        chunk_count = 0
        silence_threshold = 0.03
        print('Waiting for speech...')

        def audio_callback(indata, frames, time, status):
            """
            Callback function for processing audio data
            https://python-sounddevice.readthedocs.io/en/0.5.1/_modules/sounddevice.html#OutputStream
            """
            nonlocal is_recording, silent_chunks, chunk_count, should_stop

            volume_level = np.linalg.norm(indata) / np.sqrt(len(indata))

            if volume_level > silence_threshold:
                if not is_recording:
                    print('Speech detected, recording...')
                    is_recording = True

                silent_chunks = 0

                if is_recording:
                    audio_buffer.append(indata.copy())
                    chunk_count += 1
            else:
                if is_recording:
                    silent_chunks += 1
                    audio_buffer.append(indata.copy())
                    chunk_count += 1

                    if silent_chunks >= silent_threshold_chunks or chunk_count >= max_chunks:
                        print('Stopping recording due to silence or max duration')
                        should_stop = True  # Set flag to break the rec
                        return

        stream = sd.InputStream(
            channels=1,
            dtype='float32',
            samplerate=sample_rate,
            blocksize=block_size,
            callback=audio_callback,
        )

        with stream:
            try:
                while not should_stop:
                    # Waiting for callback
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print('Recording interrupted')

        print('Finished recording')

        if not audio_buffer:
            print('No audio detected')
            return ''

        audio_data = np.concatenate(audio_buffer).flatten()

        # Normalize audio
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))

        print('Processing the audio...')
        result = self.pipe(audio_data, self.whisper_kwargs)

        transcription = result["text"].strip()
        return transcription