
import os
import pyttsx3
from elevenlabs import stream
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from RealtimeSTT import AudioToTextRecorder

from dotenv import load_dotenv
load_dotenv()

def load_voice_id(keyword):
    if keyword == "robot_cold":
        return os.environ.get("COLDVOICE_ID")
    elif keyword == "robot_warm":
        return os.environ.get("WARMVOICE_ID")
    elif keyword == "malak":
        return os.environ.get("MALAKVOICE_ID")

class AIAudio:
    """ Audio client for Text-to-Speech conversion """
    def __init__(self, use_elevenlabs=True, speech_model_id="whisper-large-v3", voice_id="JBFqnCBsd6RMkjVDRZzb"):
        self.use_elevenlabs = use_elevenlabs
        self.voice_id = load_voice_id(voice_id)
        self.speech_model_id = speech_model_id

        # Text-To-Speech (TTS) client
        if self.use_elevenlabs:
            self.tts_client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))
        else:
            self.tts_client = pyttsx3.init()
            self.tts_client.setProperty('rate', self.tts_client.getProperty('rate') + 30)

        # Speech-To-Text (STT) client
        self.stt_client = AudioToTextRecorder(
            model="tiny.en",
            #compute_type="float16",
            ensure_sentence_ends_with_period=False,
            #batch_size=32,
            #realtime_model_type="tiny.en", # Enable this one
            #enable_realtime_transcription=True,
            #realtime_processing_pause=0.05,
            #early_transcription_on_silence=100,
            #post_speech_silence_duration=0.3,
            #min_length_of_recording=0.3,
            #no_log_file=True,                          # Enable this one
            #level=logging.CRITICAL  # Disable logging
        )
        self.speech_model_id = speech_model_id

    def say(self, text):
        """ Converts text to speech and plays the audio stream """
        audio_stream = self.tts_client.text_to_speech.convert_as_stream(
            text=text,
            voice_id=self.voice_id,
            model_id=self.speech_model_id,
            voice_settings=VoiceSettings(
                stability=0.4,
                similarity_boost=0.9,
                speed=0.9,
            )
        )
        stream(audio_stream)
        return True

    def listen_and_transcribe(self):
        """ Listens for audio input and converts to text (blocking)"""
        # Create a thread which listens for audio input and returns the transcribed text
        #threading.Thread(target=self.stt_client.text, daemon=True).start()

        return self.stt_client.text()
