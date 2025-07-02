import os
import uuid
import logging
import cloudinary
import cloudinary.uploader
import cloudinary.api
import tempfile
from google.cloud import texttospeech
from elevenlabs.client import ElevenLabs
from app.voice.dto import VoiceSchema, GCTTSRequest, VoiceCloneRequest, ElevenlabsTTSRequest

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

logger = logging.getLogger(__name__)
class VoiceService:
    _instance = None
    _gctts_client = None
    _elevenlabs_client = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize_elevenlabs_client()
        return cls._instance
    
    # Google Cloud TTS
    def _initialize_gctts_client(self):
        if not self._gctts_client:
            try:
                self._gctts_client = texttospeech.TextToSpeechClient()
                logger.info("Initialized Google Cloud TTS client successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Google Cloud TTS client: {e}")
                raise e
    
    def get_gctts_voice_lists(self, language_code='en-US') -> list[VoiceSchema]:
        if not self._gctts_client:
            self._initialize_gctts_client()
        GCTTS_SAMPLE_VOICE_BASE_URL = "https://cloud.google.com/static/text-to-speech/docs/audio/"
        try:
            google_voices = self._gctts_client.list_voices(language_code=language_code)
            serialized_voices = []
            for g_voice in google_voices.voices:
                voice_data = {
                    'name': g_voice.name,
                    'language_code': g_voice.language_codes[0],
                    'gender': texttospeech.SsmlVoiceGender(g_voice.ssml_gender).name,
                    'natural_sample_rate_hertz': g_voice.natural_sample_rate_hertz,
                    'preview_url': f"{GCTTS_SAMPLE_VOICE_BASE_URL}{g_voice.name}.wav"
                }
                serialized_voices.append(VoiceSchema.model_validate(voice_data))
            return serialized_voices
        except Exception as e:
            logger.error(f"Error retrieving voice lists: {e}")
            raise e
    
    def gctts_generate_tts(self, dto: GCTTSRequest) -> dict:
        if not self._gctts_client:
            self._initialize_gctts_client()
        
        try:
            synthesis_input = texttospeech.SynthesisInput(text=dto.script)
            voice = texttospeech.VoiceSelectionParams(
                language_code=dto.language_code,
                name=dto.voice_name
            )
            
            audio_config_params = {
                "volume_gain_db": dto.volume_gain_db,
                "audio_encoding": texttospeech.AudioEncoding.MP3
            }

            voice_name = dto.voice_name

            if "Chirp-HD" in voice_name or "Chirp3-HD" in voice_name:
                logger.warning(
                    f"Voice '{voice_name}' is a Chirp-HD type. "
                    f"Skipping 'speaking_rate' parameter (value: {dto.speaking_rate})."
                )
            else:
                audio_config_params["speaking_rate"] = dto.speaking_rate

            if "Chirp-HD" in voice_name or "Studio" in voice_name or "Chirp3-HD" in voice_name:
                logger.warning(
                    f"Voice '{voice_name}' is a Chirp-HD or Studio type. "
                    f"Skipping 'pitch' parameter (value: {dto.pitch})."
                )
            else:
                audio_config_params["pitch"] = dto.pitch

            audio_config = texttospeech.AudioConfig(**audio_config_params)
            
            response = self._gctts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            filename = f"{uuid.uuid4()}.mp3"
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, filename)
            with open(output_path, "wb") as f:
                f.write(response.audio_content)
            
        except Exception as e:
            logger.error(f"Error generating TTS: {e}")
            raise e
        
        cloudinary_response = cloudinary.uploader.upload(
            output_path,
            folder='gctts',
            resource_type='video',
            public_id=f"gctts_{uuid.uuid4()}"
        )
        
        # remove the local file after upload
        os.remove(output_path)
        
        return {
            "message": "TTS generated successfully.",
            "audio_url": cloudinary_response['secure_url'],
            "filename": filename,
            "voice_used": dto.voice_name
        }
    
    # ElevenLabs TTS and Voice Cloning
    def _initialize_elevenlabs_client(self):
        if not self._elevenlabs_client:
            api_key = os.getenv('ELEVENLABS_API_KEY')
            if not api_key:
                raise ValueError("ELEVENLABS_API_KEY is not set in the application config.")
            self._elevenlabs_client = ElevenLabs(api_key=api_key)
            logger.info("Initialized ElevenLabs client successfully.")
    
    def clone_voice(self, dto: VoiceCloneRequest, audio_file) -> object:
        if not self._elevenlabs_client:
            self._initialize_elevenlabs_client()

        try:            
            clone_voice = self._elevenlabs_client.voices.ivc.create(
                name=dto.voice_name,
                files=[audio_file]
            )
        except Exception as e:
            logger.error(f"Error creating voice clone: {e}")
            raise e
        
        voice = self._elevenlabs_client.voices.get(clone_voice.voice_id)
        
        try:
            preview_url = self.elevenlabs_generate_tts(
                ElevenlabsTTSRequest(
                    script=dto.preview_script,
                    voice_id=clone_voice.voice_id,
                )
            )['audio_url']
            return {
                "voice_id": getattr(voice, "voice_id", ""),
                "preview_url": preview_url
            }
        except Exception as e:
            logger.error(f"Error generating preview for cloned voice: {e}")
            raise e
    
    def elevenlabs_generate_tts(self, dto: ElevenlabsTTSRequest) -> dict:
        if not self._elevenlabs_client:
            self._initialize_elevenlabs_client()

        try:            
            settings_dict = {
                "stability": dto.stability,
                "speed": dto.speed
            }
            
            audio = self._elevenlabs_client.text_to_speech.convert(
                text=dto.script,
                voice_id=dto.voice_id,
                voice_settings=settings_dict,
                model_id="eleven_flash_v2_5",
                output_format="mp3_44100_128",
            )
            
            audio_data = b"".join([chunk for chunk in audio])
            filename = f"{uuid.uuid4()}.mp3"
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, filename)
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            cloudinary_response = cloudinary.uploader.upload(
                output_path,
                folder='elevenlabs',
                resource_type='video',
                public_id=f"elevenlabs_{uuid.uuid4()}"
            )
            
            # remove the local file after upload
            os.remove(output_path)
                        
            return {
                "audio_url": cloudinary_response['secure_url'],
                "filename": filename,
                "voice_used": dto.voice_id
            }
        except Exception as e:
            logger.error(f"Error generating TTS with ElevenLabs: {e}")
            raise e
    
    def delete_cloned_voice(self, voice_id) -> dict:
        if not self._elevenlabs_client:
            self._initialize_elevenlabs_client()

        try:
            self._elevenlabs_client.voices.delete(voice_id)
        except Exception as e:
            logger.error(f"Error deleting cloned voice: {e}")
            raise e