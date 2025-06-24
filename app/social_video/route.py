from flask import Blueprint, request, jsonify
from .service import save_or_update_social_video, get_all_social_videos

social_video_bp = Blueprint("social_video", __name__)

@social_video_bp.route("/share", methods=["POST"])
def share_video():
    data = request.json
    video_id = data.get("id")
    platform = data.get("platform")  # "facebook", "youtube", "tiktok"
    link = data.get("link")
    if not video_id or not platform or not link:
        return jsonify({"error": "Missing params"}), 400
    video = save_or_update_social_video(video_id, platform, link)
    return jsonify(video.dict())

@social_video_bp.route("/all", methods=["GET"])
def get_all():
    videos = get_all_social_videos()
    return jsonify([v.dict() for v in videos])