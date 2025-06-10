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

from app.extentions import mongo
from datetime import datetime
from typing import Optional

images_collection = mongo.db.images

def insert_image(
    file_id: str,
    url: str,
    script: str,
    owner_id: Optional[str] = None,
    video_id: Optional[str] = None,
    session_id: Optional[str] = None,
    status: str = "pending",
    metadata: Optional[dict] = None
) -> str:
    """
    Insert a new image document into the images collection.
    Returns the inserted_id as a string.
    """
    doc = {
        "file_id": file_id,
        "file_path": None,  # No local storage
        "url": url,
        "owner_id": owner_id,
        "video_id": video_id,
        "status": status,  # Added status field
        "created_at": datetime.utcnow(),
        "metadata": metadata or {}
    }
    doc["metadata"]["session_id"] = session_id  # Store session_id in metadata
    doc["metadata"]["script"] = script  # Store script (sentence) in metadata
    try:
        result = images_collection.insert_one(doc)
        return str(result.inserted_id)
    except Exception as e:
        raise ValueError(f"Failed to insert image: {str(e)}")