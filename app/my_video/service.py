from datetime import datetime
import uuid
from app.my_video.repo import get_videos_by_owner, insert_video
import cloudinary.uploader

class VideosService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def get_videos(self, owner_id: str):
        """
        Retrieve all videos created by a specific owner.
        
        Args:
            owner_id: ID of the user who owns the videos.
        
        Returns:
            List of video documents.
        """
        return get_videos_by_owner(owner_id)

    def upload_video(self, file, owner_id: str, title: str, thumbnail=None):
        """
        Upload video file to Cloudinary and save info to DB.
        """
        print(f"Title and owner_id received: {title}, {owner_id}")
        video_uuid = uuid.uuid4()
        upload_result = cloudinary.uploader.upload_large(
            file.stream,
            resource_type="video",
            public_id=f"videos/video_{video_uuid}",
            folder="user_videos"
        )
    
        insert_video(
            video_id=str(video_uuid),
            owner_id=owner_id,
            video_path=upload_result['secure_url'],
            created_at=datetime.utcnow(),
            status="completed"
        )
        
        return {
            "video_id": str(video_uuid),
            "owner_id": owner_id,
            "video_path": upload_result['secure_url'],
            "created_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }