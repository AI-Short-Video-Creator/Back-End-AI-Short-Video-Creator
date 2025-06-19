from datetime import datetime
from app.extentions import mongo
from bson import ObjectId

def get_videos_by_owner(owner_id: str):
    """
    Retrieve all videos created by a specific owner.
    
    Args:
        owner_id: ID of the user who owns the videos.
    
    Returns:
        List of video documents.
    """
    try:
        videos = mongo.db.videos.find({"owner_id": owner_id})
        return list(videos)
    except Exception as e:
        raise Exception(f"Failed to retrieve videos from MongoDB: {str(e)}")
    
def insert_video(video_id: str, video_path: str, owner_id: str, created_at: datetime, status: str, title: str = None, thumbnail: str = None):
    """
    Insert a video document into the MongoDB videos collection.
    
    Args:
        video_id: Unique identifier for the video.
        video_path: Path to the video file.
        owner_id: ID of the user who owns the video.
        created_at: Timestamp when the video was created.
        status: Status of the video (e.g., pending, completed).
        title: Title of the video (optional).
        thumbnail: URL of the thumbnail image (optional).
    """
    try:
        document = {
            "video_id": video_id,
            "video_path": video_path,
            "owner_id": owner_id,
            "created_at": created_at,
            "status": status,
            "title": title,
            "thumbnail": thumbnail
        }
        mongo.db.videos.insert_one(document)
    except Exception as e:
        raise Exception(f"Failed to insert video into MongoDB: {str(e)}")

def delete_video(id: str):
    """
    Delete a video document from the MongoDB videos collection.
    
    Args:
        video_id: Unique identifier for the video to be deleted.
    """
    try:
        result = mongo.db.videos.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise Exception(f"No video found with ID: {id}")
        return True
    except Exception as e:
        raise Exception(f"Failed to delete video from MongoDB: {str(e)}")
