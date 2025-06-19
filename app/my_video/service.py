from datetime import datetime
import uuid
from app.my_video.repo import get_videos_by_owner, insert_video, delete_video
from app.file.service import FileService

class VideosService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.file_service = FileService()

    def get_videos(self, owner_id: str):
        """
        Retrieve all videos created by a specific owner.
        
        Args:
            owner_id: ID of the user who owns the videos.
        
        Returns:
            List of video documents.
        """
        return get_videos_by_owner(owner_id)
    
    def delete_video(self, id: str):
        """
        Delete a video by its ID.
        
        Args:
            video_id: ID of the video to be deleted.
        
        Returns:
            Boolean indicating success or failure of the deletion.
        """
        # Implement deletion logic here
        # For example, remove the video from the database and delete the file from storage
        return delete_video(id)

    def upload_video(self, file, owner_id: str, title: str, thumbnail=None):
        """
        Upload video file to Cloudinary and save info to DB.
        """
        video_uuid = uuid.uuid4()
        video_url = self.file_service.uploadVideo(file.stream, str(video_uuid))

        if thumbnail:
            thumbnail_uuid = uuid.uuid4()
            thumbnail_url = self.file_service.uploadImages(thumbnail.stream, str(thumbnail_uuid))

        insert_video(
            video_id=str(video_uuid),
            owner_id=owner_id,
            video_path=video_url,
            created_at=datetime.utcnow(),
            status="completed",
            title=title,
            thumbnail=thumbnail_url if thumbnail else None
        )

        return {
            "video_id": str(video_uuid),
            "owner_id": owner_id,
            "video_path": video_url,
            "title": title,
            "thumbnail": thumbnail_url if thumbnail else None,
            "created_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }