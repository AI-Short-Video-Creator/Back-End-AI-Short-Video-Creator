import os
import uuid
import logging
import base64
from io import BytesIO
from flask import current_app
from elevenlabs.client import ElevenLabs

logger = logging.getLogger(__name__)

class VoiceService:
    _instance = None
    _elevenlabs_client = None
    _voice_samples_data = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize_elevenlabs_client()
        return cls._instance

    def _initialize_elevenlabs_client(self):
        if not self._elevenlabs_client:
            api_key = os.getenv('ELEVENLABS_API_KEY')
            if not api_key:
                raise ValueError("ELEVENLABS_API_KEY is not set in the application config.")
            self._elevenlabs_client = ElevenLabs(api_key=api_key)
            logger.info("Initialized ElevenLabs client successfully.")
    
    def _load_voice_samples_data(self):
        if not self._elevenlabs_client:
            self._initialize_elevenlabs_client()
            
        if not self._voice_samples_data:
            self._voice_samples_data = self._elevenlabs_client.voices.search(
                page_size=20,
            )
            
        if not self._voice_samples_data:
            raise ValueError("No voice samples data found. Please check your ElevenLabs API configuration.")
    
    def get_voice_samples(self):
        if not self._voice_samples_data:
            self._load_voice_samples_data()
        
        return self._voice_samples_data.voices
    
    def generate_tts(self, tts_request):
        if not self._elevenlabs_client:
            self._initialize_elevenlabs_client()
        
        try:
            audio = self._elevenlabs_client.text_to_speech.convert(
                text=tts_request.text,
                voice_id=tts_request.voice_id,
                model_id="eleven_flash_v2_5",
                output_format="mp3_44100_128",
            )
            
            audio_data = b"".join([chunk for chunk in audio])
            filename = f"{uuid.uuid4()}.mp3"
            output_path = os.path.join(current_app.config['AUDIO_UPLOAD_FOLDER'], filename)
            
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            return {
                "message": "TTS generated successfully.",
                "audio_path": output_path,
                "filename": filename,
                "voice_used": tts_request.voice_id
            }
        except Exception as e:
            logger.error(f"Error generating TTS: {e}")
            raise e
    
    def generate_tts_voice_clone(self, tts_voice_clone_request):
        if not self._elevenlabs_client:
            self._initialize_elevenlabs_client()
        
        try:
            audio_data = base64.b64decode(tts_voice_clone_request.audio_base64)
            audio_file = BytesIO(audio_data)
            
            voice = self._elevenlabs_client.voices.ivc.create(
                name='Clone Voice',
                files=[audio_file]
            )
        except Exception as e:
            logger.error(f"Error creating voice clone: {e}")
            raise e

        try:
            audio = self._elevenlabs_client.text_to_speech.convert(
                text=tts_voice_clone_request.text,
                voice_id=voice.voice_id,
                model_id="eleven_flash_v2_5",
                output_format="mp3_44100_128",
            )
            
            audio_data = b"".join([chunk for chunk in audio])
            filename = f"{uuid.uuid4()}.mp3"
            output_path = os.path.join(current_app.config['AUDIO_UPLOAD_FOLDER'], filename)
            
            with open(output_path, "wb") as f:
                f.write(audio_data)
                        
            return {
                "message": "TTS voice clone generated successfully.",
                "audio_path": output_path,
                "filename": filename,
            }
        except Exception as e:
            logger.error(f"Error generating TTS voice clone: {e}")
            raise e
        finally:
            if voice is not None:
                try:
                    self._elevenlabs_client.voices.delete(voice.voice_id)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to delete cloned voice: {cleanup_err}")