from datetime import datetime
import uuid
from app.my_video.repo import get_videos_by_owner, insert_video, delete_video, update_video
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

    def update_video(self, id: str, title: str = None, thumbnail_file=None):
        """
        Update video title and/or thumbnail.
        
        Args:
            id: ID of the video to be updated.
            title: New title for the video (optional).
            thumbnail_file: New thumbnail file to upload (optional).
        
        Returns:
            Updated video information.
        """
        thumbnail_url = None
        
        # Upload new thumbnail if provided
        if thumbnail_file:
            thumbnail_uuid = uuid.uuid4()
            thumbnail_url = self.file_service.uploadImages(thumbnail_file.stream, str(thumbnail_uuid))
        
        # Update video in database
        updated_video = update_video(id, title, thumbnail_url)
        
        return {
            "video_id": str(updated_video["_id"]),
            "owner_id": updated_video["owner_id"],
            "video_path": updated_video["video_path"],
            "title": updated_video["title"],
            "thumbnail": updated_video["thumbnail"],
            "created_at": updated_video["created_at"].isoformat() if hasattr(updated_video["created_at"], 'isoformat') else updated_video["created_at"],
            "status": updated_video["status"]
        }