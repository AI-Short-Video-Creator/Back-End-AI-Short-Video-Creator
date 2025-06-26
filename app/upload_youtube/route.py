from flask import Blueprint, request, jsonify
from .service import upload_video_youtube

youtube_bp = Blueprint('youtube', __name__)

@youtube_bp.route('/upload', methods=['POST'])
def upload_youtube_video():
    try:
        data = request.get_json()
        video_url = data.get("videoUrl")
        title = data.get("title")
        description = data.get("description")
        thumbnail_url = data.get("thumbnailUrl")

        if not all([video_url, title, description]):
            return jsonify({"error": {"message": "Missing required fields"}}), 400

        result = upload_video_youtube(video_url, title, description, thumbnail_url)
        return jsonify(result)

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # In ra toàn bộ stacktrace
        return jsonify({"error": {"message": str(e)}}), 500
