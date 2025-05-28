from flask import Blueprint, jsonify, request
from app.video.service import VideoService
from app.video.dto import VideoGenerateDTO

class VideoController:
    def __init__(self):
        self.service = VideoService()
        self.video_bp = Blueprint('video_bp', __name__)

        self._register_routes()

    def _register_routes(self):
        self.video_bp.add_url_rule('/', view_func=self.gen_image, methods=['POST'])

    def gen_image(self):
        """image route handler."""
        try:
            data = request.json
            dto = VideoGenerateDTO(**data)

            script = self.service.generate_video(dto)
            return jsonify({"data": script}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
        
image_controller = VideoController()
video_bp = image_controller.video_bp