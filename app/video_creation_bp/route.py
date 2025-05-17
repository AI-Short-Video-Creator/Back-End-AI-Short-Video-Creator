from flask import Blueprint, jsonify, current_app, request
from app.video_creation_bp.service import VideoCreationService
from app.video_creation_bp.dto import CreateVideoRequestDTO

class VideoCreationController:
    def __init__(self):
        self.service = VideoCreationService()
        self.video_creation_bp = Blueprint('video_creation_api', __name__)
        self._register_routes()

    def _register_routes(self):
        self.video_creation_bp.add_url_rule('/create', view_func=self.create_video, methods=['POST'])

    def create_video(self):
        try:
            data = request.get_json()

            if not data:
                return jsonify({"error": "Missing JSON body"}), 400

            dto = CreateVideoRequestDTO(
                audio_path=data.get("audio_path"),
                script_text=data.get("script_text"),
                background_path=data.get("background_path"),
                font_name=data.get("font_name", "Arial")
            )

            video_url = self.service.create_video_from_request(dto)

            if video_url:
                return jsonify({
                    "message": "Video created successfully and uploaded to Cloudinary.",
                    "video_url": video_url
                }), 201
            else:
                return jsonify({
                    "error": "Video creation failed",
                    "message": "Could not generate video."
                }), 500

        except FileNotFoundError as e:
            current_app.logger.error(f"File not found during video creation: {e}")
            return jsonify({"error": "Configuration error", "message": str(e)}), 500
        except Exception as e:
            current_app.logger.error(f"Error in create_video_local endpoint: {e}")
            return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

video_creation_controller = VideoCreationController()
video_creation_bp = video_creation_controller.video_creation_bp
