from flask import Blueprint, request, jsonify, current_app
import logging
from pydantic import ValidationError

from app.voice_bp.service import VoiceService
from app.voice_bp.dto import GoogleTTSRequest, TTSResponse

logger = logging.getLogger(__name__)

class VoiceController:
    def __init__(self):
        self.service = VoiceService()
        self.voice_bp = Blueprint('voice_bp', __name__)
        self._register_routes()

    def _register_routes(self):
        self.voice_bp.add_url_rule('/samples', view_func=self.get_voice_samples, methods=['GET'])
        self.voice_bp.add_url_rule('/google-tts', view_func=self.generate_google_tts, methods=['POST'])
        
    def get_voice_samples(self):
        """
        API endpoint to retrieve a list of available voice samples.
        Supports filtering via query parameters:
        - lang (e.g., "en-US", "vi-VN")
        - gender (e.g., "FEMALE", "MALE")
        - type (e.g., "Standard", "WaveNet")
        """
        try:
            lang_code = request.args.get('lang')
            gender = request.args.get('gender')
            voice_type = request.args.get('type')

            current_app.logger.info(
                f"Fetching voice samples with filters - lang: {lang_code}, gender: {gender}, type: {voice_type}"
            )

            samples_data = self.service.get_samples_by_criteria(
                language_code=lang_code,
                gender=gender,
                voice_type=voice_type
            )

            if not samples_data:
                current_app.logger.warning(
                    "No voice samples found matching criteria or metadata could not be loaded."
                )
                if lang_code or gender or voice_type:
                    return jsonify({"message": "No voice samples found matching your criteria.", "data": []}), 200
                else:
                    return jsonify({"message": "No voice samples currently available.", "data": []}), 200
            
            response_data = []
            for sample in samples_data:
                response_data.append({
                    "voiceName": sample.get("voiceName"),
                    "languageCode": sample.get("languageCode"),
                    "gender": sample.get("ssmlGender"),
                    "type": sample.get("voiceTypeApproximation"),
                    "sampleUrl": sample.get("cloudinaryUrl")
                })

            return jsonify({
                "message": "Voice samples retrieved successfully.",
                "count": len(response_data),
                "data": response_data
            }), 200

        except Exception as e:
            current_app.logger.error(f"Error in get_voice_samples: {e}", exc_info=True)
            return jsonify({"error": "An unexpected error occurred while fetching voice samples."}), 500

    def generate_google_tts(self):
        """Handles Google TTS audio generation requests using Pydantic DTOs."""
        try:
            json_data = request.get_json()
            if not json_data:
                return jsonify({"error": "Request body must be JSON and not empty."}), 400
            
            tts_request_data = GoogleTTSRequest.model_validate(json_data)
            
        except ValidationError as err:
            logger.warning(f"Pydantic validation error for Google TTS request: {err.errors()}")
            return jsonify({"error": "Validation failed", "details": err.errors()}), 400
        except Exception as e:
            logger.error(f"Error parsing JSON or unexpected error before Pydantic validation: {e}", exc_info=True)
            return jsonify({"error": "Invalid request format or unexpected error."}), 400

        try:
            result_data = self.service.generate_google_tts_audio(tts_request_data.model_dump())

            validated_response_data = TTSResponse.model_validate(result_data)
            return jsonify(validated_response_data.model_dump()), 200

        except ConnectionError as conn_err:
            logger.error(f"TTS Service Connection Error: {conn_err}")
            return jsonify({"error": str(conn_err)}), 503
        except Exception as e:
            logger.error(f"Failed to generate Google TTS audio: {e}", exc_info=True)
            return jsonify({"error": "An unexpected error occurred while generating audio."}), 500

voice_controller_instance = VoiceController()
voice_bp = voice_controller_instance.voice_bp