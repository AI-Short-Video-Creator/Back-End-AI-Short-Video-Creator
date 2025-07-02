import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import requests
import tempfile
import json

# Tạo credentials từ file client_secrets.json hoặc từ biến môi trường
def get_authenticated_service():
    # Đọc credentials từ file JSON
    CREDENTIALS_FILE = os.getenv("YOUTUBE_CREDENTIALS_FILE", "authorized_user.json")
    if not os.path.exists(CREDENTIALS_FILE):
        raise Exception(f"Credentials file '{CREDENTIALS_FILE}' not found")
    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        creds_dict = json.load(f)
    creds = Credentials.from_authorized_user_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/youtube.upload"
    ])
    return build("youtube", "v3", credentials=creds)

def download_file(url, suffix=''):
    response = requests.get(url)
    response.raise_for_status()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(response.content)
    temp_file.close()
    return temp_file.name

def upload_video_youtube(video_url, title, description, thumbnail_url=None):
    youtube = get_authenticated_service()
    
    # Tải video tạm
    video_path = download_file(video_url, suffix=".mp4")
    
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["quickclip", "auto-upload"],
            "categoryId": "22"  # default: People & Blogs
        },
        "status": {
            "privacyStatus": "public"  # or 'private' or 'unlisted'
        }
    }

    media = MediaFileUpload(video_path, resumable=True, mimetype='video/*')
    response_upload = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    ).execute()

    video_id = response_upload.get("id")

    # Gắn thumbnail nếu có
    if thumbnail_url:
        thumbnail_path = download_file(thumbnail_url, suffix=".jpg")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()

    # Trả kết quả
    return {
        "videoId": video_id,
        "videoUrl": f"https://www.youtube.com/watch?v={video_id}",
        "title": title,
        "description": description,
        "thumbnail": thumbnail_url
    }
