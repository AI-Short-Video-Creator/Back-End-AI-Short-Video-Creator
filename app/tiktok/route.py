from flask import Blueprint, request, jsonify
from flask_cors import CORS
from .service import exchange_code_for_access_token, get_tiktok_user_info
import tempfile
import requests
import os
import traceback
import math, json
from datetime import datetime
from collections import defaultdict

tiktok_bp = Blueprint("tiktok", __name__)

CORS(tiktok_bp, supports_credentials=True)

@tiktok_bp.route("exchange_token", methods=["POST"])
def exchange_token():
    data = request.get_json()
    code = data.get("code")
    redirect_uri = data.get("redirect_uri")
    if not code or not redirect_uri:
        return jsonify({"error": "Missing code or redirect_uri"}), 400
    try:
        token_data = exchange_code_for_access_token(code, redirect_uri)
        access_token = token_data.get("access_token")
        if not access_token:
            return jsonify({"error": "No access_token in TikTok response", "detail": token_data}), 400
        user_info = get_tiktok_user_info(access_token)
        user = user_info.get("data", {}).get("user", {})
        return jsonify({
            "access_token": access_token,
            "name": user.get("display_name", ""),
            "avatar": user.get("avatar_url", "")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tiktok_bp.route("/upload_video_by_url", methods=["POST"])
def upload_video_by_url():
    data = request.get_json()
    video_url = data.get("video_url")
    title = data.get("title")
    description = data.get("description", "")
    access_token = data.get("access_token")

    if not video_url or not title or not access_token:
        return jsonify({"error": "Missing video_url, title, or access_token"}), 400

    try:
        # 1. Tải video về file tạm
        video_res = requests.get(video_url, stream=True, timeout=20)
        content_type = video_res.headers.get("Content-Type", "")
        if video_res.status_code != 200 or "video" not in content_type:
            return jsonify({"error": "Invalid video URL or unsupported content type"}), 400

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        for chunk in video_res.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        temp_file.close()
        file_path = temp_file.name
        file_size = os.path.getsize(file_path)

        # 2. Gửi yêu cầu init upload TikTok
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        
        # Chỉ upload 1 chunk duy nhất (toàn bộ file)
        chunk_size = file_size
        total_chunks = 1

        payload = {
            "post_info": {
                "title": title,
                "privacy_level": "SELF_ONLY",  # Chỉ cho phép private khi app chưa duyệt
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunks
            }
        }

        init_res = requests.post(init_url, headers=headers, json=payload, timeout=30)
        init_data = init_res.json()
        
        print("TikTok INIT response:", init_res.status_code)
        print("TikTok INIT payload:", json.dumps(payload, indent=2))
        print("TikTok INIT raw response:", init_res.text)

        if init_res.status_code != 200 or "data" not in init_data:
            os.unlink(file_path)
            return jsonify({"error": "TikTok init failed", "detail": init_data}), 400

        upload_url = init_data["data"]["upload_url"]
        publish_id = init_data["data"]["publish_id"]

        # 3. Upload video file bằng PUT
        with open(file_path, "rb") as f:
            video_data = f.read()

        content_range = f"bytes 0-{file_size - 1}/{file_size}"
        upload_headers = {
            "Content-Type": "video/mp4",
            "Content-Range": content_range
        }
        upload_res = requests.put(upload_url, headers=upload_headers, data=video_data, timeout=60)
        os.unlink(file_path)

        if upload_res.status_code not in (200, 201):
            return jsonify({
                "error": "Failed to upload video",
                "upload_response": upload_res.text
            }), 400

        return jsonify({
            "status": "upload_success",
            "publish_id": publish_id
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "Internal server error",
            "detail": str(e)
        }), 500

@tiktok_bp.route("/total_views", methods=["GET"])
def get_total_views():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    access_token = auth_header.replace("Bearer ", "")

    try:
        # Thêm query param đúng cách
        fields = "cover_image_url,id,title,view_count"
        videos_url = f"https://open.tiktokapis.com/v2/video/list/?fields={fields}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        total_views = 0
        has_more = True
        cursor = None

        while has_more:
            payload = {
                "max_count": 20  # Max là 20 theo tài liệu
            }
            if cursor:
                payload["cursor"] = cursor

            print("Sending payload:", payload)
            res = requests.post(videos_url, headers=headers, json=payload)

            if not res.ok:
                print("TikTok error:", res.status_code, res.text)
                return jsonify({"error": "TikTok API error", "detail": res.text}), 500

            data = res.json()
            print("Response:", data)

            if "data" not in data or "videos" not in data["data"]:
                break

            for video in data["data"]["videos"]:
                total_views += int(video.get("view_count", 0))

            has_more = data["data"].get("has_more", False)
            cursor = data["data"].get("cursor", None)

        return jsonify({"totalViews": total_views})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500

def parse_month(dt: str):
    d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    return d.strftime("%B %Y")  # Ví dụ: "June 2024"

@tiktok_bp.route("/monthly_views", methods=["GET"])
def tiktok_monthly_views():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    access_token = auth_header.replace("Bearer ", "")

    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end:
        return jsonify({"error": "Missing start or end"}), 400

    try:
        # Lấy danh sách video
        fields = "id,create_time,cover_image_url,title,like_count,comment_count,share_count,view_count"
        videos_url = f"https://open.tiktokapis.com/v2/video/list/?fields={fields}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        has_more = True
        cursor = None
        videos = []

        while has_more:
            payload = {"max_count": 20}
            if cursor:
                payload["cursor"] = cursor
            res = requests.post(videos_url, headers=headers, json=payload)
            data = res.json()
            if "data" not in data or "videos" not in data["data"]:
                break
            videos.extend(data["data"]["videos"])
            has_more = data["data"].get("has_more", False)
            cursor = data["data"].get("cursor", None)

        # Khởi tạo các tháng trong khoảng thời gian
        result = {}
        start_dt = datetime.fromisoformat(start).date()
        print(start_dt)
        end_dt = datetime.fromisoformat(end).date()
        current = datetime(start_dt.year, start_dt.month, 1).date()
        while current <= end_dt:
            month_str = current.strftime("%B %Y")
            result[month_str] = {"month": month_str, "views": 0, "likes": 0, "comments": 0, "shares": 0}
            # Tăng sang tháng tiếp theo
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1).date()
            else:
                current = datetime(current.year, current.month + 1, 1).date()

        # Cộng dồn số liệu video vào tháng tương ứng
        for video in videos:
            created = datetime.fromtimestamp(int(video["create_time"])).date()
            if not (start_dt <= created <= end_dt):
                continue
            month = created.strftime("%B %Y")
            if month not in result:
                result[month] = {"month": month, "views": 0, "likes": 0, "comments": 0, "shares": 0}
            result[month]["views"] += int(video.get("view_count", 0))
            result[month]["likes"] += int(video.get("like_count", 0))
            result[month]["comments"] += int(video.get("comment_count", 0))
            result[month]["shares"] += int(video.get("share_count", 0))

        # Trả về mảng đã sắp xếp theo tháng, chỉ lấy 3 tháng cuối
        sorted_result = sorted(result.values(), key=lambda x: datetime.strptime(x["month"], "%B %Y"))
        return jsonify(sorted_result[-3:])

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500

@tiktok_bp.route("/video_detail_stats", methods=["GET"])
def tiktok_video_detail_stats():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    access_token = auth_header.replace("Bearer ", "")

    start = request.args.get("start")
    end = request.args.get("end")

    try:
        # Lấy danh sách video
        fields = "id,create_time,cover_image_url,title,like_count,comment_count,share_count,view_count"
        videos_url = f"https://open.tiktokapis.com/v2/video/list/?fields={fields}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        has_more = True
        cursor = None
        videos = []

        while has_more:
            payload = {"max_count": 20}
            if cursor:
                payload["cursor"] = cursor
            res = requests.post(videos_url, headers=headers, json=payload)
            data = res.json()
            if "data" not in data or "videos" not in data["data"]:
                break
            videos.extend(data["data"]["videos"])
            has_more = data["data"].get("has_more", False)
            cursor = data["data"].get("cursor", None)

        # Lọc video theo khoảng thời gian nếu có
        if start:
            start_dt = datetime.fromisoformat(start).date()
        else:
            start_dt = None
        if end:
            end_dt = datetime.fromisoformat(end).date()
        else:
            end_dt = None

        result = []
        for video in videos:
            created = datetime.fromtimestamp(int(video["create_time"])).date()
            if start_dt and created < start_dt:
                continue
            if end_dt and created > end_dt:
                continue
            result.append({
                "id": video.get("id"),
                "title": video.get("title", "Untitled"),
                "thumbnail": video.get("cover_image_url", ""),
                "views": int(video.get("view_count", 0)),
                "likes": int(video.get("like_count", 0)),
                "comments": int(video.get("comment_count", 0)),
                "shares": int(video.get("share_count", 0)),
            })

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500