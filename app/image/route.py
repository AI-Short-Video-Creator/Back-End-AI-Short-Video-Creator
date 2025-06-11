from flask import Blueprint, jsonify, request
from app.image.service import ImageService
from app.image.dto import ImageGenerateDTO
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageController:
    def __init__(self):
        self.service = ImageService()
        self.image_bp = Blueprint('image_bp', __name__, url_prefix='/api/image')
        self._register_routes()

    def _register_routes(self):
        self.image_bp.add_url_rule('/', view_func=self.gen_image, methods=['POST'])
        self.image_bp.add_url_rule('/regenerate', view_func=self.regenerate_image, methods=['POST'])

    @jwt_required()
    def gen_image(self):
        """Generate images from script."""
        try:
            data = request.json
            if not data or 'script' not in data:
                logger.error("Missing script in request body")
                return jsonify({"error": "Script is required"}), 400
            
            user_id = get_jwt_identity()
            logger.info(f"Processing image generation for user_id: {user_id}")
            data['owner_id'] = user_id
            if 'themes' not in data:
                logger.info("No themes provided, using default 'cartoon'")
                data['themes'] = "cartoon"
            dto = ImageGenerateDTO(**data)
            result = self.service.generate_image(dto)
            return jsonify(result), 200
        except ValueError as e:
            logger.error(f"ValueError in gen_image: {str(e)}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Unexpected error in gen_image: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    @jwt_required()
    def regenerate_image(self):
        """Regenerate a specific image."""
        try:
            data = request.json
            image_id = data.get('image_id')
            session_id = data.get('session_id')
            if not image_id or not session_id:
                logger.error("Missing image_id or session_id in request")
                return jsonify({"error": "image_id and session_id required"}), 400
            
            logger.info(f"Regenerating image {image_id} for session {session_id}")
            result = self.service.regenerate_image(image_id, session_id)
            return jsonify(result), 200
        except ValueError as e:
            logger.error(f"ValueError in regenerate_image: {str(e)}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Unexpected error in regenerate_image: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

image_controller = ImageController()
image_bp = image_controller.image_bp