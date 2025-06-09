from app.extentions import mongo

# Truy cập collection
from datetime import datetime
from typing import List, Optional
images_collection = mongo.db.images

# Schema đề xuất cho 3 collections:
# 1. images
# {
#   _id: ObjectId,
#   file_id: str,
#   file_path: str,
#   url: str,
#   owner_id: str,         # user _id
#   video_id: Optional[str], # video _id nếu ảnh thuộc video nào đó
#   created_at: datetime,
#   metadata: dict
# }
#
# 2. videos
# {
#   _id: ObjectId,
#   title: str,
#   description: str,
#   owner_id: str,         # user _id
#   image_ids: [str],      # danh sách image file_id
#   url: str,
#   created_at: datetime,
#   metadata: dict
# }
#
# 3. users
# {
#   _id: ObjectId,
#   username: str,
#   email: str,
#   password_hash: str,
#   created_at: datetime,
#   avatar_url: str,
#   metadata: dict
# }

def insert_image(
    file_id: str,
    url: str,
    script: str,
    owner_id: Optional[str] = None,
    video_id: Optional[str] = None,
    metadata: Optional[dict] = None
) -> str:
    """
    Insert a new image document into the images collection.
    Returns the inserted_id as a string.
    """
    doc = {
        "file_id": file_id,
        "url": url,
        "script": script,
        "owner_id": owner_id,
        "video_id": video_id,
        "created_at": datetime.utcnow(),
        "metadata": metadata or {}
    }
    try:
        result = images_collection.insert_one(doc)
    except Exception as e:
        raise ValueError(f"Failed to insert image: {str(e)}")
    return str(result.inserted_id)

# Example usage:
# image_id = insert_image(
#     file_id="abc123",
#     file_path="output/image1.png",
#     url="https://res.cloudinary.com/xxx/image/upload/v123/abc123.png",
#     owner_id="user123"
# )