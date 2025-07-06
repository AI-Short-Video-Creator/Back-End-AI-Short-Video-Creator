from flask import Blueprint, jsonify, request
from app.file.service import FileService
from datetime import datetime
import uuid
from app.my_video.repo import insert_video
from app.file.dto import UploadImageDTO, UploadVideoDTO
from flask_jwt_extended import jwt_required, get_jwt_identity

class FileController:
    def __init__(self):
        self.service = FileService()
        self.file_bp = Blueprint('file_bp', __name__)

        self._register_routes()

    def _register_routes(self):
        self.file_bp.add_url_rule('/images', view_func=self.upload_images, methods=['POST'])
        self.file_bp.add_url_rule('/video', view_func=self.upload_video, methods=['POST'])
        self.file_bp.add_url_rule('/upload-image-from-url', view_func=self.upload_image_from_url, methods=['POST'])


    def upload_images(self):
        """Script route handler."""
        try:
            data = request.json
            dto = UploadImageDTO(**data)

            script = self.service.uploadImages(dto)
            return jsonify({"data": script}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    @jwt_required()
    def upload_video(self):
        """Upload video file and return its Cloudinary URL."""
        # Expect multipart/form-data with 'video' file
        if 'video' not in request.files:
            return jsonify({"error": "Missing video file"}), 400
        file = request.files['video']
        video_bytes = file.read()
        # Generate unique ID for video
        video_id = uuid.uuid4().hex
        try:
            url = self.service.uploadVideo(video_bytes, video_id)
            # Insert video metadata into MongoDB
            insert_video(video_id or '', url, get_jwt_identity() , datetime.utcnow(), 'completed')
            return jsonify({"video_url": url}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    def upload_image_from_url(self):
        """
        Nhận JSON: { "image_url": "https://..." }
        Tải ảnh về, upload lên Cloudinary, trả về link Cloudinary.
        """
        data = request.get_json()
        image_url = data.get("image_url")
        image_id = data.get("image_id", None)  # optional

        if not image_url:
            return jsonify({"error": "Missing image_url"}), 400

        try:
            cloudinary_url = self.service.upload_image_from_url(image_url, image_id)
            return jsonify({"cloudinary_url": cloudinary_url}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
file_controller = FileController()
file_bp = file_controller.file_bp