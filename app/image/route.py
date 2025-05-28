from flask import Blueprint, jsonify, request
from app.image.service import ImageService
from app.image.dto import ImageGenerateDTO

class ImageController:
    def __init__(self):
        self.service = ImageService()
        self.image_bp = Blueprint('image_bp', __name__)

        self._register_routes()

    def _register_routes(self):
        self.image_bp.add_url_rule('/', view_func=self.gen_image, methods=['POST'])

    def gen_image(self):
        """image route handler."""
        try:
            data = request.json
            dto = ImageGenerateDTO(**data)

            script = self.service.generate_image(dto)
            return jsonify({"data": script}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
        
image_controller = ImageController()
image_bp = image_controller.image_bp