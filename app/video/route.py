from flask import Blueprint, jsonify, request
from app.video.service import VideoService
from app.video.dto import VideoGenerateDTO
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import uuid
from app.extentions import mongo
from datetime import datetime
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoController:
    def __init__(self):
        self.service = VideoService()
        self.video_bp = Blueprint('video_bp', __name__, url_prefix='/api/video')
        self._register_routes()

    def _register_routes(self):
        self.video_bp.add_url_rule('/', view_func=self.gen_video, methods=['POST'])

    @jwt_required()
    def gen_video(self):
        """Generate a video from image URLs and voices."""
        try:
            data = request.json
            if not data or 'image_urls' not in data or 'voices' not in data:
                logger.error("Missing image_urls or voices in request body")
                return jsonify({"error": "image_urls and voices are required"}), 400
            
            user_id = get_jwt_identity()
            logger.info(f"Processing video generation for user_id: {user_id}")
            
            dto = VideoGenerateDTO(**data)
            video_path = self.service.generate_video(dto)
            
            # Store video metadata in MongoDB
            video_id = str(uuid.uuid4())
            mongo.db.videos.insert_one({
                "video_id": video_id,
                "video_path": video_path,
                "owner_id": user_id,
                "created_at": datetime.utcnow(),
                "status": "completed"
            })
            
            # Update images with video_id
            images_collection = mongo.db.images
            for image_url in data["image_urls"]:
                images_collection.update_one(
                    {"url": image_url, "owner_id": user_id},
                    {"$set": {"video_id": video_id}}
                )
            
            return jsonify({"video_id": video_id, "video_path": video_path}), 200
        except ValueError as e:
            logger.error(f"ValueError in gen_video: {str(e)}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Unexpected error in gen_video: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

video_controller = VideoController()
video_bp = video_controller.video_bp