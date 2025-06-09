from flask import Blueprint, jsonify, request
from app.file.service import FileService
from app.file.dto import UploadImageDTO, UploadVideoDTO
class FileController:
    def __init__(self):
        self.service = FileService()
        self.file_bp = Blueprint('file_bp', __name__)

        self._register_routes()

    def _register_routes(self):
        self.file_bp.add_url_rule('/images', view_func=self.script, methods=['POST'])
        self.file_bp.add_url_rule('/video', view_func=self.script, methods=['POST'])


    def upload_images(self):
        """Script route handler."""
        try:
            data = request.json
            dto = UploadImageDTO(**data)

            script = self.service.uploadImages(dto)
            return jsonify({"data": script}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    def upload_video(self):
        """Script route handler."""
        try:
            data = request.json
            dto = UploadVideoDTO(**data)

            script = self.service.uploadVideo(dto)
            return jsonify({"data": script}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
file_controller = FileController()
file_bp = file_controller.file_bp