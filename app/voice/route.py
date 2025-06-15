from flask import Blueprint, request, jsonify
import logging
from pydantic import ValidationError
from app.voice.service import VoiceService
from app.voice.dto import TTSRequest, TTSVoiceCloneRequest, TTSResponse, VoiceListResponse

logger = logging.getLogger(__name__)

class VoiceController:
    def __init__(self):
        self.service = VoiceService()
        self.voice_bp = Blueprint('voice_bp', __name__)
        self._register_routes()

    def _register_routes(self):
        self.voice_bp.add_url_rule('/samples', view_func=self.get_voice_samples, methods=['GET'])
        self.voice_bp.add_url_rule('/tts', view_func=self.generate_tts, methods=['POST'])
        self.voice_bp.add_url_rule('/tts-clone-voice', view_func=self.generate_tts_clone_voice, methods=['POST'])
        
    def get_voice_samples(self):
        try:
            voices = self.service.get_voice_samples()
            response = VoiceListResponse(
                total_count=len(voices),
                message="Successfully retrieved voice samples.",
                voices=[voice.dict() for voice in voices]
            )
            return jsonify(response.dict()), 200
        except Exception as e:
            logger.error(f"Error retrieving voice samples: {e}")
            return jsonify({"message": "Failed to retrieve voice samples."}), 500
    
    def generate_tts(self):
        try:
            data = request.get_json()
            tts_request = TTSRequest(**data)
            response_data = self.service.generate_tts(tts_request)
            response = TTSResponse(
                message="TTS generated successfully.",
                audio_path=response_data['audio_path'],
                filename=response_data['filename'],
                voice_used=response_data.get('voice_used')
            )
            return jsonify(response.dict()), 200
        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
            return jsonify({"message": str(ve)}), 400
        except Exception as e:
            logger.error(f"Error generating TTS: {e}")
            return jsonify({"message": "Failed to generate TTS."}), 500
    
    def generate_tts_clone_voice(self):
        try:
            text = request.form.get("text")
            audio_file = request.files.get("audio")
            if not text or not audio_file:
                return jsonify({"message": "Missing text or audio file"}), 400

            import base64
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

            tts_voice_clone_request = TTSVoiceCloneRequest(text=text, audio_base64=audio_base64)
            response_data = self.service.generate_tts_voice_clone(tts_voice_clone_request)
            response = TTSResponse(
                message="TTS voice clone generated successfully.",
                audio_path=response_data['audio_path'],
                filename=response_data['filename'],
                voice_used=response_data.get('voice_used')
            )
            return jsonify(response.dict()), 200
        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
            return jsonify({"message": str(ve)}), 400
        except Exception as e:
            logger.error(f"Error generating TTS voice clone: {e}")
            return jsonify({"message": "Failed to generate TTS voice clone."}), 500

voice_controller_instance = VoiceController()
voice_bp = voice_controller_instance.voice_bp