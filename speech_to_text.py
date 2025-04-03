import torch
import sounddevice as sd
import numpy as np
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

class STT:
    def __init__(self,  model_id="openai/whisper-large-v3-turbo"):
        """
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_id = model_id
        self.pipe = self._create_pipeline()

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

    def record_audio(self, duration:int=5, sample_rate:int=16000, block_size=4000):

        # TODO: Dynamic audio capturing

        print('Start Recording...')
        # is_recording = False
        #
        # # https://python-sounddevice.readthedocs.io/en/0.5.1/api/streams.html#sounddevice.Stream
        # with sd.InputStream(
        #     channels=1,
        #     dtype='float32',
        #     samplerate=sample_rate,
        #     blocksize=block_size, # he number of frames passed to the stream callback function, or the preferred block granularity for a blocking read/write stream
        # ):
        #     pass


        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16
        )

        sd.wait()
        print('Finished Recording')
        # Convert to the right format
        audio_data = audio_data.flatten().astype(np.float32)

        # Normalize audio
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))

        print("Processing...")
        # Process with Whisper

        result = self.pipe(audio_data)

        # Display result
        transcription = result["text"].strip()

        # print(transcription)
        return transcription
