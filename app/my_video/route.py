from flask import Blueprint, jsonify, request
from app.my_video.service import VideosService
from flask_jwt_extended import jwt_required, get_jwt_identity

class VideoController:
    def __init__(self):
        self.service = VideosService()
        self.video_bp = Blueprint('videos_bp', __name__)

        self._register_routes()

    def _register_routes(self):
        """
        Register the routes for the video controller.
        """
        self.video_bp.add_url_rule('/', view_func=self.get_videos, methods=['GET'])
        self.video_bp.add_url_rule('/upload', view_func=self.upload_video, methods=['POST'])
        self.video_bp.add_url_rule('/<string:id>', view_func=self.delete_video, methods=['DELETE'])

    @jwt_required()
    def get_videos(self):
        """
        Retrieve all videos created by the authenticated user.
        
        Returns:
            JSON response containing the list of videos.
        """
        owner_id = get_jwt_identity()
        print(f"Fetching videos for owner_id: {owner_id}")
        try:
            videos = self.service.get_videos(owner_id)
            return jsonify(videos), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @jwt_required()
    def upload_video(self):
        """
        Handle video file upload.
        """
        owner_id = get_jwt_identity()
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        title = request.form.get('title')
        if not title:
            return jsonify({"error": "No title provided"}), 400
        thumbnail = request.files.get('thumbnail')
        try:
            video_info = self.service.upload_video(file, owner_id, title, thumbnail)
            return jsonify(video_info), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @jwt_required()
    def delete_video(self, id: str):
        """
        Delete a video by its ID.
        
        Args:
            video_id (str): The ID of the video to delete.
        
        Returns:
            JSON response indicating success or failure.
        """
        try:
            result = self.service.delete_video(id)
            if result:
                return jsonify({"message": "Video deleted successfully"}), 200
            else:
                return jsonify({"error": "Video not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

videos_controller = VideoController()
videos_bp = videos_controller.video_bp