from flask import Blueprint, request, jsonify
import logging
from pydantic import ValidationError
from app.voice.service import VoiceService
from app.voice.dto import VoiceListResponse, GCTTSRequest, TTSResponse, VoiceCloneRequest, VoiceCloneResponse, ElevenlabsTTSRequest
from flask_jwt_extended import jwt_required, get_jwt_identity

logger = logging.getLogger(__name__)

class VoiceController:
    def __init__(self):
        self.service = VoiceService()
        self.voice_bp = Blueprint('voice_bp', __name__)
        self._register_routes()

    def _register_routes(self):
        self.voice_bp.add_url_rule('', view_func=self.get_voices, methods=['GET'])
        self.voice_bp.add_url_rule('/synthesis', view_func=self.generate_speech, methods=['POST'])
        self.voice_bp.add_url_rule('/clones', view_func=self.create_cloned_voice, methods=['POST'])
        self.voice_bp.add_url_rule('/clones/<string:voice_id>', view_func=self.delete_cloned_voice, methods=['DELETE'])

    @jwt_required()
    def get_voices(self):
        try:
            language_code = request.args.get('language_code', 'en-US')
            voices = self.service.get_gctts_voice_lists(language_code=language_code)
            response = VoiceListResponse(
                total_count=len(voices),
                message="Successfully retrieved voice lists.",
                voices=voices
            )
            return jsonify(response.model_dump()), 200
        except Exception as e:
            logger.error(f"Error retrieving voice lists: {e}")
            return jsonify({"message": "Failed to retrieve voice lists."}), 500

    @jwt_required()
    def generate_speech(self):
        try:
            data = request.get_json()
            if data['provider'] == 'gctts':
                dto = GCTTSRequest(**data)
                response_data = self.service.gctts_generate_tts(dto)
            elif data['provider'] == 'elevenlabs':
                dto = ElevenlabsTTSRequest(**data)
                response_data = self.service.elevenlabs_generate_tts(dto)
            else:
                return jsonify({"message": "Unsupported provider"}), 400
            response = TTSResponse(
                message="Speech generated successfully.",
                audio_url=response_data['audio_url'],
                filename=response_data['filename'],
                voice_used=response_data.get('voice_used')
            )
            return jsonify(response.model_dump()), 201
        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
            return jsonify({"message": str(ve)}), 400
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return jsonify({"message": "Failed to generate speech."}), 500

    @jwt_required()
    def create_cloned_voice(self):
        try:            
            audio_file = request.files.get("audio_file")
            if not audio_file:
                return jsonify({"message": "Missing audio file"}), 400
            
            voice_name = request.form.get("voice_name")
            previrew_script = request.form.get("preview_script", "This is a preview of the cloned voice.")
            dto = VoiceCloneRequest(
                voice_name=voice_name,
                preview_script=previrew_script
            )
            response_data = self.service.clone_voice(dto, audio_file)
            response = VoiceCloneResponse(
                message="Voice cloned successfully.",
                voice_id=response_data["voice_id"],
                preview_url=response_data["preview_url"],
            )
            return jsonify(response.model_dump()), 201
        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
            return jsonify({"message": str(ve)}), 400
        except Exception as e:
            logger.error(f"Error cloning voice: {e}")
            return jsonify({"message": "Failed to clone voice."}), 500

    @jwt_required()
    def delete_cloned_voice(self, voice_id):
        try:
            self.service.delete_cloned_voice(voice_id)
            return jsonify({"message": "Cloned voice deleted successfully."}), 200
        except Exception as e:
            logger.error(f"Error deleting cloned voice: {e}")
            return jsonify({"message": "Failed to delete cloned voice."}), 500

voice_controller_instance = VoiceController()
voice_bp = voice_controller_instance.voice_bp