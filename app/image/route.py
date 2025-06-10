from flask import Blueprint, jsonify, request
from app.image.service import ImageService
from app.image.dto import ImageGenerateDTO
from flask_jwt_extended import jwt_required, get_jwt_identity

class ImageController:
    def __init__(self):
        self.service = ImageService()
        self.image_bp = Blueprint('image_bp', __name__)
        self._register_routes()

    def _register_routes(self):
        self.image_bp.add_url_rule('/', view_func=self.gen_image, methods=['POST'])
        self.image_bp.add_url_rule('/regenerate', view_func=self.regenerate_image, methods=['POST'])

    @jwt_required()
    def gen_image(self):
        """Generate images from script."""
        try:
            data = request.json
            data['owner_id'] = get_jwt_identity()  # Add owner_id to DTO
            dto = ImageGenerateDTO(**data)
            result = self.service.generate_image(dto)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    @jwt_required()
    def regenerate_image(self):
        """Regenerate a specific image."""
        try:
            data = request.json
            image_id = data.get('image_id')
            session_id = data.get('session_id')
            if not image_id or not session_id:
                return jsonify({"error": "image_id and session_id required"}), 400
            
            result = self.service.regenerate_image(image_id, session_id)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

image_controller = ImageController()
image_bp = image_controller.image_bp