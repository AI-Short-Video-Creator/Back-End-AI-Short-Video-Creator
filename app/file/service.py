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
    
    def uploadVideo(self, dto: UploadVideoDTO) -> str:
        video_url = ""
        if not dto.path:
            raise ValueError("No videos provided for upload.")
        try:
            response = cloudinary.uploader.upload(dto.images.file_path, folder="short_video_creator/videos", public_id=dto.images.file_id, resource_type="video")
            video_url = response['secure_url']
            print(f"Uploaded video {dto.images.file_id} to Cloudinary: {response['secure_url']}")
        except Exception as e:
            raise ValueError(f"Failed to upload video {dto.images.file_id}: {str(e)}")
        
        return json.dumps({"video_urls": video_url})