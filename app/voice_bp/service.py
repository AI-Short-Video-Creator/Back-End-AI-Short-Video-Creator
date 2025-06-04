from google.cloud import texttospeech
import os
import uuid
import logging
import json
from flask import current_app

logger = logging.getLogger(__name__)

class VoiceService:
    _instance = None
    _tts_client = None
    _voice_samples_data = None
    _metadata_file_path = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize_tts_client()
        return cls._instance

    def _initialize_tts_client(self):
        if not VoiceService._tts_client:
            if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                logger.error("CRITICAL: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
                logger.error("         Google Cloud TTS Client will NOT be initialized.")
                VoiceService._tts_client = None
                return
            try:
                VoiceService._tts_client = texttospeech.TextToSpeechClient()
                logger.info("Google Cloud TTS Client initialized successfully by VoiceService.")
            except Exception as e:
                logger.error(f"Failed to initialize Google Cloud TTS Client in VoiceService: {e}")
                logger.error("Ensure 'GOOGLE_APPLICATION_CREDENTIALS' points to a valid service account key file.")
                VoiceService._tts_client = None
                
    def _ensure_metadata_loaded(self):
        if VoiceService._voice_samples_data is not None:
            return

        if VoiceService._metadata_file_path is None:
            if not current_app:
                logger.error("VoiceService (Metadata): Cannot determine metadata path (current_app not available).")
                VoiceService._voice_samples_data = []
                return

            app_folder_path = current_app.root_path 
            
            metadata_filename = "voice_samples_metadata.json"
            VoiceService._metadata_file_path = os.path.join(app_folder_path, metadata_filename)
            logger.info(f"VoiceService (Metadata): Path set to '{VoiceService._metadata_file_path}'")

        if not os.path.exists(VoiceService._metadata_file_path):
            logger.warning(f"VoiceService (Metadata): File not found at '{VoiceService._metadata_file_path}'.")
            VoiceService._voice_samples_data = []
            return
        try:
            with open(VoiceService._metadata_file_path, 'r', encoding='utf-8') as f:
                VoiceService._voice_samples_data = json.load(f)
            logger.info(f"VoiceService (Metadata): Loaded {len(VoiceService._voice_samples_data)} samples.")
        except Exception as e:
            logger.error(f"VoiceService (Metadata): Error loading metadata: {e}", exc_info=True)
            VoiceService._voice_samples_data = []

    def get_all_voice_samples(self):
        self._ensure_metadata_loaded()
        return VoiceService._voice_samples_data or []

    def get_sample_by_voice_name(self, voice_name_to_find: str):
        all_samples = self.get_all_voice_samples()
        for sample in all_samples:
            if sample.get("voiceName") == voice_name_to_find:
                return sample
        logger.debug(f"VoiceService (Metadata): Sample for '{voice_name_to_find}' not found.")
        return None

    def get_samples_by_criteria(self, language_code: str = None, gender: str = None, voice_type: str = None):
        all_samples = self.get_all_voice_samples()
        if not all_samples: return []
        
        filtered_samples = list(all_samples)
        logger.debug(f"VoiceService (Metadata): Filtering - lang: {language_code}, gender: {gender}, type: {voice_type}")
        
        if language_code:
            filtered_samples = [s for s in filtered_samples if s.get("languageCode") and s.get("languageCode").lower() == language_code.lower()]
        if gender:
            gender_upper = gender.upper()
            filtered_samples = [s for s in filtered_samples if s.get("ssmlGender") and s.get("ssmlGender").upper() == gender_upper]
        if voice_type:
            filtered_samples = [s for s in filtered_samples if s.get("voiceTypeApproximation") and s.get("voiceTypeApproximation").lower() == voice_type.lower()]
            
        logger.info(f"VoiceService (Metadata): Found {len(filtered_samples)} samples matching criteria.")
        return filtered_samples

    def is_metadata_loaded_successfully(self):
        self._ensure_metadata_loaded()
        return VoiceService._voice_samples_data is not None and len(VoiceService._voice_samples_data) > 0

    def reload_metadata(self):
        logger.info("VoiceService (Metadata): Reloading voice samples metadata...")
        VoiceService._voice_samples_data = None
        VoiceService._metadata_file_path = None
        self._ensure_metadata_loaded()
        if VoiceService._voice_samples_data is None: return False
        return True
    
    def generate_google_tts_audio(self, text_data: dict):
        if not VoiceService._tts_client:
            raise ConnectionError("Google Cloud TTS client is not initialized. Check server logs for details.")

        synthesis_input = texttospeech.SynthesisInput(text=text_data['text'])

        voice_params = texttospeech.VoiceSelectionParams(
            language_code=text_data['language_code'],
            name=text_data['voice_name']
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        try:
            response = VoiceService._tts_client.synthesize_speech(
                request={"input": synthesis_input, "voice": voice_params, "audio_config": audio_config}
            )

            default_audio_path = os.path.join(current_app.root_path, current_app.static_folder, 'generated_audio')
            audio_folder = current_app.config.get('AUDIO_UPLOAD_FOLDER', default_audio_path)
            os.makedirs(audio_folder, exist_ok=True)

            filename = f"gtts_{uuid.uuid4()}.mp3"
            output_filepath = os.path.join(audio_folder, filename)

            with open(output_filepath, "wb") as out_file:
                out_file.write(response.audio_content)
            logger.info(f"Audio content written to file: {output_filepath}")

            return {
                "message": "Tạo giọng đọc bằng Google Cloud TTS thành công!",
                "audio_path": output_filepath,
                "filename": filename,
                "voice_used": text_data['voice_name'],
                "language_code": text_data['language_code']
            }
        except Exception as e:
            logger.error(f"Error calling Google Cloud TTS API: {e}", exc_info=True)
            raise e