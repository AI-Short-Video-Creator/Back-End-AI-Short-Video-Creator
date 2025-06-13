import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api
import json
from app.file.dto import UploadImageDTO, UploadVideoDTO
class FileService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        config = cloudinary.config(secure=True)

    
    def uploadImages(self, image_bytes, image_id ) -> str:
        try:
            upload_result = cloudinary.uploader.upload(
                        image_bytes,
                        public_id=f"images/{image_id}",
                        resource_type="image",
                        folder="video_creator"
                    )
            image_url = upload_result['secure_url']
            print(f"Uploaded image {image_id} to Cloudinary: {image_url}")
            return image_url
        except Exception as e:
            raise ValueError(f"Failed to upload image {image_id}: {str(e)}")
    
    def uploadVideo(self, video_bytes, video_id) -> str:
        try:
            upload_result = cloudinary.uploader.upload(
                video_bytes,
                public_id=f"videos/{video_id}",
                resource_type="video",
                folder="video_creator"
            )
            video_url = upload_result['secure_url']
            print(f"Uploaded video {video_id} to Cloudinary: {video_url}")
            return video_url
        except Exception as e:
            raise ValueError(f"Failed to upload video {video_id}: {str(e)}")